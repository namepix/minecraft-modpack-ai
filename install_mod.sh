#!/bin/bash
# ModpackAI NeoForge 모드 자동 설치 스크립트

set -euo pipefail

# 색깔 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 전역 변수
BUILT_MOD_FILE=""

# 시스템 정보 확인
check_system() {
    log_info "시스템 요구사항 확인 중..."
    
    # Java 17+ 확인
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
        JAVA_MAJOR=$(echo $JAVA_VERSION | cut -d'.' -f1)
        
        if [[ $JAVA_MAJOR -ge 17 ]]; then
            log_success "Java $JAVA_VERSION 확인됨"
        else
            log_error "Java 17+ 필요. 현재 버전: $JAVA_VERSION"
            exit 1
        fi
    else
        log_error "Java가 설치되지 않음"
        exit 1
    fi
    
    # Gradle 또는 Gradle 래퍼 확인
    if [[ -x "minecraft_mod/gradlew" ]]; then
        log_success "Gradle 래퍼 확인됨 (minecraft_mod/gradlew)"
    elif ! command -v gradle &> /dev/null; then
        log_warning "Gradle이 설치되지 않음. 설치를 진행합니다..."
        install_gradle
    else
        log_success "시스템 Gradle 확인됨"
    fi
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3이 설치되지 않음"
        exit 1
    else
        log_success "Python 3 확인됨"
    fi

    # Python venv 모듈 확인 (Debian 계열에서 종종 누락)
    if ! python3 -c "import venv" 2>/dev/null; then
        log_warning "python3-venv 모듈이 없어 가상환경 생성을 할 수 없습니다. 설치를 진행합니다..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-venv || true
        fi
    fi
}

# Gradle 설치
install_gradle() {
    log_info "Gradle 설치 중..."
    
    # 우분투/데비안
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y gradle
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        sudo yum install -y gradle
    # macOS
    elif command -v brew &> /dev/null; then
        brew install gradle
    else
        log_error "지원되지 않는 운영체제입니다"
        exit 1
    fi
    
    log_success "Gradle 설치 완료"
}

# 백엔드 설치
install_backend() {
    log_info "AI 백엔드 설치 중..."
    
    cd backend
    
    # 가상환경 생성
    if [[ ! -d "venv" ]]; then
        if ! python3 -m venv venv; then
            log_warning "가상환경 생성 실패. python3-venv 패키지를 설치하고 재시도합니다."
            if command -v apt-get &> /dev/null; then
                sudo apt-get update && sudo apt-get install -y python3-venv
            fi
            python3 -m venv venv
        fi
    fi
    
    # 가상환경 활성화
    source venv/bin/activate
    
    # 패키지 설치
    pip install --upgrade pip
    pip install -r requirements.txt
    
    cd ..
    
    log_success "AI 백엔드 설치 완료"
}

# NeoForge 모드 빌드
build_mod() {
    log_info "NeoForge 모드 빌드 중..."
    
    cd minecraft_mod
    
    # Gradle 빌드 (래퍼 우선, 없으면 시스템 gradle)
    if [[ -x "./gradlew" ]]; then
        ./gradlew clean build --no-daemon
    else
        gradle clean build --no-daemon
    fi

    # 산출물 자동 탐지 (modpackai-*.jar 중 최신 파일)
    BUILT_MOD_FILE=$(find build/libs -maxdepth 1 -type f -name "modpackai-*.jar" | sort | tail -n 1 || true)
    if [[ -n "${BUILT_MOD_FILE}" && -f "${BUILT_MOD_FILE}" ]]; then
        log_success "NeoForge 모드 빌드 완료: ${BUILT_MOD_FILE}"
    else
        log_error "모드 빌드 실패: build/libs/modpackai-*.jar 산출물을 찾을 수 없습니다"
        exit 1
    fi
    
    cd ..
}

# 모드팩 감지 및 모드 설치
install_to_modpacks() {
    log_info "모드팩 감지 및 모드 설치 중..."
    
    INSTALLED_COUNT=0
    local MOD_FILE_PATH="${BUILT_MOD_FILE}"
    if [[ -z "${MOD_FILE_PATH}" ]]; then
        MOD_FILE_PATH=$(find minecraft_mod/build/libs -maxdepth 1 -type f -name "modpackai-*.jar" | sort | tail -n 1 || true)
    fi
    if [[ -z "${MOD_FILE_PATH}" || ! -f "${MOD_FILE_PATH}" ]]; then
        log_error "설치에 사용할 모드 JAR를 찾을 수 없습니다 (minecraft_mod/build/libs/modpackai-*.jar)"
        exit 1
    fi
    
    # 홈 디렉토리에서 모드팩 찾기
    for dir in ~/*/; do
        if [[ -d "$dir/mods" ]]; then
            MODPACK_NAME=$(basename "$dir")
            log_info "모드팩 발견: $MODPACK_NAME"

            # 호환성 체크: NeoForge 전용 설치
            IS_FABRIC=0
            IS_FORGE=0
            IS_NEOFORGE=0

            # Fabric 런처 존재 시 Fabric으로 판단
            if [[ -f "$dir/fabric-server-launcher.jar" ]]; then
                IS_FABRIC=1
            fi

            # 루트에 버전 표시 JAR 존재 시 Forge/NeoForge 추정
            if ls "$dir"/forge-*.jar >/dev/null 2>&1; then
                IS_FORGE=1
            fi
            if ls "$dir"/neoforge-*.jar >/dev/null 2>&1; then
                IS_NEOFORGE=1
            fi

            # 라이브러리에서 문자열 탐지 보강
            if [[ -d "$dir/libraries" ]]; then
                if grep -Rqi "neoforge" "$dir/libraries" 2>/dev/null; then
                    IS_NEOFORGE=1
                fi
                if grep -Rqi "forge" "$dir/libraries" 2>/dev/null && [[ $IS_NEOFORGE -eq 0 ]]; then
                    IS_FORGE=1
                fi
            fi

            if [[ $IS_FABRIC -eq 1 ]]; then
                log_warning "호환되지 않는 서버 타입(Fabric): $MODPACK_NAME → 건너뜀"
                continue
            fi
            if [[ $IS_FORGE -eq 1 && $IS_NEOFORGE -eq 0 ]]; then
                log_warning "호환되지 않는 서버 타입(Forge): $MODPACK_NAME → 건너뜀"
                continue
            fi
            if [[ $IS_NEOFORGE -eq 0 ]]; then
                log_warning "NeoForge 징후가 없어 건너뜀: $MODPACK_NAME"
                continue
            fi
            
            # 모드 복사
            cp "${MOD_FILE_PATH}" "$dir/mods/"
            
            if ls "$dir/mods"/modpackai-*.jar >/dev/null 2>&1; then
                log_success "모드 설치 완료: $MODPACK_NAME"
                ((INSTALLED_COUNT++))
            else
                log_warning "모드 설치 실패: $MODPACK_NAME"
            fi
        fi
    done
    
    if [[ $INSTALLED_COUNT -eq 0 ]]; then
        log_warning "NeoForge 모드팩을 찾을 수 없습니다"
        log_info "mods/ 폴더가 있는 모드팩 디렉토리가 필요합니다"
    else
        log_success "$INSTALLED_COUNT개 모드팩에 모드 설치 완료"
    fi
}

# 백엔드 서비스 설정
setup_backend_service() {
    log_info "백엔드 서비스 설정 중..."
    
    # 백엔드 디렉토리로 이동
    BACKEND_DIR="$HOME/minecraft-ai-backend"
    
    if [[ ! -d "$BACKEND_DIR" ]]; then
        mkdir -p "$BACKEND_DIR"
        cp -r backend/* "$BACKEND_DIR/"
    fi

    # 대상 경로에 venv 보장 (service-only로 실행될 수 있으므로 여기서도 보장)
    if [[ ! -d "$BACKEND_DIR/venv" ]]; then
        log_info "백엔드 가상환경 생성 및 의존성 설치 중..."
        python3 -m venv "$BACKEND_DIR/venv"
        source "$BACKEND_DIR/venv/bin/activate"
        if [[ -f "$BACKEND_DIR/requirements.txt" ]]; then
            pip install --upgrade pip
            pip install -r "$BACKEND_DIR/requirements.txt"
        fi
        deactivate || true
    fi
    
    # systemd 서비스 파일 생성
    cat > /tmp/mc-ai-backend.service << EOF
[Unit]
Description=Minecraft Modpack AI Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 서비스 등록
    sudo mv /tmp/mc-ai-backend.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable mc-ai-backend
    
    log_success "백엔드 서비스 설정 완료"
}

# API 키 설정 안내
setup_api_keys() {
    log_info "API 키 설정 안내"
    
    ENV_FILE="$HOME/minecraft-ai-backend/.env"
    
    if [[ ! -f "$ENV_FILE" ]]; then
        cat > "$ENV_FILE" << EOF
# Google Gemini API 키 (권장, 웹검색 지원)
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI API 키 (선택, 백업용)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API 키 (선택, 백업용)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Flask 서버 설정
PORT=5000
DEBUG=false
EOF
    fi
    
    echo
    echo "🔑 API 키 설정이 필요합니다!"
    echo "   파일 위치: $ENV_FILE"
    echo
    echo "📝 다음 명령어로 API 키를 입력하세요:"
    echo "   nano $ENV_FILE"
    echo
    echo "🌟 Google Gemini API 키 발급 (무료):"
    echo "   https://makersuite.google.com/app/apikey"
    echo
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    # 백엔드 서비스 시작
    sudo systemctl start mc-ai-backend
    
    # 서비스 상태 확인
    if sudo systemctl is-active --quiet mc-ai-backend; then
        log_success "백엔드 서비스 시작됨"
    else
        log_warning "백엔드 서비스 시작 실패 - API 키를 설정 후 다시 시도하세요"
    fi
}

# 설치 검증
verify_installation() {
    log_info "설치 검증 중..."
    
    # 모드 파일 확인
    MOD_COUNT=$(find ~ -type f -name "modpackai-*.jar" -path "*/mods/*" | wc -l)
    if [[ $MOD_COUNT -gt 0 ]]; then
        log_success "모드 설치 확인: $MOD_COUNT 개 모드팩"
    else
        log_warning "설치된 모드를 찾을 수 없음"
    fi
    
    # 백엔드 상태 확인
    if sudo systemctl is-active --quiet mc-ai-backend; then
        log_success "백엔드 서비스 실행 중"
        
        # API 테스트
        sleep 2
        if curl -s http://localhost:5000/health > /dev/null; then
            log_success "API 연결 확인"
        else
            log_warning "API 연결 실패 - API 키를 확인하세요"
        fi
    else
        log_warning "백엔드 서비스 중지됨"
    fi
}

# 사용법 안내
show_usage() {
    echo
    echo "🎮 ModpackAI 설치가 완료되었습니다!"
    echo
    echo "📋 다음 단계:"
    echo "   1. API 키 설정: nano $HOME/minecraft-ai-backend/.env"
    echo "   2. 서비스 재시작: sudo systemctl restart mc-ai-backend"
    echo "   3. NeoForge 모드팩 서버 시작"
    echo
    echo "🎯 게임 내 명령어:"
    echo "   /ai <질문>              - AI에게 질문하기"
    echo "   /ai                     - AI GUI 열기"
    echo "   /modpackai give         - AI 아이템 받기"
    echo "   /modpackai help         - 도움말 보기"
    echo
    echo "🔍 문제 해결:"
    echo "   - 서비스 상태: sudo systemctl status mc-ai-backend"
    echo "   - 로그 확인: sudo journalctl -u mc-ai-backend -f"
    echo "   - API 테스트: curl http://localhost:5000/health"
    echo
}

# 메인 실행 함수
main() {
    # 인자 파싱
    SERVICE_ONLY=0
    if [[ "${1:-}" == "--service-only" ]]; then
        SERVICE_ONLY=1
    fi

    echo "🚀 ModpackAI NeoForge 모드 설치 시작"
    echo

    if [[ $SERVICE_ONLY -eq 1 ]]; then
        # 서비스 설정만 수행 (단계별 설치 4단계용)
        setup_backend_service
        setup_api_keys
        start_services
        verify_installation
        show_usage
        log_success "서비스 설정 완료!"
        return 0
    fi

    # 전체 설치 플로우
    check_system
    install_backend
    build_mod
    install_to_modpacks
    setup_backend_service
    setup_api_keys
    start_services
    verify_installation
    show_usage
    
    log_success "설치 완료!"
}

# 스크립트 실행
main "$@"