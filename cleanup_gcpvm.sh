#!/bin/bash
# 🧹 GCP VM AI 프로젝트 파일 정리 스크립트
# 기존 모드팩 서버는 건드리지 않고 AI 프로젝트 관련 파일만 삭제

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🧹 AI 프로젝트 파일 정리 시작"
echo "════════════════════════════════════════"
echo ""

log_warning "⚠️ 주의: 이 스크립트는 AI 프로젝트 관련 파일만 삭제합니다"
log_info "기존 모드팩 서버 파일들은 건드리지 않습니다"
echo ""

# 1. AI 백엔드 및 환경 삭제
log_info "1. AI 백엔드 및 Python 환경 삭제"
if [ -d "$HOME/minecraft-ai-backend" ]; then
    log_info "minecraft-ai-backend 디렉토리 삭제 중..."
    rm -rf "$HOME/minecraft-ai-backend"
    log_success "✅ minecraft-ai-backend 삭제 완료"
fi

if [ -d "$HOME/minecraft-ai-env" ]; then
    log_info "minecraft-ai-env (Python 가상환경) 삭제 중..."
    rm -rf "$HOME/minecraft-ai-env"
    log_success "✅ minecraft-ai-env 삭제 완료"
fi

if [ -d "$HOME/minecraft-modpack-ai" ]; then
    log_info "minecraft-modpack-ai (Git 프로젝트) 삭제 중..."
    rm -rf "$HOME/minecraft-modpack-ai"
    log_success "✅ minecraft-modpack-ai 삭제 완료"
fi

# 2. 각 모드팩에서 AI 관련 파일만 삭제
log_info "2. 각 모드팩에서 AI 관련 파일 삭제"

MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e" 
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        log_info "처리 중: $modpack"
        cd "$HOME/$modpack"
        
        # plugins 디렉토리에서 AI 플러그인만 삭제
        if [ -d "plugins" ]; then
            # ModpackAI 플러그인 파일들만 삭제
            if [ -f "plugins/ModpackAI-1.0.jar" ]; then
                rm -f "plugins/ModpackAI-1.0.jar"
                log_info "  ✅ ModpackAI-1.0.jar 삭제"
            fi
            if [ -f "plugins/modpack-ai-plugin-1.0.0.jar" ]; then
                rm -f "plugins/modpack-ai-plugin-1.0.0.jar"
                log_info "  ✅ modpack-ai-plugin-1.0.0.jar 삭제"
            fi
            if [ -f "plugins/modpack-ai-plugin-1.0.0-shaded.jar" ]; then
                rm -f "plugins/modpack-ai-plugin-1.0.0-shaded.jar"
                log_info "  ✅ modpack-ai-plugin-1.0.0-shaded.jar 삭제"
            fi
            if [ -d "plugins/ModpackAI" ]; then
                rm -rf "plugins/ModpackAI"
                log_info "  ✅ ModpackAI 설정 디렉토리 삭제"
            fi
        fi
        
        # 하이브리드 서버 JAR 파일들 삭제
        if [ -f "youer-neoforge.jar" ]; then
            rm -f "youer-neoforge.jar"
            log_info "  ✅ youer-neoforge.jar 삭제"
        fi
        if [ -f "mohist-1.20.1.jar" ]; then
            rm -f "mohist-1.20.1.jar"
            log_info "  ✅ mohist-1.20.1.jar 삭제"
        fi
        if [ -f "mohist-1.16.5.jar" ]; then
            rm -f "mohist-1.16.5.jar"
            log_info "  ✅ mohist-1.16.5.jar 삭제"
        fi
        if [ -f "cardboard.jar" ]; then
            rm -f "cardboard.jar"
            log_info "  ✅ cardboard.jar 삭제"
        fi
        if [ -f "cardboard-1.20.1.jar" ]; then
            rm -f "cardboard-1.20.1.jar"
            log_info "  ✅ cardboard-1.20.1.jar 삭제"
        fi
        if [ -f "arclight-neoforge.jar" ]; then
            rm -f "arclight-neoforge.jar"
            log_info "  ✅ arclight-neoforge.jar 삭제"
        fi
        
        # AI 지원 시작 스크립트 삭제
        if [ -f "start_with_ai.sh" ]; then
            rm -f "start_with_ai.sh"
            log_info "  ✅ start_with_ai.sh 삭제"
        fi
        
        # 백업된 시작 스크립트 복원
        if [ -f "start.sh.backup" ]; then
            if [ -f "start.sh" ]; then
                # 현재 start.sh가 AI 버전인지 확인
                if grep -q "AI Assistant" "start.sh" 2>/dev/null; then
                    cp "start.sh.backup" "start.sh"
                    log_info "  ✅ 원본 start.sh 복원"
                fi
            fi
            rm -f "start.sh.backup"
            log_info "  ✅ start.sh.backup 삭제"
        fi
        
        log_success "  모드팩 '$modpack' 정리 완료"
    fi
done

# 3. systemd 서비스 제거
log_info "3. systemd 서비스 제거"
if systemctl is-enabled mc-ai-backend >/dev/null 2>&1; then
    sudo systemctl stop mc-ai-backend 2>/dev/null || true
    sudo systemctl disable mc-ai-backend 2>/dev/null || true
    log_info "mc-ai-backend 서비스 중지 및 비활성화"
fi

if [ -f "/etc/systemd/system/mc-ai-backend.service" ]; then
    sudo rm -f "/etc/systemd/system/mc-ai-backend.service"
    sudo systemctl daemon-reload
    log_success "✅ mc-ai-backend.service 삭제 완료"
fi

# 4. 전역 관리 스크립트 제거
log_info "4. 전역 관리 스크립트 제거"
if [ -f "/usr/local/bin/modpack_switch" ]; then
    sudo rm -f "/usr/local/bin/modpack_switch"
    log_success "✅ modpack_switch 스크립트 삭제"
fi

if [ -f "/usr/local/bin/mc-ai-monitor" ]; then
    sudo rm -f "/usr/local/bin/mc-ai-monitor"
    log_success "✅ mc-ai-monitor 스크립트 삭제"
fi

# 5. mcrcon 제거 (AI 프로젝트에서 설치했다면)
if [ -d "$HOME/mcrcon" ]; then
    log_info "5. mcrcon 디렉토리 삭제 (AI 프로젝트에서 설치된 경우)"
    read -p "mcrcon을 삭제하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/mcrcon"
        log_success "✅ mcrcon 삭제 완료"
    else
        log_info "mcrcon 보존"
    fi
fi

echo ""
echo "🎉 AI 프로젝트 파일 정리 완료!"
echo "════════════════════════════════════════"
echo ""
echo "📊 정리 요약:"
echo "  ✅ AI 백엔드 및 Python 환경 삭제"
echo "  ✅ Git 프로젝트 디렉토리 삭제" 
echo "  ✅ 모든 모드팩의 AI 플러그인 및 하이브리드 서버 삭제"
echo "  ✅ systemd 서비스 제거"
echo "  ✅ 전역 관리 스크립트 제거"
echo ""
echo "✅ 기존 모드팩 서버는 그대로 보존됨"
echo "✅ 이제 새로운 설치를 진행할 수 있습니다"
echo ""
echo "🚀 다음 단계:"
echo "  1. git clone https://github.com/YOUR_REPO/minecraft-modpack-ai.git"
echo "  2. cd minecraft-modpack-ai"
echo "  3. ./install.sh"