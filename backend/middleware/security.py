"""
보안 미들웨어
Flask 애플리케이션의 보안 기능을 제공합니다.
"""

from flask import request, jsonify, g
from functools import wraps
import re
import time
import uuid
from collections import defaultdict, deque
import logging
import html
import bleach

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        self.rate_limit_storage = defaultdict(lambda: deque())
        self.blocked_ips = set()
        
        # 허용된 HTML 태그 (매우 제한적)
        self.allowed_tags = []
        self.allowed_attributes = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 미들웨어 초기화"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """요청 전 처리"""
        # IP 차단 확인
        if self._is_blocked_ip(request.remote_addr):
            return jsonify({"error": "Access denied"}), 403
        
        # Rate Limiting 확인
        if not self._check_rate_limit(request.remote_addr):
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # 요청 시작 시간 기록
        g.request_start_time = time.time()
    
    def after_request(self, response):
        """요청 후 처리"""
        # CORS 헤더 설정
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        # 보안 헤더 설정
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # 응답 시간 로깅
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            if duration > 5.0:  # 5초 초과 시 경고
                logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
        
        return response
    
    def _is_blocked_ip(self, ip):
        """IP 차단 확인"""
        return ip in self.blocked_ips
    
    def _check_rate_limit(self, ip):
        """Rate Limiting 확인"""
        now = time.time()
        window = 60  # 1분 윈도우
        max_requests = 50  # 분당 최대 50 요청
        
        # 오래된 요청 기록 제거
        user_requests = self.rate_limit_storage[ip]
        while user_requests and user_requests[0] < now - window:
            user_requests.popleft()
        
        # 현재 요청 추가
        user_requests.append(now)
        
        # 제한 확인
        if len(user_requests) > max_requests:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return False
        
        return True
    
    def validate_uuid(self, uuid_string):
        """UUID 형식 검증 (개발 편의를 위해 완화된 규칙 허용)
        - 표준 UUID (8-4-4-4-12) 또는
        - 간단한 플레이어 식별자: 영숫자/언더스코어/하이픈 3~32자
        """
        if not isinstance(uuid_string, str):
            return False
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        simple_pattern = re.compile(r'^[A-Za-z0-9_-]{3,32}$')
        return bool(uuid_pattern.match(uuid_string) or simple_pattern.match(uuid_string))
    
    def sanitize_input(self, text):
        """입력 데이터 정제"""
        if not isinstance(text, str):
            return str(text)
        
        # HTML 태그 제거
        cleaned = bleach.clean(text, tags=self.allowed_tags, attributes=self.allowed_attributes)
        
        # HTML 엔티티 인코딩
        cleaned = html.escape(cleaned)
        
        # 길이 제한 (1000자)
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000] + "..."
        
        return cleaned
    
    def validate_input(self, data):
        """입력 데이터 검증"""
        if not data:
            return False, "데이터가 비어있습니다"
        
        # UUID 검증
        if 'player_uuid' in data:
            if not self.validate_uuid(data['player_uuid']):
                return False, "잘못된 UUID 형식입니다"
        
        # 메시지 검증
        if 'message' in data:
            message = data['message']
            if not isinstance(message, str):
                return False, "메시지는 문자열이어야 합니다"
            if len(message.strip()) == 0:
                return False, "메시지가 비어있습니다"
            if len(message) > 1000:
                return False, "메시지가 너무 깁니다 (최대 1000자)"
            
            # 정제된 메시지로 교체
            data['message'] = self.sanitize_input(message)
        
        # SQL 인젝션 패턴 확인
        dangerous_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)',
            r'(\bOR\b|\bAND\b).*?[=<>]',
            r'[\'";]',
            r'--',
            r'/\*.*\*/'
        ]
        
        for field, value in data.items():
            if isinstance(value, str):
                for pattern in dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        logger.warning(f"Dangerous pattern detected in {field}: {pattern}")
                        return False, f"입력 데이터에 위험한 패턴이 감지되었습니다"
        
        return True, "검증 완료"

def require_valid_input(f):
    """입력 검증 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400
        
        from flask import current_app
        security = SecurityMiddleware()
        
        valid, message = security.validate_input(data)
        if not valid:
            return jsonify({"error": message}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def measure_performance(operation_name):
    """성능 측정 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed in {duration:.3f}s: {e}")
                raise
        return wrapper
    return decorator