#!/bin/bash
# ModpackAI 통합 설치 스크립트 (NeoForge + Fabric 지원)

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
BUILT_NEOFORGE_MOD=""
BUILT_FABRIC_MOD=""
MODLOADER_TYPE=""

# 도움말 표시
show_help() {
    echo "ModpackAI 통합 설치 스크립트 (NeoForge + Fabric 지원)"
    echo ""
    echo "사용법:"
    echo "  $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --modloader TYPE    설치할 모드로더 지정 (neoforge|fabric|both)"
    echo "  --help             이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 --modloader neoforge    # NeoForge만 설치"
    echo "  $0 --modloader fabric      # Fabric만 설치"
    echo "  $0 --modloader both        # 두 모드로더 모두 설치"
    echo "  $0                         # 자동 감지 및 설치"
}

# 모드로더 감지
detect_modloaders() {
    log_info "모드로더 자동 감지 중..."
    
    local neoforge_count=0
    local fabric_count=0
    
    # 홈 디렉토리에서 모드팩 검색
    for dir in "$HOME"/*/; do
        if [ -d "$dir" ]; then
            # NeoForge 감지 (neoforge 또는 neoforged JAR 파일)
            if find "$dir" -name "*neoforge*.jar" -o -name "*neoforged*.jar" | grep -q .; then
                neoforge_count=$((neoforge_count + 1))
                log_info "NeoForge 모드팩 발견: $(basename "$dir")"
            fi
            
            # Fabric 감지 (fabric-server-launcher.jar 또는 fabric-loader)
            if find "$dir" -name "*fabric*loader*.jar" -o -name "*fabric*server*.jar" | grep -q .; then
                fabric_count=$((fabric_count + 1))
                log_info "Fabric 모드팩 발견: $(basename "$dir")"
            fi
        fi
    done
    
    log_info "감지된 모드팩: NeoForge $neoforge_count개, Fabric $fabric_count개"
    
    # 자동 선택 로직
    if [ $neoforge_count -gt 0 ] && [ $fabric_count -gt 0 ]; then
        MODLOADER_TYPE="both"
        log_info "양쪽 모드로더 모두 설치합니다"
    elif [ $neoforge_count -gt 0 ]; then
        MODLOADER_TYPE="neoforge"
        log_info "NeoForge 모드만 설치합니다"
    elif [ $fabric_count -gt 0 ]; then
        MODLOADER_TYPE="fabric"
        log_info "Fabric 모드만 설치합니다"
    else
        log_warning "모드팩을 찾을 수 없습니다. 양쪽 모두 설치합니다"
        MODLOADER_TYPE="both"
    fi
}

# 시스템 요구사항 확인
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
    
    # Python 3.9+ 확인
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        log_success "Python $PYTHON_VERSION 확인됨"
    else
        log_warning "Python3가 설치되지 않음. 백엔드 설정이 필요할 수 있습니다."
    fi
    
    # Git 확인
    if ! command -v git &> /dev/null; then
        log_error "Git이 설치되지 않음"
        exit 1
    fi
}

# 모드 빌드
build_mods() {
    log_info "모드 빌드 시작..."
    
    case $MODLOADER_TYPE in
        "neoforge")
            build_neoforge_mod
            ;;
        "fabric")
            build_fabric_mod
            ;;
        "both")
            build_neoforge_mod
            build_fabric_mod
            ;;
        *)
            log_error "알 수 없는 모드로더: $MODLOADER_TYPE"
            exit 1
            ;;
    esac
}

# NeoForge 모드 빌드
build_neoforge_mod() {
    log_info "NeoForge 모드 빌드 중..."
    
    if [ ! -d "minecraft_mod" ]; then
        log_error "minecraft_mod 디렉토리를 찾을 수 없습니다"
        exit 1
    fi
    
    cd minecraft_mod
    
    # Gradle wrapper 생성/확인
    if [ ! -f "gradlew" ]; then
        log_info "Gradle wrapper 생성 중..."
        gradle wrapper --gradle-version 8.8 --distribution-type all
    fi
    
    # 빌드
    log_info "NeoForge 모드 컴파일 중..."
    ./gradlew clean build
    
    # 빌드 결과 확인
    if [ -f "build/libs/modpackai-1.0.0.jar" ]; then
        BUILT_NEOFORGE_MOD="$(pwd)/build/libs/modpackai-1.0.0.jar"
        log_success "NeoForge 모드 빌드 성공: $BUILT_NEOFORGE_MOD"
    else
        log_error "NeoForge 모드 빌드 실패"
        exit 1
    fi
    
    cd ..
}

# Fabric 모드 빌드
build_fabric_mod() {
    log_info "Fabric 모드 빌드 중..."
    
    if [ ! -d "minecraft_fabric_mod" ]; then
        log_error "minecraft_fabric_mod 디렉토리를 찾을 수 없습니다"
        exit 1
    fi
    
    cd minecraft_fabric_mod
    
    # Gradle wrapper 생성/확인
    if [ ! -f "gradlew" ]; then
        log_info "Gradle wrapper 생성 중..."
        gradle wrapper --gradle-version 8.8 --distribution-type all
    fi
    
    # 빌드
    log_info "Fabric 모드 컴파일 중..."
    ./gradlew clean build
    
    # 빌드 결과 확인
    if [ -f "build/libs/modpackai-fabric-1.0.0.jar" ]; then
        BUILT_FABRIC_MOD="$(pwd)/build/libs/modpackai-fabric-1.0.0.jar"
        log_success "Fabric 모드 빌드 성공: $BUILT_FABRIC_MOD"
    else
        log_error "Fabric 모드 빌드 실패"
        exit 1
    fi
    
    cd ..
}

# 모드 설치
install_mods() {
    log_info "모드 설치 시작..."
    
    case $MODLOADER_TYPE in
        "neoforge")
            install_neoforge_mods
            ;;
        "fabric")
            install_fabric_mods
            ;;
        "both")
            install_neoforge_mods
            install_fabric_mods
            ;;
    esac
}

# NeoForge 모드팩에 설치
install_neoforge_mods() {
    log_info "NeoForge 모드팩 검색 및 설치..."
    
    local installed=0
    
    for modpack_dir in "$HOME"/*/; do
        if [ -d "$modpack_dir" ]; then
            # NeoForge 모드팩인지 확인
            if find "$modpack_dir" -name "*neoforge*.jar" -o -name "*neoforged*.jar" | grep -q .; then
                local mods_dir="$modpack_dir/mods"
                
                if [ -d "$mods_dir" ]; then
                    local modpack_name=$(basename "$modpack_dir")
                    log_info "NeoForge 모드팩에 설치: $modpack_name"
                    
                    # 기존 모드 제거
                    find "$mods_dir" -name "modpackai*.jar" -delete 2>/dev/null || true
                    
                    # 새 모드 설치
                    cp "$BUILT_NEOFORGE_MOD" "$mods_dir/"
                    log_success "설치됨: $mods_dir/$(basename "$BUILT_NEOFORGE_MOD")"
                    installed=$((installed + 1))
                fi
            fi
        fi
    done
    
    if [ $installed -eq 0 ]; then
        log_warning "NeoForge 모드팩을 찾을 수 없습니다"
    else
        log_success "총 $installed개 NeoForge 모드팩에 설치 완료"
    fi
}

# Fabric 모드팩에 설치
install_fabric_mods() {
    log_info "Fabric 모드팩 검색 및 설치..."
    
    local installed=0
    
    for modpack_dir in "$HOME"/*/; do
        if [ -d "$modpack_dir" ]; then
            # Fabric 모드팩인지 확인
            if find "$modpack_dir" -name "*fabric*loader*.jar" -o -name "*fabric*server*.jar" | grep -q .; then
                local mods_dir="$modpack_dir/mods"
                
                if [ -d "$mods_dir" ]; then
                    local modpack_name=$(basename "$modpack_dir")
                    log_info "Fabric 모드팩에 설치: $modpack_name"
                    
                    # 기존 모드 제거
                    find "$mods_dir" -name "modpackai*.jar" -delete 2>/dev/null || true
                    
                    # 새 모드 설치
                    cp "$BUILT_FABRIC_MOD" "$mods_dir/"
                    log_success "설치됨: $mods_dir/$(basename "$BUILT_FABRIC_MOD")"
                    installed=$((installed + 1))
                fi
            fi
        fi
    done
    
    if [ $installed -eq 0 ]; then
        log_warning "Fabric 모드팩을 찾을 수 없습니다"
    else
        log_success "총 $installed개 Fabric 모드팩에 설치 완료"
    fi
}

# 백엔드 설치 (기존 스크립트 재사용)
install_backend() {
    log_info "AI 백엔드 설치..."
    
    # 기존 install_mod.sh의 백엔드 설치 부분 실행
    if [ -f "install_mod.sh" ]; then
        log_info "기존 백엔드 설치 스크립트 실행..."
        # 모드 빌드 부분은 건너뛰고 백엔드만 설치
        bash install_mod.sh --backend-only 2>/dev/null || {
            log_warning "기존 스크립트로 백엔드 설치 실패. 수동 설치 필요"
        }
    else
        log_warning "install_mod.sh를 찾을 수 없습니다. 백엔드를 수동으로 설치해주세요."
    fi
}

# 메인 함수
main() {
    echo "🚀 ModpackAI 통합 설치 스크립트"
    echo "================================"
    echo "NeoForge와 Fabric 모드로더를 모두 지원합니다"
    echo ""
    
    # 명령행 인수 처리
    while [[ $# -gt 0 ]]; do
        case $1 in
            --modloader)
                MODLOADER_TYPE="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "알 수 없는 옵션: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 모드로더 타입이 지정되지 않은 경우 자동 감지
    if [ -z "$MODLOADER_TYPE" ]; then
        detect_modloaders
    fi
    
    log_info "설치할 모드로더: $MODLOADER_TYPE"
    echo ""
    
    # 시스템 확인
    check_system
    echo ""
    
    # 모드 빌드
    build_mods
    echo ""
    
    # 모드 설치
    install_mods
    echo ""
    
    # 백엔드 설치
    install_backend
    echo ""
    
    # 완료 메시지
    log_success "🎉 ModpackAI 통합 설치 완료!"
    echo ""
    echo "📋 설치 정보:"
    if [[ "$MODLOADER_TYPE" == "neoforge" || "$MODLOADER_TYPE" == "both" ]] && [ -n "$BUILT_NEOFORGE_MOD" ]; then
        echo "  ✅ NeoForge 모드: $(basename "$BUILT_NEOFORGE_MOD")"
    fi
    if [[ "$MODLOADER_TYPE" == "fabric" || "$MODLOADER_TYPE" == "both" ]] && [ -n "$BUILT_FABRIC_MOD" ]; then
        echo "  ✅ Fabric 모드: $(basename "$BUILT_FABRIC_MOD")"
    fi
    echo ""
    echo "🎮 게임 내 사용법:"
    echo "  /ai <질문>               - AI에게 바로 질문"
    echo "  /modpackai give          - AI 아이템 받기"
    echo "  /modpackai help          - 도움말 보기"
    echo ""
    echo "⚠️  다음 단계:"
    echo "  1. ~/minecraft-ai-backend/.env 파일에 API 키 설정"
    echo "  2. 모드팩 서버 재시작"
    echo "  3. 게임에서 /ai help 명령어로 테스트"
}

# 스크립트 실행
main "$@"