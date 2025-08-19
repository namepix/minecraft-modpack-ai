#!/bin/bash

# 🎯 ModpackAI 모드팩별 자동 선택 및 설치 스크립트
# 모드팩 이름을 입력하면 올바른 JAR 파일을 자동으로 선택합니다

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${CYAN}🎯 ModpackAI 모드팩 선택기${NC}"
echo "================================="

# 모드팩 데이터베이스 (확장 가능)
declare -A MODPACK_DB=(
    # 모드팩명:플랫폼:Java버전:Minecraft버전
    ["enigmatica_10"]="neoforge:21:1.21.1"
    ["prominence_2"]="fabric:17:1.20.1"
    ["all_the_mods_9"]="neoforge:21:1.21.1"
    ["vault_hunters"]="fabric:17:1.20.1"
    ["create_above_and_beyond"]="fabric:17:1.20.1"
    ["better_minecraft"]="fabric:17:1.20.1"
    ["ftb_skies"]="fabric:17:1.20.1"
    ["gregtech_new_horizons"]="fabric:17:1.12.2"
    ["sevtech_ages"]="fabric:17:1.12.2"
)

# 사용법 출력
show_usage() {
    echo ""
    echo "사용법: $0 <모드팩명> [모드팩폴더경로]"
    echo ""
    echo "지원하는 모드팩:"
    echo "=================="
    for modpack in "${!MODPACK_DB[@]}"; do
        IFS=':' read -r platform java_ver mc_ver <<< "${MODPACK_DB[$modpack]}"
        printf "%-25s %s (Java %s, MC %s)\n" "$modpack" "$platform" "$java_ver" "$mc_ver"
    done
    echo ""
    echo "예시:"
    echo "  $0 prominence_2"
    echo "  $0 enigmatica_10 /opt/minecraft/enigmatica"
    echo ""
}

# 인자 확인
if [ $# -eq 0 ]; then
    log_error "모드팩명을 입력하세요."
    show_usage
    exit 1
fi

MODPACK_NAME="$1"
MODPACK_DIR="${2:-}"

# 모드팩 정보 확인
if [[ ! -v MODPACK_DB["$MODPACK_NAME"] ]]; then
    log_error "지원하지 않는 모드팩입니다: $MODPACK_NAME"
    show_usage
    exit 1
fi

# 모드팩 정보 파싱
IFS=':' read -r PLATFORM JAVA_VER MC_VER <<< "${MODPACK_DB[$MODPACK_NAME]}"

log_info "모드팩 정보:"
echo "  📦 모드팩: $MODPACK_NAME"
echo "  🔧 플랫폼: $PLATFORM"
echo "  ☕ Java: $JAVA_VER"
echo "  🎮 Minecraft: $MC_VER"
echo ""

# JAR 파일명 결정
JAR_NAME="modpackai-${PLATFORM}-java${JAVA_VER}-1.0.0.jar"
BUILD_OUTPUT_DIR="build_output"

# JAR 파일 존재 확인
if [ ! -f "$BUILD_OUTPUT_DIR/$JAR_NAME" ]; then
    log_error "필요한 JAR 파일을 찾을 수 없습니다: $JAR_NAME"
    log_info "먼저 다음 명령어로 빌드하세요:"
    echo "  ./build_all_mods_multi_java.sh"
    exit 1
fi

log_success "적합한 JAR 파일 발견: $JAR_NAME"

# 모드팩 디렉토리 자동 감지 또는 사용자 입력
if [ -z "$MODPACK_DIR" ]; then
    echo ""
    log_info "모드팩 디렉토리를 자동으로 찾는 중..."
    
    # 일반적인 모드팩 설치 경로들
    SEARCH_PATHS=(
        "$HOME/minecraft"
        "$HOME/minecraft-servers"
        "$HOME/${MODPACK_NAME}"
        "/opt/minecraft"
        "/opt/minecraft/${MODPACK_NAME}"
        "$HOME/Documents/Curse/Minecraft/Instances/${MODPACK_NAME}"
        "$HOME/.minecraft/versions/${MODPACK_NAME}"
    )
    
    FOUND_DIRS=()
    for path in "${SEARCH_PATHS[@]}"; do
        if [ -d "$path" ] && [ -d "$path/mods" ]; then
            FOUND_DIRS+=("$path")
        fi
    done
    
    if [ ${#FOUND_DIRS[@]} -eq 0 ]; then
        log_warning "모드팩 디렉토리를 자동으로 찾을 수 없습니다."
        echo ""
        read -p "모드팩 설치 경로를 입력하세요: " MODPACK_DIR
        
        if [ ! -d "$MODPACK_DIR" ]; then
            log_error "존재하지 않는 디렉토리입니다: $MODPACK_DIR"
            exit 1
        fi
    elif [ ${#FOUND_DIRS[@]} -eq 1 ]; then
        MODPACK_DIR="${FOUND_DIRS[0]}"
        log_success "모드팩 디렉토리 자동 감지: $MODPACK_DIR"
    else
        echo ""
        log_info "여러 후보 디렉토리를 발견했습니다:"
        for i in "${!FOUND_DIRS[@]}"; do
            echo "  $((i+1)). ${FOUND_DIRS[$i]}"
        done
        echo ""
        read -p "번호를 선택하세요 (1-${#FOUND_DIRS[@]}): " selection
        
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le ${#FOUND_DIRS[@]} ]; then
            MODPACK_DIR="${FOUND_DIRS[$((selection-1))]}"
            log_success "선택된 디렉토리: $MODPACK_DIR"
        else
            log_error "잘못된 선택입니다."
            exit 1
        fi
    fi
fi

# mods 디렉토리 확인
MODS_DIR="$MODPACK_DIR/mods"
if [ ! -d "$MODS_DIR" ]; then
    log_error "mods 디렉토리를 찾을 수 없습니다: $MODS_DIR"
    exit 1
fi

log_info "설치 대상 디렉토리: $MODS_DIR"

# 기존 ModpackAI JAR 파일 제거
echo ""
log_info "기존 ModpackAI 파일 확인 중..."
OLD_JARS=$(find "$MODS_DIR" -name "modpackai*.jar" 2>/dev/null || true)

if [ -n "$OLD_JARS" ]; then
    log_warning "기존 ModpackAI 파일 발견:"
    echo "$OLD_JARS"
    echo ""
    read -p "기존 파일을 제거하고 계속하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$OLD_JARS" | while read -r jar; do
            rm -f "$jar"
            log_success "제거됨: $(basename "$jar")"
        done
    else
        log_info "설치를 취소했습니다."
        exit 0
    fi
fi

# 새 JAR 파일 복사
echo ""
log_info "ModpackAI 설치 중..."
cp "$BUILD_OUTPUT_DIR/$JAR_NAME" "$MODS_DIR/"

if [ $? -eq 0 ]; then
    log_success "설치 완료!"
    echo ""
    echo "📋 설치 정보:"
    echo "  ✅ 파일: $JAR_NAME"
    echo "  📂 위치: $MODS_DIR"
    echo "  📊 크기: $(ls -lh "$MODS_DIR/$JAR_NAME" | awk '{print $5}')"
    echo ""
    echo "🚀 다음 단계:"
    echo "  1. 모드팩 서버를 재시작하세요"
    echo "  2. 게임에서 '/ai 안녕' 명령어로 테스트하세요"
    echo "  3. '/modpackai help' 명령어로 사용법을 확인하세요"
else
    log_error "설치에 실패했습니다."
    exit 1
fi