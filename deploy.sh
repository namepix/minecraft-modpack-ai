#!/bin/bash
# 🚀 마인크래프트 AI 시스템 GCP VM 배포 스크립트
# 로컬 개발 환경에서 GCP VM으로 배포하는 스크립트

set -e  # 오류 시 스크립트 중단

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 설정 파일에서 값 읽기
if [ -f "deploy.config" ]; then
    source deploy.config
else
    log_error "deploy.config 파일이 없습니다. 먼저 deploy.config 파일을 생성하세요."
    exit 1
fi

# 필수 변수 확인
required_vars=("GCP_VM_IP" "GCP_VM_USER" "GCP_VM_PROJECT_PATH" "SSH_KEY_PATH")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "필수 환경변수 $var가 설정되지 않았습니다."
        exit 1
    fi
done

log_info "🚀 마인크래프트 AI 시스템 배포 시작"
log_info "대상 서버: $GCP_VM_USER@$GCP_VM_IP"
log_info "프로젝트 경로: $GCP_VM_PROJECT_PATH"

# SSH 연결 테스트
log_info "SSH 연결 테스트 중..."
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 "$GCP_VM_USER@$GCP_VM_IP" "echo 'SSH 연결 성공'" > /dev/null 2>&1; then
    log_error "SSH 연결에 실패했습니다. SSH 키와 IP 주소를 확인하세요."
    exit 1
fi
log_success "SSH 연결 성공"

# 로컬 파일 변경사항 확인
log_info "로컬 파일 변경사항 확인 중..."
if git status --porcelain | grep -q .; then
    log_warning "커밋되지 않은 변경사항이 있습니다:"
    git status --short
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "배포를 취소했습니다."
        exit 0
    fi
fi

# 빌드 및 테스트
log_info "Java 플러그인 빌드 중..."
cd minecraft_plugin
if ! mvn clean package -q; then
    log_error "Maven 빌드에 실패했습니다."
    exit 1
fi
log_success "Java 플러그인 빌드 완료"
cd ..

# Python 백엔드 테스트
log_info "Python 백엔드 테스트 중..."
cd backend
if command -v python3 &> /dev/null; then
    python3 -m py_compile app.py
    if [ -f "tests/test_app_integration.py" ]; then
        python3 -m pytest tests/test_app_integration.py -v --tb=short
    fi
else
    log_warning "Python3가 설치되지 않아 테스트를 건너뜁니다."
fi
log_success "백엔드 테스트 완료"
cd ..

# 파일 압축 및 업로드
log_info "프로젝트 파일 압축 중..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="mc_ai_${TIMESTAMP}.tar.gz"

# 제외할 파일/디렉토리 목록
EXCLUDE_PATTERNS=(
    "--exclude=.git" 
    "--exclude=.idea" 
    "--exclude=*.log" 
    "--exclude=__pycache__" 
    "--exclude=node_modules"
    "--exclude=target/*.jar"
    "--exclude=*.pyc"
    "--exclude=.env.local"
    "--exclude=deploy.config"
)

tar czf "$ARCHIVE_NAME" "${EXCLUDE_PATTERNS[@]}" .
log_success "압축 완료: $ARCHIVE_NAME"

# GCP VM에 업로드
log_info "GCP VM에 파일 업로드 중..."
scp -i "$SSH_KEY_PATH" "$ARCHIVE_NAME" "$GCP_VM_USER@$GCP_VM_IP:/tmp/"
rm "$ARCHIVE_NAME"  # 로컬 압축 파일 삭제
log_success "파일 업로드 완료"

# GCP VM에서 배포 실행
log_info "GCP VM에서 배포 스크립트 실행 중..."
ssh -i "$SSH_KEY_PATH" "$GCP_VM_USER@$GCP_VM_IP" bash << EOF
set -e

# 색상 코드 (원격에서도 사용)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "\${BLUE}[INFO]\${NC} \$1"; }
log_success() { echo -e "\${GREEN}[SUCCESS]\${NC} \$1"; }
log_warning() { echo -e "\${YELLOW}[WARNING]\${NC} \$1"; }
log_error() { echo -e "\${RED}[ERROR]\${NC} \$1"; }

log_info "GCP VM에서 배포 프로세스 시작"

# 백업 디렉토리 생성
BACKUP_DIR="\$HOME/mc_ai_backups"
mkdir -p "\$BACKUP_DIR"

# 기존 프로젝트 백업 (있는 경우)
if [ -d "$GCP_VM_PROJECT_PATH" ]; then
    log_info "기존 프로젝트 백업 중..."
    BACKUP_NAME="backup_\$(date +%Y%m%d_%H%M%S)"
    cp -r "$GCP_VM_PROJECT_PATH" "\$BACKUP_DIR/\$BACKUP_NAME"
    log_success "백업 완료: \$BACKUP_DIR/\$BACKUP_NAME"
fi

# 프로젝트 디렉토리 생성
mkdir -p "$GCP_VM_PROJECT_PATH"
cd "$GCP_VM_PROJECT_PATH"

# 기존 파일 정리 (중요한 설정 파일은 보존)
if [ -f ".env" ]; then
    cp .env /tmp/.env.backup
    log_info ".env 파일 백업됨"
fi

# 새 파일 압축 해제
log_info "새 파일 압축 해제 중..."
tar xzf "/tmp/$ARCHIVE_NAME"
rm "/tmp/$ARCHIVE_NAME"

# .env 파일 복원
if [ -f "/tmp/.env.backup" ]; then
    cp /tmp/.env.backup backend/.env
    rm /tmp/.env.backup
    log_success ".env 파일 복원됨"
fi

# Python 가상환경 설정 및 의존성 설치
log_info "Python 백엔드 환경 설정 중..."
cd backend

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Python 가상환경 생성됨"
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
log_success "Python 의존성 설치 완료"

# Java 플러그인 빌드 및 배포
log_info "Java 플러그인 배포 중..."
cd ../minecraft_plugin

# Maven이 설치되어 있는지 확인
if ! command -v mvn &> /dev/null; then
    log_error "Maven이 설치되지 않았습니다."
    exit 1
fi

# 플러그인 빌드
mvn clean package -q
if [ \$? -eq 0 ]; then
    log_success "플러그인 빌드 성공"
    
    # 플러그인 파일을 마인크래프트 서버 디렉토리로 복사 (경로가 설정된 경우)
    PLUGIN_FILE="target/modpack-ai-plugin-1.0.0.jar"
    if [ -f "\$PLUGIN_FILE" ] && [ -n "${MC_SERVER_PLUGINS_DIR:-}" ]; then
        cp "\$PLUGIN_FILE" "${MC_SERVER_PLUGINS_DIR}/"
        log_success "플러그인이 마인크래프트 서버에 배포됨"
    fi
else
    log_error "플러그인 빌드에 실패했습니다."
fi

# systemd 서비스 설정
log_info "systemd 서비스 설정 중..."
cd "$GCP_VM_PROJECT_PATH"

# 서비스 파일 생성
sudo tee /etc/systemd/system/mc-ai-backend.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Minecraft AI Backend Service
After=network.target

[Service]
Type=simple
User=$GCP_VM_USER
WorkingDirectory=$GCP_VM_PROJECT_PATH/backend
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
ExecStart=$GCP_VM_PROJECT_PATH/backend/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# systemd 다시 로드 및 서비스 시작
sudo systemctl daemon-reload
sudo systemctl enable mc-ai-backend
sudo systemctl restart mc-ai-backend

# 서비스 상태 확인
sleep 5
if sudo systemctl is-active --quiet mc-ai-backend; then
    log_success "백엔드 서비스가 성공적으로 시작되었습니다."
else
    log_error "백엔드 서비스 시작에 실패했습니다."
    sudo systemctl status mc-ai-backend --no-pager -l
fi

log_success "🎉 배포 완료!"
log_info "서비스 상태 확인: sudo systemctl status mc-ai-backend"
log_info "로그 확인: sudo journalctl -u mc-ai-backend -f"
log_info "API 테스트: curl http://localhost:5000/health"

EOF

if [ $? -eq 0 ]; then
    log_success "🎉 GCP VM 배포 완료!"
    log_info "다음 명령어로 상태를 확인할 수 있습니다:"
    echo "  ssh -i $SSH_KEY_PATH $GCP_VM_USER@$GCP_VM_IP"
    echo "  sudo systemctl status mc-ai-backend"
    echo "  curl http://$GCP_VM_IP:5000/health"
else
    log_error "배포 중 오류가 발생했습니다."
    exit 1
fi