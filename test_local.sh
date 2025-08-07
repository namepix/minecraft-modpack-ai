#!/bin/bash
# 🧪 로컬 테스트 실행 스크립트
# API 키 없이도 실행 가능한 테스트들

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "🧪 로컬 테스트 실행 시작"

# Python 백엔드 테스트
log_info "🐍 Python 백엔드 테스트"
cd backend

# 가상환경 확인 (있으면 사용)
if [ -d "venv" ]; then
    log_info "가상환경 활성화"
    source venv/bin/activate || {
        log_warning "가상환경 활성화 실패, 시스템 Python 사용"
    }
fi

# 의존성 확인
log_info "Python 의존성 확인 중..."
python3 -c "import flask, requests" 2>/dev/null || {
    log_warning "일부 의존성이 없습니다. pip install -r requirements.txt 실행을 권장합니다."
}

# Mock 기반 단위 테스트 (API 키 불필요)
log_info "📝 단위 테스트 실행 (Mock 사용)..."

test_files=(
    "tests/test_language_mapper.py"
    "tests/test_modpack_analyzer.py" 
    "tests/test_recipe_manager.py"
    "tests/test_utils.py"
)

passed_tests=0
total_tests=0

for test_file in "${test_files[@]}"; do
    if [ -f "$test_file" ]; then
        total_tests=$((total_tests + 1))
        log_info "테스트 중: $test_file"
        
        if python3 -m pytest "$test_file" -v --tb=short -q; then
            log_success "✅ $test_file 통과"
            passed_tests=$((passed_tests + 1))
        else
            log_error "❌ $test_file 실패"
        fi
    else
        log_warning "⚠️ $test_file 파일이 없습니다."
    fi
done

# 새로운 미들웨어 테스트
log_info "🔒 보안 미들웨어 테스트..."
python3 -c "
try:
    from middleware.security import SecurityMiddleware, require_valid_input, measure_performance
    security = SecurityMiddleware()
    
    # UUID 검증 테스트
    assert security.validate_uuid('550e8400-e29b-41d4-a716-446655440000') == True
    assert security.validate_uuid('invalid-uuid') == False
    
    # 입력 정제 테스트  
    cleaned = security.sanitize_input('<script>alert(\"xss\")</script>Hello')
    assert '<script>' not in cleaned
    
    print('✅ 보안 미들웨어 테스트 통과')
except Exception as e:
    print(f'❌ 보안 미들웨어 테스트 실패: {e}')
    exit(1)
"

log_info "📊 모니터링 미들웨어 테스트..."
python3 -c "
try:
    from middleware.monitoring import MetricsCollector, MonitoringMiddleware
    
    collector = MetricsCollector()
    collector.record_api_call('/test', 'GET')
    collector.record_response_time('/test', 0.5)
    
    summary = collector.get_metrics_summary()
    assert summary['total_api_calls'] >= 1
    assert '/test' in summary['api_calls_by_endpoint']
    
    print('✅ 모니터링 미들웨어 테스트 통과')
except Exception as e:
    print(f'❌ 모니터링 미들웨어 테스트 실패: {e}')
    exit(1)
"

# Flask 앱 문법 검사
log_info "🌐 Flask 앱 문법 검사..."
if python3 -m py_compile app.py; then
    log_success "✅ Flask 앱 문법 검사 통과"
else
    log_error "❌ Flask 앱 문법 오류"
fi

cd ..

# Java 플러그인 테스트
log_info "☕ Java 플러그인 테스트"
cd minecraft_plugin

if command -v mvn &> /dev/null; then
    log_info "Maven 빌드 및 테스트..."
    if mvn clean compile test -q; then
        log_success "✅ Java 플러그인 빌드 및 테스트 통과"
        passed_tests=$((passed_tests + 1))
    else
        log_error "❌ Java 플러그인 테스트 실패"
    fi
    total_tests=$((total_tests + 1))
else
    log_warning "⚠️ Maven이 설치되지 않아 Java 테스트를 건너뜁니다."
fi

cd ..

# 결과 요약
echo ""
log_info "📊 테스트 결과 요약"
echo "========================================="
echo "통과한 테스트: $passed_tests / $total_tests"
echo "========================================="

if [ "$passed_tests" -eq "$total_tests" ]; then
    log_success "🎉 모든 로컬 테스트 통과! 배포 준비 완료"
    exit 0
else
    failed_tests=$((total_tests - passed_tests))
    log_error "❌ $failed_tests 개 테스트 실패"
    log_info "실패한 테스트를 수정한 후 다시 실행하세요."
    exit 1
fi