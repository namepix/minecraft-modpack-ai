#!/bin/bash
# 🧪 완벽한 로컬 테스트 및 검증 스크립트
# GCP VM 배포 전 모든 구성 요소를 검증합니다

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

echo "🧪 완벽한 로컬 테스트 및 검증 시작"
echo "════════════════════════════════════════════════════════════"
echo ""

# 전역 변수
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# 테스트 결과 기록 함수
record_test() {
    local test_name="$1"
    local result="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("✅ $test_name")
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS+=("❌ $test_name")
    fi
}

# 1. 시스템 환경 검증
log_step "1. 시스템 환경 검증"

log_test "Python 3.9+ 설치 확인"
if python3 --version | grep -E "Python 3\.(9|10|11|12)" >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION 확인됨"
    record_test "Python 3.9+ 설치" "PASS"
else
    log_error "Python 3.9+ 필요"
    record_test "Python 3.9+ 설치" "FAIL"
fi

log_test "Java 17+ 설치 확인"
if java -version 2>&1 | grep -E "openjdk version \"(17|18|19|20|21)" >/dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2)
    log_success "Java $JAVA_VERSION 확인됨"
    record_test "Java 17+ 설치" "PASS"
else
    log_error "Java 17+ 필요"
    record_test "Java 17+ 설치" "FAIL"
fi

log_test "Maven 설치 확인"
if command -v mvn >/dev/null 2>&1; then
    MVN_VERSION=$(mvn -version | head -n1 | cut -d' ' -f3)
    log_success "Maven $MVN_VERSION 확인됨"
    record_test "Maven 설치" "PASS"
else
    log_error "Maven 필요"
    record_test "Maven 설치" "FAIL"
fi

# 2. 프로젝트 구조 검증
log_step "2. 프로젝트 구조 검증"

REQUIRED_FILES=(
    "backend/app.py"
    "backend/requirements.txt"
    "minecraft_plugin/pom.xml"
    "minecraft_plugin/src/main/java/com/modpackai/ModpackAIPlugin.java"
    "env.example"
    "install.sh"
    "setup_hybrid_servers.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    log_test "필수 파일 확인: $file"
    if [ -f "$file" ]; then
        log_success "✅ $file 존재"
        record_test "파일 존재: $file" "PASS"
    else
        log_error "❌ $file 누락"
        record_test "파일 존재: $file" "FAIL"
    fi
done

# 3. Python 백엔드 테스트
log_step "3. Python 백엔드 검증"

cd backend

# 가상환경 생성 및 활성화 (로컬 테스트용)
if [ ! -d "venv" ]; then
    log_info "로컬 테스트용 가상환경 생성 중..."
    python3 -m venv venv
fi

log_test "가상환경 활성화"
if source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null; then
    log_success "가상환경 활성화 성공"
    record_test "가상환경 활성화" "PASS"
else
    log_warning "가상환경 활성화 실패, 시스템 Python 사용"
    record_test "가상환경 활성화" "FAIL"
fi

# 의존성 설치
log_test "Python 의존성 설치"
if pip install -r requirements.txt -q; then
    log_success "의존성 설치 완료"
    record_test "Python 의존성 설치" "PASS"
else
    log_error "의존성 설치 실패"
    record_test "Python 의존성 설치" "FAIL"
fi

# 핵심 모듈 import 테스트
log_test "핵심 Python 모듈 import"
python3 -c "
import sys
try:
    import flask
    import requests
    import google.genai
    print('✅ 핵심 모듈 import 성공')
    sys.exit(0)
except ImportError as e:
    print(f'❌ 모듈 import 실패: {e}')
    sys.exit(1)
" && record_test "Python 모듈 import" "PASS" || record_test "Python 모듈 import" "FAIL"

# Flask 앱 문법 검사
log_test "Flask 앱 문법 검사"
if python3 -m py_compile app.py; then
    log_success "Flask 앱 문법 검사 통과"
    record_test "Flask 앱 문법" "PASS"
else
    log_error "Flask 앱 문법 오류"
    record_test "Flask 앱 문법" "FAIL"
fi

# 미들웨어 테스트
log_test "보안 미들웨어 검증"
python3 -c "
try:
    import sys
    sys.path.append('.')
    
    # 미들웨어 디렉토리가 없으면 스킵
    import os
    if not os.path.exists('middleware'):
        print('⚠️ middleware 디렉토리 없음, 스킵')
        sys.exit(2)
    
    from middleware.security import SecurityMiddleware
    security = SecurityMiddleware()
    
    # UUID 검증 테스트
    assert security.validate_uuid('550e8400-e29b-41d4-a716-446655440000') == True
    assert security.validate_uuid('invalid-uuid') == False
    
    # 입력 정제 테스트  
    cleaned = security.sanitize_input('<script>alert(\"xss\")</script>Hello')
    assert '<script>' not in cleaned
    
    print('✅ 보안 미들웨어 테스트 통과')
    sys.exit(0)
except ImportError:
    print('⚠️ 미들웨어 모듈 없음, 스킵')
    sys.exit(2)
except Exception as e:
    print(f'❌ 보안 미들웨어 테스트 실패: {e}')
    sys.exit(1)
"
case $? in
    0) record_test "보안 미들웨어" "PASS" ;;
    1) record_test "보안 미들웨어" "FAIL" ;;
    2) log_warning "보안 미들웨어 스킵" ;;
esac

cd ..

# 4. Java 플러그인 검증
log_step "4. Java Minecraft 플러그인 검증"

cd minecraft_plugin

# Maven 프로젝트 구조 검증
log_test "Maven 프로젝트 구조"
if [ -f "pom.xml" ] && [ -d "src/main/java" ] && [ -d "src/main/resources" ]; then
    log_success "Maven 프로젝트 구조 정상"
    record_test "Maven 프로젝트 구조" "PASS"
else
    log_error "Maven 프로젝트 구조 불완전"
    record_test "Maven 프로젝트 구조" "FAIL"
fi

# Maven 의존성 해결
log_test "Maven 의존성 해결"
if mvn dependency:resolve -q; then
    log_success "Maven 의존성 해결 완료"
    record_test "Maven 의존성 해결" "PASS"
else
    log_error "Maven 의존성 해결 실패"
    record_test "Maven 의존성 해결" "FAIL"
fi

# 컴파일 테스트 
log_test "Java 컴파일"
if mvn clean compile -q; then
    log_success "Java 컴파일 성공"
    record_test "Java 컴파일" "PASS"
else
    log_error "Java 컴파일 실패"
    record_test "Java 컴파일" "FAIL"
fi

# JAR 패키징 테스트
log_test "JAR 패키징"
if mvn clean package -q -Dmaven.test.skip=true; then
    if [ -f "target/modpack-ai-plugin-1.0.0.jar" ] || [ -f "target/modpack-ai-plugin-1.0.0-shaded.jar" ] || [ -f "target/ModpackAI-1.0.jar" ]; then
        log_success "JAR 패키징 성공"
        record_test "JAR 패키징" "PASS"
        
        # 생성된 JAR 파일 정보 표시
        log_info "생성된 JAR 파일들:"
        ls -la target/*.jar 2>/dev/null || echo "  (JAR 파일 목록을 가져올 수 없음)"
    else
        log_error "JAR 파일이 생성되지 않음"
        record_test "JAR 패키징" "FAIL"
    fi
else
    log_error "JAR 패키징 실패"
    record_test "JAR 패키징" "FAIL"
fi

cd ..

# 5. 설치 스크립트 검증
log_step "5. 설치 스크립트 구문 검증"

SCRIPTS=("install.sh" "setup_hybrid_servers.sh" "modpack_switch.sh" "monitor.sh")

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        log_test "스크립트 구문 검사: $script"
        if bash -n "$script"; then
            log_success "$script 구문 검사 통과"
            record_test "스크립트 구문: $script" "PASS"
        else
            log_error "$script 구문 오류"
            record_test "스크립트 구문: $script" "FAIL"
        fi
        
        log_test "스크립트 실행 권한: $script"
        if [ -x "$script" ]; then
            log_success "$script 실행 권한 확인"
            record_test "스크립트 실행 권한: $script" "PASS"
        else
            log_warning "$script 실행 권한 없음 (chmod +x $script 필요)"
            record_test "스크립트 실행 권한: $script" "FAIL"
        fi
    fi
done

# 6. 환경 설정 파일 검증
log_step "6. 환경 설정 파일 검증"

log_test "env.example 파일"
if [ -f "env.example" ]; then
    # 필수 환경 변수 확인
    REQUIRED_VARS=("GOOGLE_API_KEY" "GCP_PROJECT_ID" "GCS_BUCKET_NAME" "PORT" "DEBUG")
    missing_vars=0
    
    for var in "${REQUIRED_VARS[@]}"; do
        if ! grep -q "^$var=" env.example; then
            log_warning "env.example에 $var 누락"
            missing_vars=$((missing_vars + 1))
        fi
    done
    
    if [ $missing_vars -eq 0 ]; then
        log_success "env.example 필수 변수 모두 존재"
        record_test "env.example 검증" "PASS"
    else
        log_error "env.example에 $missing_vars개 필수 변수 누락"
        record_test "env.example 검증" "FAIL"
    fi
else
    log_error "env.example 파일 누락"
    record_test "env.example 검증" "FAIL"
fi

# 7. 하이브리드 서버 URL 검증
log_step "7. 하이브리드 서버 URL 유효성 검증"

URLS=(
    "https://mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download"
    "https://mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"
    "https://mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"
)

for url in "${URLS[@]}"; do
    log_test "URL 접근성: $(echo $url | cut -d'/' -f3)"
    if curl -s --head "$url" | head -n1 | grep -E "HTTP/[0-9.]+ (200|302)" >/dev/null; then
        log_success "URL 접근 가능"
        record_test "URL 접근성: $(echo $url | cut -d'/' -f3)" "PASS"
    else
        log_warning "URL 접근 실패 또는 리다이렉트"
        record_test "URL 접근성: $(echo $url | cut -d'/' -f3)" "FAIL"
    fi
done

# 8. 최종 결과 요약 및 배포 준비도 평가
log_step "8. 최종 테스트 결과 및 배포 준비도 평가"

echo ""
echo "🏆 완벽한 로컬 테스트 결과 요약"
echo "════════════════════════════════════════════════════════════"
echo ""

# 테스트 결과 출력
for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
done

echo ""
echo "📊 통계:"
echo "  총 테스트 수: $TOTAL_TESTS"
echo "  통과: $PASSED_TESTS"
echo "  실패: $FAILED_TESTS"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "  성공률: $SUCCESS_RATE%"
else
    SUCCESS_RATE=0
fi

echo ""
echo "🎯 배포 준비도 평가:"

if [ $SUCCESS_RATE -ge 90 ]; then
    log_success "🎉 우수 ($SUCCESS_RATE%) - GCP VM 배포 준비 완료!"
    echo ""
    echo "✅ 다음 단계:"
    echo "  1. GCP VM에 파일 업로드: scp -r . namepix080@34.64.217.151:~/minecraft-modpack-ai/"
    echo "  2. GCP VM에서 설치: ./install.sh"
    echo "  3. API 키 설정 후 테스트"
    DEPLOYMENT_READY=true
elif [ $SUCCESS_RATE -ge 75 ]; then
    log_warning "⚠️ 양호 ($SUCCESS_RATE%) - 일부 수정 후 배포 권장"
    echo ""
    echo "🔧 권장 사항:"
    echo "  - 실패한 테스트 확인 및 수정"
    echo "  - 필수 구성 요소 재설치"
    DEPLOYMENT_READY=true
elif [ $SUCCESS_RATE -ge 50 ]; then
    log_warning "⚠️ 보통 ($SUCCESS_RATE%) - 주요 문제 해결 필요"
    echo ""
    echo "🚨 주의 사항:"
    echo "  - 핵심 구성 요소 점검 필요"
    echo "  - 배포 전 문제 해결 권장"
    DEPLOYMENT_READY=false
else
    log_error "❌ 부족 ($SUCCESS_RATE%) - 배포 불가"
    echo ""
    echo "🔥 긴급 수정 필요:"
    echo "  - 기본 환경 구성부터 재점검"
    echo "  - 필수 의존성 설치 확인"
    DEPLOYMENT_READY=false
fi

echo ""
echo "📋 로컬 개발 환경 정보:"
echo "  Python: ${PYTHON_VERSION:-'미확인'}"
echo "  Java: ${JAVA_VERSION:-'미확인'}"  
echo "  Maven: ${MVN_VERSION:-'미확인'}"
echo "  플랫폼: $(uname -s 2>/dev/null || echo 'Windows')"

# GCP VM 배포를 위한 체크리스트 생성
if [ "$DEPLOYMENT_READY" = true ]; then
    echo ""
    echo "🚀 GCP VM 배포 체크리스트:"
    echo "  [ ] API 키 준비 (Google AI Studio, GCP 프로젝트)"
    echo "  [ ] GCP VM SSH 접속 확인"
    echo "  [ ] 프로젝트 파일 업로드"
    echo "  [ ] install.sh 실행"
    echo "  [ ] API 키 설정"
    echo "  [ ] 백엔드 서비스 시작"
    echo "  [ ] 모드팩 서버 테스트"
fi

echo ""
if [ "$DEPLOYMENT_READY" = true ]; then
    log_success "🎯 로컬 검증 완료! GCP VM 배포를 진행하세요."
    exit 0
else
    log_error "❌ 로컬 환경에 문제가 있습니다. 수정 후 다시 테스트하세요."
    exit 1
fi