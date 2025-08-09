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
    
    # Java 21+ 확인
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}')
        JAVA_MAJOR=$(echo $JAVA_VERSION | cut -d'.' -f1)
        
        if [[ $JAVA_MAJOR -ge 21 ]]; then
            log_success "Java $JAVA_VERSION 확인됨"
        else
            log_error "Java 21+ 필요. 현재 버전: $JAVA_VERSION"
            exit 1
        fi
    else
        log_error "Java가 설치되지 않음"
        exit 1
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

# 백엔드 설치
install_backend() {
    log_info "AI 백엔드 설치 중..."
    
    cd backend
    
    # 가상환경 생성
    if [[ ! -d "venv" ]]; then
        if ! python3 -m venv venv; then
            log_warning "가상환경 생성 실패. python3-venv 패키지를 설��하고 재시도합니다."
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
    
    # Gradle Wrapper 생성 및 실행 (가장 안정적인 방법)
    if [[ ! -f "gradlew" ]]; then
        log_warning "Gradle Wrapper(gradlew)가 없습니다. 생성합니다..."
        # 시스템 gradle이 너무 오래되었을 수 있으므로, 임시 gradle로 wrapper를 생성
        wget -q https://services.gradle.org/distributions/gradle-8.8-bin.zip -O /tmp/gradle-8.8-bin.zip
        unzip -q /tmp/gradle-8.8-bin.zip -d /tmp
        /tmp/gradle-8.8/bin/gradle wrapper --gradle-version 8.8 --distribution-type all
        rm -rf /tmp/gradle-8.8 /tmp/gradle-8.8-bin.zip
    fi

    # Gradle Wrapper를 사용하여 빌드
    chmod +x ./gradlew
    ./gradlew build

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
    local MOD_FILE_PATH="minecraft_mod/${BUILT_MOD_FILE}"
    if [[ -z "${BUILT_MOD_FILE}" || ! -f "${MOD_FILE_PATH}" ]]; then
        log_error "설치에 사용할 모드 JAR를 찾을 수 없습니다: ${MOD_FILE_PATH}"
        exit 1
    fi
    
    # find 결과를 배열에 저장
    mapfile -t mod_dirs < <(find "$HOME" -maxdepth 2 -type d -name "mods")

    # 배열을 순회
    for mods_dir in "${mod_dirs[@]}"; do
        local dir
        dir=$(dirname "$mods_dir")
        MODPACK_NAME=$(basename "$dir")
        log_info "모드팩 발견: $MODPACK_NAME"

        # 호환성 체크: NeoForge 전용 설치
        IS_NEOFORGE=0
        if ls "$dir"/neoforge-*.jar >/dev/null 2>&1 || grep -Rqi "neoforge" "$dir/libraries" 2>/dev/null; then
            IS_NEOFORGE=1
        fi

        if [[ $IS_NEOFORGE -eq 0 ]]; then
            log_warning "NeoForge 모드팩이 아니므로 건너뜁니다: $MODPACK_NAME"
            continue
        fi
        
        # 모드 복사
        cp "${MOD_FILE_PATH}" "$mods_dir/"
        
        if ls "$mods_dir"/modpackai-*.jar >/dev/null 2>&1; then
            log_success "모드 설치 완료: $MODPACK_NAME"
            ((INSTALLED_COUNT++))
        else
            log_warning "모드 설치 실패: $MODPACK_NAME"
        fi
    done
    
    if [[ $INSTALLED_COUNT -eq 0 ]]; then
        log_warning "설치할 NeoForge 모드팩을 찾을 수 없습니다"
    else
        log_success "$INSTALLED_COUNT개 모드팩에 모드 ��치 완료"
    fi
}

# 백엔드 서비스 설정
setup_backend_service() {
    log_info "백엔드 서비스 설정 중..."
    
    BACKEND_DIR="$HOME/minecraft-ai-backend"
    
    if [[ ! -d "$BACKEND_DIR" ]]; then
        mkdir -p "$BACKEND_DIR"
    fi
    
    # 소스 파일 복사 (venv 제외)
    rsync -a --exclude 'venv' "backend/" "$BACKEND_DIR/"

    # 대상 경로에 venv 보장
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
        cp env.example "$ENV_FILE"
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
    
    sudo systemctl restart mc-ai-backend
    
    sleep 3
    if sudo systemctl is-active --quiet mc-ai-backend; then
        log_success "백엔드 서비스 시작됨"
    else
        log_warning "백엔드 서비스 시작 실패 - API 키를 설정 후 다시 시도하세요"
        sudo systemctl status mc-ai-backend || true
    fi
}

# 설치 검증
verify_installation() {
    log_info "설치 검증 중..."
    
    MOD_COUNT=$(find ~ -maxdepth 3 -type f -name "modpackai-*.jar" -path "*/mods/*" | wc -l)
    if [[ $MOD_COUNT -gt 0 ]]; then
        log_success "모드 설치 확인: $MOD_COUNT 개 모드팩"
    else
        log_warning "설치된 모드를 찾을 수 없음"
    fi
    
    if sudo systemctl is-active --quiet mc-ai-backend; then
        log_success "백엔드 서비스 실행 중"
        
        sleep 2
        if curl -s --fail http://localhost:5000/health > /dev/null; then
            log_success "API 연결 확인"
        else
            log_warning "API 연결 실패 - API 키 또는 백엔드 로그를 확인하세요"
        fi
    else
        log_warning "백엔드 서비스 중지됨"
    fi
}

# 사용법 안내
show_usage() {
    echo
    echo "🎮 ModpackAI 설치가 완료���었습니다!"
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
    echo "🚀 ModpackAI NeoForge 모드 설치 시작"
    echo

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