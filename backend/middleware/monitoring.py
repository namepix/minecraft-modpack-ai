"""
모니터링 및 메트릭 수집 미들웨어
시스템 성능과 사용량을 추적합니다.
"""

import time
import psutil
import os
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
from flask import g, request, jsonify

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'api_calls': defaultdict(int),
            'response_times': defaultdict(list),
            'error_counts': defaultdict(int),
            'model_usage': defaultdict(int),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'active_users': set()
        }
        self.start_time = time.time()
        
    def record_api_call(self, endpoint, method):
        """API 호출 기록"""
        key = f"{method} {endpoint}"
        self.metrics['api_calls'][key] += 1
        
    def record_response_time(self, endpoint, duration):
        """응답 시간 기록"""
        self.metrics['response_times'][endpoint].append(duration)
        # 최근 100개만 유지
        if len(self.metrics['response_times'][endpoint]) > 100:
            self.metrics['response_times'][endpoint].pop(0)
            
    def record_error(self, endpoint, error_type):
        """오류 기록"""
        key = f"{endpoint}:{error_type}"
        self.metrics['error_counts'][key] += 1
        
    def record_model_usage(self, model_name):
        """AI 모델 사용량 기록"""
        self.metrics['model_usage'][model_name] += 1
        
    def record_user_activity(self, user_uuid):
        """사용자 활동 기록"""
        if user_uuid:
            self.metrics['active_users'].add(user_uuid)
            
    def collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # 메모리 사용량
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'].append({
                'timestamp': time.time(),
                'percent': memory.percent,
                'available': memory.available,
                'used': memory.used
            })
            
            # CPU 사용량
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_usage'].append({
                'timestamp': time.time(),
                'percent': cpu_percent
            })
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
    
    def get_metrics_summary(self):
        """메트릭 요약 정보 반환"""
        now = time.time()
        uptime = now - self.start_time
        
        # 평균 응답 시간 계산
        avg_response_times = {}
        for endpoint, times in self.metrics['response_times'].items():
            if times:
                avg_response_times[endpoint] = sum(times) / len(times)
        
        # 최근 CPU/메모리 사용량
        latest_memory = self.metrics['memory_usage'][-1] if self.metrics['memory_usage'] else None
        latest_cpu = self.metrics['cpu_usage'][-1] if self.metrics['cpu_usage'] else None
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'total_api_calls': sum(self.metrics['api_calls'].values()),
            'api_calls_by_endpoint': dict(self.metrics['api_calls']),
            'average_response_times': avg_response_times,
            'total_errors': sum(self.metrics['error_counts'].values()),
            'errors_by_type': dict(self.metrics['error_counts']),
            'model_usage': dict(self.metrics['model_usage']),
            'active_users_count': len(self.metrics['active_users']),
            'current_memory_usage': latest_memory['percent'] if latest_memory else None,
            'current_cpu_usage': latest_cpu['percent'] if latest_cpu else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_report(self):
        """성능 보고서 생성"""
        summary = self.get_metrics_summary()
        
        # 성능 임계값 체크
        alerts = []
        
        if summary['current_memory_usage'] and summary['current_memory_usage'] > 80:
            alerts.append(f"높은 메모리 사용량: {summary['current_memory_usage']:.1f}%")
            
        if summary['current_cpu_usage'] and summary['current_cpu_usage'] > 80:
            alerts.append(f"높은 CPU 사용량: {summary['current_cpu_usage']:.1f}%")
        
        # 느린 응답 시간 체크
        for endpoint, avg_time in summary['average_response_times'].items():
            if avg_time > 5.0:
                alerts.append(f"느린 응답: {endpoint} ({avg_time:.2f}초)")
        
        # 오류율 체크
        total_calls = summary['total_api_calls']
        total_errors = summary['total_errors']
        if total_calls > 0:
            error_rate = (total_errors / total_calls) * 100
            if error_rate > 5:
                alerts.append(f"높은 오류율: {error_rate:.1f}%")
        
        return {
            'summary': summary,
            'alerts': alerts,
            'status': 'warning' if alerts else 'healthy'
        }
    
    def reset_metrics(self):
        """메트릭 초기화"""
        self.metrics = {
            'api_calls': defaultdict(int),
            'response_times': defaultdict(list),
            'error_counts': defaultdict(int),
            'model_usage': defaultdict(int),
            'memory_usage': deque(maxlen=100),
            'cpu_usage': deque(maxlen=100),
            'active_users': set()
        }
        self.start_time = time.time()

# 전역 메트릭 수집기
metrics_collector = MetricsCollector()

class MonitoringMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 모니터링 미들웨어 초기화"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # 메트릭 엔드포인트 추가
        @app.route('/metrics', methods=['GET'])
        def get_metrics():
            return jsonify(metrics_collector.get_metrics_summary())
        
        @app.route('/health/detailed', methods=['GET'])
        def get_detailed_health():
            return jsonify(metrics_collector.get_performance_report())
    
    def before_request(self):
        """요청 전 처리"""
        g.request_start_time = time.time()
        
        # API 호출 기록
        metrics_collector.record_api_call(request.endpoint or request.path, request.method)
        
        # 시스템 메트릭 주기적 수집 (10번째 요청마다)
        if sum(metrics_collector.metrics['api_calls'].values()) % 10 == 0:
            metrics_collector.collect_system_metrics()
    
    def after_request(self, response):
        """요청 후 처리"""
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            
            # 응답 시간 기록
            metrics_collector.record_response_time(
                request.endpoint or request.path, 
                duration
            )
            
            # 오류 기록
            if response.status_code >= 400:
                metrics_collector.record_error(
                    request.endpoint or request.path,
                    str(response.status_code)
                )
            
            # 성능 헤더 추가
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response

def track_model_usage(model_name):
    """AI 모델 사용량 추적 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            metrics_collector.record_model_usage(model_name)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def track_user_activity(f):
    """사용자 활동 추적 데코레이터"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json() if request.is_json else {}
        user_uuid = data.get('player_uuid')
        if user_uuid:
            metrics_collector.record_user_activity(user_uuid)
        return f(*args, **kwargs)
    return wrapper