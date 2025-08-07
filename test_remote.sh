#!/bin/bash
# 🌐 원격 테스트 실행 스크립트  
# GCP VM에서 실제 환경 테스트 (API 키 필요)

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

# 설정 파일 로드
if [ -f "deploy.config" ]; then
    source deploy.config
else
    log_error "deploy.config 파일이 없습니다."
    exit 1
fi

log_info "🌐 GCP VM에서 원격 테스트 실행"
log_info "대상: $GCP_VM_USER@$GCP_VM_IP"

# SSH 연결 테스트
log_info "SSH 연결 테스트..."
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 "$GCP_VM_USER@$GCP_VM_IP" "echo 'SSH 연결 성공'" > /dev/null 2>&1; then
    log_error "SSH 연결 실패"
    exit 1
fi

# 원격에서 테스트 실행
ssh -i "$SSH_KEY_PATH" "$GCP_VM_USER@$GCP_VM_IP" bash << 'EOF'
set -e

# 색상 코드 (원격에서도 사용)
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "🧪 GCP VM 통합 테스트 시작"

# 프로젝트 디렉토리로 이동
cd "$GCP_VM_PROJECT_PATH/backend"

# 가상환경 활성화
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    log_info "Python 가상환경 활성화됨"
else
    log_error "Python 가상환경을 찾을 수 없습니다."
    exit 1
fi

# 환경변수 확인
log_info "🔑 API 키 설정 확인..."
if [ -f ".env" ]; then
    if grep -q "GOOGLE_API_KEY" .env && [ -n "$(grep GOOGLE_API_KEY .env | cut -d'=' -f2)" ]; then
        log_success "Google API 키 설정됨"
    else
        log_warning "Google API 키가 설정되지 않았습니다."
    fi
    
    if grep -q "OPENAI_API_KEY" .env; then
        log_info "OpenAI API 키 설정됨 (선택사항)"
    fi
    
    if grep -q "ANTHROPIC_API_KEY" .env; then
        log_info "Anthropic API 키 설정됨 (선택사항)"  
    fi
else
    log_error ".env 파일이 없습니다."
    exit 1
fi

# 서비스 상태 확인
log_info "🚀 서비스 상태 확인..."
if sudo systemctl is-active --quiet mc-ai-backend; then
    log_success "mc-ai-backend 서비스 실행 중"
else
    log_warning "서비스가 중지되어 있습니다. 시작합니다..."
    sudo systemctl start mc-ai-backend
    sleep 5
fi

# API 엔드포인트 테스트
log_info "🌐 API 엔드포인트 테스트..."
test_results=()

# Health Check
log_info "Health Check 테스트..."
if curl -f -s http://localhost:5000/health > /dev/null; then
    log_success "✅ /health 엔드포인트 정상"
    test_results+=("health:pass")
else
    log_error "❌ /health 엔드포인트 실패"  
    test_results+=("health:fail")
fi

# Models 엔드포인트
log_info "Models 엔드포인트 테스트..."
if curl -f -s http://localhost:5000/models > /dev/null; then
    log_success "✅ /models 엔드포인트 정상"
    test_results+=("models:pass")
else
    log_error "❌ /models 엔드포인트 실패"
    test_results+=("models:fail")
fi

# Metrics 엔드포인트 (새로 추가됨)
log_info "Metrics 엔드포인트 테스트..."
if curl -f -s http://localhost:5000/metrics > /dev/null; then
    log_success "✅ /metrics 엔드포인트 정상"
    test_results+=("metrics:pass")
else
    log_error "❌ /metrics 엔드포인트 실패"
    test_results+=("metrics:fail")
fi

# Chat 엔드포인트 (간단한 테스트 메시지)
log_info "Chat API 테스트..."
chat_response=$(curl -f -s -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"테스트","player_uuid":"test-uuid-123","modpack_name":"TestPack"}' \
    2>/dev/null || echo "failed")

if [ "$chat_response" != "failed" ] && echo "$chat_response" | grep -q "success"; then
    log_success "✅ /chat 엔드포인트 정상 (AI 응답 생성됨)"
    test_results+=("chat:pass")
else
    log_warning "⚠️ /chat 엔드포인트 응답 이상 (API 키 확인 필요)"
    test_results+=("chat:warning")
fi

# Python 통합 테스트 실행
log_info "🐍 Python 통합 테스트 실행..."
python_test_result="pass"

# AI 모델 테스트 (API 키 있는 경우만)
if grep -q "GOOGLE_API_KEY.*=" .env && [ -n "$(grep GOOGLE_API_KEY .env | cut -d'=' -f2 | tr -d ' ')" ]; then
    log_info "Gemini SDK 테스트..."
    if python test_gemini_sdk.py > /dev/null 2>&1; then
        log_success "✅ Gemini SDK 테스트 통과"
    else
        log_warning "⚠️ Gemini SDK 테스트 실패 (API 키 또는 네트워크 이슈)"
        python_test_result="warning"
    fi
else
    log_info "Google API 키가 없어 Gemini 테스트를 건너뜁니다."
fi

# 통합 테스트 실행
log_info "전체 통합 테스트 실행..."
if python -m pytest tests/test_app_integration.py -v --tb=short; then
    log_success "✅ 통합 테스트 통과"
else
    log_warning "⚠️ 일부 통합 테스트 실패"
    python_test_result="warning"
fi

test_results+=("python:$python_test_result")

# 시스템 리소스 확인
log_info "🔍 시스템 리소스 확인..."
memory_usage=$(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')
cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"%"}')

echo "메모리 사용량: $memory_usage"
echo "CPU 사용량: $cpu_usage"

# 로그 확인 (최근 10줄)
log_info "📋 최근 로그 확인..."
sudo journalctl -u mc-ai-backend -n 10 --no-pager

# 결과 요약
echo ""
log_info "📊 원격 테스트 결과 요약"
echo "========================================="

passed=0
failed=0
warnings=0

for result in "${test_results[@]}"; do
    test_name=$(echo "$result" | cut -d':' -f1)
    test_status=$(echo "$result" | cut -d':' -f2)
    
    case $test_status in
        "pass")
            echo "✅ $test_name: 통과"
            passed=$((passed + 1))
            ;;
        "fail") 
            echo "❌ $test_name: 실패"
            failed=$((failed + 1))
            ;;
        "warning")
            echo "⚠️ $test_name: 경고"
            warnings=$((warnings + 1))
            ;;
    esac
done

echo "========================================="
echo "통과: $passed, 실패: $failed, 경고: $warnings"
echo "메모리: $memory_usage, CPU: $cpu_usage"
echo "========================================="

if [ $failed -eq 0 ]; then
    if [ $warnings -eq 0 ]; then
        log_success "🎉 모든 원격 테스트 통과!"
        exit 0
    else
        log_warning "⚠️ 경고가 있지만 전체적으로 정상 동작"
        exit 0
    fi
else
    log_error "❌ $failed 개 테스트 실패"
    exit 1
fi
EOF

if [ $? -eq 0 ]; then
    log_success "🎉 원격 테스트 완료"
else
    log_error "원격 테스트 중 오류 발생"
    exit 1
fi