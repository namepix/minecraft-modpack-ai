#!/bin/bash

# 🔧 수동 하이브리드 서버 설치 스크립트
# install.sh에서 하이브리드 서버 다운로드 실패 시 사용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🔧 수동 하이브리드 서버 설치 스크립트"
echo "════════════════════════════════════════"
echo ""

# GCP VM 모드팩 정보
declare -A MODPACK_TYPES=(
    ["enigmatica_10"]="neoforge-1.21"
    ["enigmatica_9e"]="neoforge-1.20.1"
    ["enigmatica_6"]="forge-1.16.5"
    ["integrated_MC"]="forge-1.20.1"
    ["atm10"]="neoforge-1.21"
    ["beyond_depth"]="forge-1.20.1"
    ["carpg"]="neoforge-1.21"
    ["cteserver"]="forge-1.20.1"
    ["prominence_2"]="fabric-1.20.1"
    ["mnm"]="forge-1.16.5"
    ["test"]="neoforge-1.21"
)

# 임시 다운로드 디렉토리 생성
TEMP_DIR="$HOME/hybrid_downloads"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

log_info "임시 다운로드 디렉토리: $TEMP_DIR"

# 1. 모든 필요한 하이브리드 서버 다운로드
log_info "1. 하이브리드 서버 파일 다운로드 중..."

# NeoForge 1.21 (Youer/Arclight)
log_info "📥 NeoForge 1.21 하이브리드 서버 다운로드 중..."
if wget -q --show-progress -O "youer-neoforge-1.21.jar" "https://api.mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download"; then
    log_success "✅ Youer NeoForge 1.21 다운로드 성공"
elif wget -q --show-progress -O "youer-neoforge-1.21.jar" "https://github.com/IzzelAliz/Arclight/releases/download/1.21.1/arclight-neoforge-1.21.1.jar"; then
    log_success "✅ Arclight NeoForge 1.21 다운로드 성공"
else
    log_error "❌ NeoForge 1.21 다운로드 실패"
fi

# NeoForge 1.20.1 (Youer/Arclight)
log_info "📥 NeoForge 1.20.1 하이브리드 서버 다운로드 중..."
if wget -q --show-progress -O "youer-neoforge-1.20.1.jar" "https://api.mohistmc.com/api/v2/projects/youer/versions/1.20.1/builds/latest/download"; then
    log_success "✅ Youer NeoForge 1.20.1 다운로드 성공"
elif wget -q --show-progress -O "youer-neoforge-1.20.1.jar" "https://github.com/IzzelAliz/Arclight/releases/download/1.20.1/arclight-neoforge-1.20.1.jar"; then
    log_success "✅ Arclight NeoForge 1.20.1 다운로드 성공"
else
    log_error "❌ NeoForge 1.20.1 다운로드 실패"
fi

# Forge 1.20.1 (Mohist)
log_info "📥 Mohist 1.20.1 하이브리드 서버 다운로드 중..."
if wget -q --show-progress -O "mohist-1.20.1.jar" "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"; then
    log_success "✅ Mohist 1.20.1 다운로드 성공"
else
    log_error "❌ Mohist 1.20.1 다운로드 실패"
fi

# Forge 1.16.5 (Mohist)
log_info "📥 Mohist 1.16.5 하이브리드 서버 다운로드 중..."
if wget -q --show-progress -O "mohist-1.16.5.jar" "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"; then
    log_success "✅ Mohist 1.16.5 다운로드 성공"
else
    log_error "❌ Mohist 1.16.5 다운로드 실패"
fi

# Fabric 1.20.1 (CardBoard/Banner)
log_info "📥 Fabric 하이브리드 서버 다운로드 중..."
if wget -q --show-progress -O "cardboard.jar" "https://github.com/CardboardPowered/cardboard/releases/download/1.20.1-4.0.6/cardboard-1.20.1-4.0.6.jar"; then
    log_success "✅ CardBoard 다운로드 성공"
elif wget -q --show-progress -O "cardboard.jar" "https://github.com/Dueris/Banner/releases/latest/download/banner-1.20.1.jar"; then
    log_success "✅ Banner 다운로드 성공"
else
    log_error "❌ Fabric 하이브리드 서버 다운로드 실패"
fi

# 2. 각 모드팩에 적절한 하이브리드 서버 복사
log_info "2. 각 모드팩에 하이브리드 서버 설치 중..."

for modpack in "${!MODPACK_TYPES[@]}"; do
    modpack_type="${MODPACK_TYPES[$modpack]}"
    
    if [ -d "$HOME/$modpack" ]; then
        log_info "처리 중: $modpack ($modpack_type)"
        cd "$HOME/$modpack"
        
        case "$modpack_type" in
            "neoforge-1.21")
                if [ -f "$TEMP_DIR/youer-neoforge-1.21.jar" ] && [ $(stat -c%s "$TEMP_DIR/youer-neoforge-1.21.jar") -gt 1000 ]; then
                    cp "$TEMP_DIR/youer-neoforge-1.21.jar" "youer-neoforge.jar"
                    log_success "  ✅ NeoForge 1.21 하이브리드 설치 완료"
                else
                    log_warning "  ⚠️ NeoForge 1.21 파일이 없거나 손상됨"
                fi
                ;;
            "neoforge-1.20.1")
                if [ -f "$TEMP_DIR/youer-neoforge-1.20.1.jar" ] && [ $(stat -c%s "$TEMP_DIR/youer-neoforge-1.20.1.jar") -gt 1000 ]; then
                    cp "$TEMP_DIR/youer-neoforge-1.20.1.jar" "youer-neoforge.jar"
                    log_success "  ✅ NeoForge 1.20.1 하이브리드 설치 완료"
                else
                    log_warning "  ⚠️ NeoForge 1.20.1 파일이 없거나 손상됨"
                fi
                ;;
            "forge-1.20.1")
                if [ -f "$TEMP_DIR/mohist-1.20.1.jar" ] && [ $(stat -c%s "$TEMP_DIR/mohist-1.20.1.jar") -gt 1000 ]; then
                    cp "$TEMP_DIR/mohist-1.20.1.jar" "mohist-1.20.1.jar"
                    log_success "  ✅ Forge 1.20.1 하이브리드 설치 완료"
                else
                    log_warning "  ⚠️ Mohist 1.20.1 파일이 없거나 손상됨"
                fi
                ;;
            "forge-1.16.5")
                if [ -f "$TEMP_DIR/mohist-1.16.5.jar" ] && [ $(stat -c%s "$TEMP_DIR/mohist-1.16.5.jar") -gt 1000 ]; then
                    cp "$TEMP_DIR/mohist-1.16.5.jar" "mohist-1.16.5.jar"
                    log_success "  ✅ Forge 1.16.5 하이브리드 설치 완료"
                else
                    log_warning "  ⚠️ Mohist 1.16.5 파일이 없거나 손상됨"
                fi
                ;;
            "fabric-1.20.1")
                if [ -f "$TEMP_DIR/cardboard.jar" ] && [ $(stat -c%s "$TEMP_DIR/cardboard.jar") -gt 1000 ]; then
                    cp "$TEMP_DIR/cardboard.jar" "cardboard.jar"
                    log_success "  ✅ Fabric 하이브리드 설치 완료"
                else
                    log_warning "  ⚠️ CardBoard/Banner 파일이 없거나 손상됨"
                fi
                ;;
        esac
        
        # 시작 스크립트 권한 확인
        if [ -f "start_with_ai.sh" ]; then
            chmod +x start_with_ai.sh
        fi
    else
        log_warning "모드팩 디렉토리를 찾을 수 없습니다: $HOME/$modpack"
    fi
done

# 3. 정리
log_info "3. 임시 파일 정리 중..."
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 수동 하이브리드 서버 설치 완료!"
echo "════════════════════════════════════════"
echo ""
echo "📋 설치된 하이브리드 서버:"
echo "  🔧 NeoForge 모드팩들: youer-neoforge.jar (Youer/Arclight)"
echo "  🔧 Forge 모드팩들: mohist-*.jar (Mohist)"
echo "  🔧 Fabric 모드팩들: cardboard.jar (CardBoard/Banner)"
echo ""
echo "🚀 사용법:"
echo "  cd ~/enigmatica_10"
echo "  ./start_with_ai.sh"
echo ""
echo "⚠️ 주의사항:"
echo "  - AI 백엔드가 먼저 실행되어야 합니다: sudo systemctl start mc-ai-backend"
echo "  - 하이브리드 서버는 처음 실행 시 시간이 오래 걸릴 수 있습니다"
echo "  - 메모리 부족 시 start_with_ai.sh에서 -Xmx 값을 조정하세요"