#!/bin/bash
# 🔄 마인크래프트 AI 시스템 업데이트 스크립트
# 로컬에서 수정한 내용을 GCP VM에 빠르게 반영하는 스크립트

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

# 업데이트 타입 확인
UPDATE_TYPE=${1:-"all"}

case $UPDATE_TYPE in
    "backend"|"b")
        log_info "🐍 백엔드만 업데이트합니다..."
        UPDATE_BACKEND=true
        UPDATE_PLUGIN=false
        ;;
    "plugin"|"p")
        log_info "☕ 플러그인만 업데이트합니다..."
        UPDATE_BACKEND=false
        UPDATE_PLUGIN=true
        ;;
    "all"|"a")
        log_info "🚀 전체 업데이트를 진행합니다..."
        UPDATE_BACKEND=true
        UPDATE_PLUGIN=true
        ;;
    *)
        log_error "사용법: $0 [backend|plugin|all]"
        echo "  backend (b): 백엔드만 업데이트"
        echo "  plugin (p): 플러그인만 업데이트"  
        echo "  all (a): 전체 업데이트 (기본값)"
        exit 1
        ;;
esac

# SSH 연결 테스트
log_info "SSH 연결 테스트 중..."
if ! ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 "$GCP_VM_USER@$GCP_VM_IP" "echo 'SSH 연결 성공'" > /dev/null 2>&1; then
    log_error "SSH 연결 실패"
    exit 1
fi

# Git 상태 확인
log_info "Git 상태 확인 중..."
if git status --porcelain | grep -q .; then
    log_warning "커밋되지 않은 변경사항:"
    git status --short
fi

# 로컬 테스트 (배포 전)
if [ "$UPDATE_BACKEND" = true ]; then
    log_info "🧪 로컬 테스트 실행 중..."
    cd backend
    
    # 빠른 단위 테스트 (API 키 불필요)
    if command -v python3 &> /dev/null; then
        python3 -m pytest tests/test_language_mapper.py tests/test_utils.py -q --tb=short
        if [ $? -ne 0 ]; then
            log_error "로컬 테스트 실패 - 배포를 중단합니다."
            exit 1
        fi
        log_success "로컬 테스트 통과"
    fi
    cd ..
fi

# 백엔드 업데이트
if [ "$UPDATE_BACKEND" = true ]; then
    log_info "🐍 백엔드 코드 업데이트 중..."
    
    # 백엔드 파일만 압축
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKEND_ARCHIVE="backend_${TIMESTAMP}.tar.gz"
    
    tar czf "$BACKEND_ARCHIVE" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude="venv" \
        --exclude=".env" \
        backend/
    
    # 업로드
    scp -i "$SSH_KEY_PATH" "$BACKEND_ARCHIVE" "$GCP_VM_USER@$GCP_VM_IP:/tmp/"
    rm "$BACKEND_ARCHIVE"
    
    # 원격 업데이트 및 테스트 실행
    ssh -i "$SSH_KEY_PATH" "$GCP_VM_USER@$GCP_VM_IP" "
        cd $GCP_VM_PROJECT_PATH &&
        sudo systemctl stop mc-ai-backend &&
        tar xzf /tmp/backend_*.tar.gz &&
        rm /tmp/backend_*.tar.gz &&
        cd backend && source venv/bin/activate && pip install -r requirements.txt &&
        
        # 🧪 원격 테스트 (API 키 필요한 테스트들)
        echo '🧪 원격 환경에서 통합 테스트 실행 중...' &&
        python -m pytest tests/test_app_integration.py -q --tb=short &&
        
        sudo systemctl start mc-ai-backend &&
        sleep 5 &&
        
        # 🌐 API 응답 테스트
        curl -f http://localhost:5000/health > /dev/null &&
        echo '✅ API 응답 테스트 통과'
    "
    
    if [ $? -eq 0 ]; then
        log_success "백엔드 업데이트 및 테스트 완료"
    else
        log_error "백엔드 배포 또는 테스트 실패"
        exit 1
    fi
fi

# 플러그인 업데이트  
if [ "$UPDATE_PLUGIN" = true ]; then
    log_info "☕ 플러그인 업데이트 중..."
    
    # 플러그인 빌드
    cd minecraft_plugin
    if ! mvn clean package -q; then
        log_error "Maven 빌드 실패"
        exit 1
    fi
    cd ..
    
    log_success "플러그인 업데이트 완료"
fi

log_success "🎉 업데이트 완료!" 