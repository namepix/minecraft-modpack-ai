#!/bin/bash

# 마인크래프트 모드팩 AI 시스템 설치 스크립트
# GCP VM Debian 환경용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 시스템 정보 확인
log_info "시스템 정보 확인 중..."
OS=$(lsb_release -si)
VERSION=$(lsb_release -sr)

if [ "$OS" != "Debian" ] && [ "$OS" != "Ubuntu" ]; then
    log_error "이 스크립트는 Debian/Ubuntu 시스템에서만 실행됩니다."
    exit 1
fi

log_success "운영체제: $OS $VERSION"

# 1. 시스템 업데이트
log_info "시스템 패키지 업데이트 중..."
sudo apt update
sudo apt upgrade -y

# 2. 필수 패키지 설치
log_info "필수 패키지 설치 중..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    java-11-openjdk \
    maven \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev \
    python3-dev

# 3. 백엔드 디렉토리 생성
log_info "백엔드 디렉토리 설정 중..."
sudo mkdir -p /opt/mc_ai_backend
sudo mkdir -p /opt/mc_ai_backend/logs
sudo mkdir -p /opt/mc_ai_backend/uploads
sudo mkdir -p /opt/mc_ai_backend/backups
sudo mkdir -p /tmp/modpacks

# 4. 사용자 권한 설정
sudo chown -R $USER:$USER /opt/mc_ai_backend
sudo chown -R $USER:$USER /tmp/modpacks
sudo chmod 755 /opt/mc_ai_backend
sudo chmod 755 /tmp/modpacks

# 5. Python 가상환경 생성
log_info "Python 가상환경 생성 중..."
cd /opt/mc_ai_backend
python3 -m venv /opt/mc_ai_env
source /opt/mc_ai_env/bin/activate

# 6. Python 패키지 설치
log_info "Python 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 7. 환경 변수 파일 설정
log_info "환경 변수 파일 설정 중..."
if [ ! -f /opt/mc_ai_backend/.env ]; then
    cp env.example /opt/mc_ai_backend/.env
    log_warning "환경 변수 파일이 생성되었습니다. API 키를 설정해주세요:"
    log_info "nano /opt/mc_ai_backend/.env"
fi

# 8. 모드팩 스위치 스크립트 설치
log_info "모드팩 스위치 스크립트 설치 중..."
sudo cp modpack_switch.sh /usr/local/bin/modpack_switch
sudo chmod +x /usr/local/bin/modpack_switch
sudo chown $USER:$USER /usr/local/bin/modpack_switch

# 9. systemd 서비스 설정
log_info "systemd 서비스 설정 중..."
sudo tee /etc/systemd/system/mc-ai-backend.service > /dev/null <<EOF
[Unit]
Description=Minecraft Modpack AI Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mc_ai_backend
Environment=PATH=/opt/mc_ai_env/bin
ExecStart=/opt/mc_ai_env/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 10. 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable mc-ai-backend

# 11. Minecraft 플러그인 빌드
log_info "Minecraft 플러그인 빌드 중..."
cd minecraft_plugin
mvn clean package
sudo mkdir -p /opt/minecraft/plugins
sudo cp target/ModpackAI-1.0.jar /opt/minecraft/plugins/
sudo chown -R $USER:$USER /opt/minecraft

# 12. 방화벽 설정
log_info "방화벽 설정 중..."
sudo ufw allow 25565/tcp  # Minecraft 서버
sudo ufw allow 5000/tcp   # AI 백엔드
sudo ufw --force enable

# 13. 모니터링 스크립트 설치
log_info "모니터링 스크립트 설치 중..."
sudo cp monitor.sh /usr/local/bin/mc-ai-monitor
sudo chmod +x /usr/local/bin/mc-ai-monitor
sudo chown $USER:$USER /usr/local/bin/mc-ai-monitor

# 14. 업데이트 스크립트 설치
log_info "업데이트 스크립트 설치 중..."
sudo cp update.sh /usr/local/bin/mc-ai-update
sudo chmod +x /usr/local/bin/mc-ai-update
sudo chown $USER:$USER /usr/local/bin/mc-ai-update

# 15. 설치 완료 메시지
log_success "설치가 완료되었습니다!"
echo ""
echo "🎉 마인크래프트 모드팩 AI 시스템 설치 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. API 키 설정:"
echo "   nano /opt/mc_ai_backend/.env"
echo ""
echo "2. 백엔드 서비스 시작:"
echo "   sudo systemctl start mc-ai-backend"
echo ""
echo "3. 서비스 상태 확인:"
echo "   sudo systemctl status mc-ai-backend"
echo ""
echo "4. 모드팩 변경 테스트:"
echo "   modpack_switch --help"
echo ""
echo "5. 모니터링:"
echo "   mc-ai-monitor"
echo ""
echo "📚 문서:"
echo "- README.md: 기본 사용법"
echo "- DEPLOYMENT_GUIDE.md: 상세 배포 가이드"
echo "- GAME_COMMANDS.md: 게임 내 명령어"
echo "- MODPACK_SWITCH_GUIDE.md: 모드팩 변경 가이드"
echo ""
echo "🚀 즐거운 모드팩 플레이 되세요!" 