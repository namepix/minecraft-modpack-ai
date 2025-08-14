#!/bin/bash
# 🔄 GCP VM 완전 초기화 스크립트 - ADMIN_SETUP.md 재실행 준비
# 목적: GCP VM을 ADMIN_SETUP.md 실행 이전 상태로 완전히 초기화
# 범위: ModpackAI 관련 모든 흔적 제거 및 시스템 정리

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${CYAN}=== $1 ===${NC}"; }

# 기본 설정
DRY_RUN=false
ASSUME_YES=false
KEEP_SYSTEM_PACKAGES=true
KEEP_MINECRAFT_WORLDS=true
VERBOSE=false
BACKUP_CONFIGS=false

# 사용법
usage() {
    cat << EOF
🔄 GCP VM 완전 초기화 스크립트 (ADMIN_SETUP.md 재실행 준비)

사용법: $0 [옵션]

기본 옵션:
  --dry-run               실제 삭제 대신 예정 작업만 출력
  --yes, -y               모든 확인 프롬프트 생략 (비대화식)
  --verbose, -v           상세 로그 출력
  --backup-configs        삭제 전 중요 설정 파일 백업

고급 옵션:
  --remove-packages       시스템 패키지도 제거 (Java, Python 등)
  --remove-worlds         마인크래프트 월드 데이터도 삭제
  --help, -h              도움말 표시

예시:
  $0 --dry-run --verbose
  $0 -y --backup-configs
  $0 --yes --remove-packages
EOF
}

# 인자 처리
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true ;;
        --yes|-y) ASSUME_YES=true ;;
        --verbose|-v) VERBOSE=true ;;
        --backup-configs) BACKUP_CONFIGS=true ;;
        --remove-packages) KEEP_SYSTEM_PACKAGES=false ;;
        --remove-worlds) KEEP_MINECRAFT_WORLDS=false ;;
        --help|-h) usage; exit 0 ;;
        *) log_error "알 수 없는 옵션: $1"; usage; exit 1 ;;
    esac
    shift
done

# 실행 함수
run() {
    if $DRY_RUN; then
        echo "DRY-RUN: $*"
    else
        if $VERBOSE; then
            echo "EXEC: $*"
        fi
        eval "$@"
    fi
}

# 확인 함수
confirm() {
    if $ASSUME_YES; then return 0; fi
    echo -e "${YELLOW}❓ $1 (y/N): ${NC}\c"
    read -r REPLY
    [[ $REPLY =~ ^[Yy]$ ]]
}

# 백업 함수
backup_file() {
    local file="$1"
    if [[ -f "$file" ]] && $BACKUP_CONFIGS; then
        local backup_dir="$HOME/modpackai_backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        cp "$file" "$backup_dir/"
        log_info "백업: $file → $backup_dir/"
    fi
}

# 시작 메시지
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════╗
║     🔄 GCP VM 완전 초기화 스크립트        ║
║      ADMIN_SETUP.md 재실행 준비용        ║
╚══════════════════════════════════════════╝
EOF
echo -e "${NC}"

log_warn "⚠️  이 스크립트는 ModpackAI 관련 모든 설치 흔적을 제거합니다"
log_warn "⚠️  마인크래프트 월드 데이터는 기본적으로 보존됩니다"
log_info "옵션: DRY_RUN=$DRY_RUN, ASSUME_YES=$ASSUME_YES, VERBOSE=$VERBOSE"

if ! $ASSUME_YES; then
    echo ""
    if ! confirm "정말로 GCP VM을 ADMIN_SETUP.md 실행 이전 상태로 초기화하시겠습니까?"; then
        log_info "작업이 취소되었습니다"
        exit 0
    fi
fi

echo ""

# =============================================================================
# 1단계: 프로세스 및 서비스 정지
# =============================================================================
log_header "1단계: 실행 중인 프로세스 및 서비스 정리"

# ModpackAI 관련 프로세스 종료
log_info "ModpackAI 관련 프로세스 종료 중..."
for pattern in "app.py" "modpack" "minecraft.*ai" "mc.*ai"; do
    if pgrep -f "$pattern" >/dev/null 2>&1; then
        if $VERBOSE; then log_info "프로세스 패턴 '$pattern' 종료 중..."; fi
        run "pkill -f '$pattern' || true"
    fi
done

# systemd 서비스 정리
SERVICES=(
    "mc-ai-backend"
    "minecraft-ai-backend" 
    "modpack-ai"
    "minecraft-modpack-ai"
)

for service in "${SERVICES[@]}"; do
    if systemctl list-unit-files 2>/dev/null | grep -q "^${service}\.service"; then
        log_info "서비스 중지: $service"
        run "sudo systemctl stop $service 2>/dev/null || true"
        run "sudo systemctl disable $service 2>/dev/null || true"
    fi
    
    if [[ -f "/etc/systemd/system/${service}.service" ]]; then
        backup_file "/etc/systemd/system/${service}.service"
        run "sudo rm -f /etc/systemd/system/${service}.service"
        log_info "서비스 파일 삭제: ${service}.service"
    fi
done

run "sudo systemctl daemon-reload"
log_success "프로세스 및 서비스 정리 완료"

# =============================================================================
# 2단계: 백엔드 및 Python 환경 정리
# =============================================================================
log_header "2단계: 백엔드 및 Python 환경 정리"

# 백엔드 실행 디렉토리들
BACKEND_DIRS=(
    "$HOME/minecraft-ai-backend"
    "$HOME/minecraft-ai-env"
    "$HOME/modpack-ai-backend" 
    "$HOME/mc-ai-backend"
)

for dir in "${BACKEND_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        backup_file "$dir/.env"
        run "rm -rf '$dir'"
        log_info "삭제: $dir"
    fi
done

log_success "백엔드 환경 정리 완료"

# =============================================================================
# 3단계: 프로젝트 소스 디렉토리 정리
# =============================================================================
log_header "3단계: 프로젝트 소스 디렉토리 정리"

# 자동 탐지
PROJECT_DIRS=(
    "$HOME/minecraft-modpack-ai"
    "$HOME/mc_ai"
    "$HOME/modpack-ai"
    "$HOME/MinecraftAI"
)

# 추가 패턴으로 검색
while IFS= read -r -d '' dir; do
    PROJECT_DIRS+=("$dir")
done < <(find "$HOME" -maxdepth 2 -type d -name "*minecraft*ai*" -print0 2>/dev/null || true)

# 중복 제거
readarray -t PROJECT_DIRS < <(printf '%s\n' "${PROJECT_DIRS[@]}" | sort -u)

for project_dir in "${PROJECT_DIRS[@]}"; do
    if [[ -d "$project_dir" ]]; then
        # 중요 파일 백업
        if [[ -f "$project_dir/.env" ]]; then
            backup_file "$project_dir/.env"
        fi
        if [[ -f "$project_dir/backend/rag_config.json" ]]; then
            backup_file "$project_dir/backend/rag_config.json"
        fi
        
        if confirm "프로젝트 디렉토리를 삭제하시겠습니까? ($project_dir)"; then
            run "rm -rf '$project_dir'"
            log_info "삭제: $project_dir"
        else
            log_info "보존: $project_dir"
        fi
    fi
done

log_success "프로젝트 디렉토리 정리 완료"

# =============================================================================
# 4단계: 모드팩 디렉토리에서 ModpackAI 흔적 제거
# =============================================================================
log_header "4단계: 모드팩 디렉토리 정리"

# 모드팩 디렉토리 탐지
discover_modpacks() {
    local dirs=()
    # 일반적인 마인크래프트 서버 위치들
    for base in "$HOME" "/opt" "/srv" "/var"; do
        if [[ -d "$base" ]]; then
            while IFS= read -r -d '' dir; do
                dirs+=("$dir")
            done < <(find "$base" -maxdepth 3 -type d \( -name "mods" -o -name "plugins" \) -print0 2>/dev/null | xargs -0 -I{} dirname {} | sort -u)
        fi
    done
    printf '%s\n' "${dirs[@]}" | sort -u
}

mapfile -t MODPACK_DIRS < <(discover_modpacks)

for modpack_dir in "${MODPACK_DIRS[@]}"; do
    if [[ ! -d "$modpack_dir" ]]; then continue; fi
    
    log_info "처리 중: $modpack_dir"
    modpack_name=$(basename "$modpack_dir")
    
    # 모드 JAR 파일 제거
    if [[ -d "$modpack_dir/mods" ]]; then
        for mod_pattern in "modpackai*" "ModpackAI*" "modpack-ai*"; do
            for mod_file in "$modpack_dir/mods/"$mod_pattern.jar; do
                [[ -f "$mod_file" ]] || continue
                run "rm -f '$mod_file'"
                log_info "  모드 삭제: mods/$(basename "$mod_file")"
            done
        done
    fi
    
    # 플러그인 JAR 파일 제거
    if [[ -d "$modpack_dir/plugins" ]]; then
        for plugin_pattern in "ModpackAI*" "modpack-ai*"; do
            for plugin_file in "$modpack_dir/plugins/"$plugin_pattern.jar; do
                [[ -f "$plugin_file" ]] || continue
                run "rm -f '$plugin_file'"
                log_info "  플러그인 삭제: plugins/$(basename "$plugin_file")"
            done
        done
        
        # 플러그인 데이터 디렉토리
        if [[ -d "$modpack_dir/plugins/ModpackAI" ]]; then
            run "rm -rf '$modpack_dir/plugins/ModpackAI'"
            log_info "  플러그인 데이터 삭제: plugins/ModpackAI"
        fi
    fi
    
    # 설정 파일 제거
    CONFIG_PATTERNS=(
        "config/modpackai*"
        "config/ModpackAI*" 
        "config/*modpack*ai*"
    )
    for pattern in "${CONFIG_PATTERNS[@]}"; do
        for config_file in $modpack_dir/$pattern; do
            [[ -e "$config_file" ]] || continue
            backup_file "$config_file"
            run "rm -rf '$config_file'"
            log_info "  설정 삭제: $(echo "$config_file" | sed "s#^$modpack_dir/##")"
        done
    done
    
    # 시작 스크립트 복원
    if [[ -f "$modpack_dir/start.sh.backup" ]]; then
        run "mv '$modpack_dir/start.sh.backup' '$modpack_dir/start.sh'"
        log_info "  시작 스크립트 복원: start.sh"
    fi
    
    # AI 관련 시작 스크립트 제거
    for ai_script in "start_with_ai.sh" "run_with_ai.sh" "launch_ai.sh"; do
        if [[ -f "$modpack_dir/$ai_script" ]]; then
            run "rm -f '$modpack_dir/$ai_script'"
            log_info "  AI 스크립트 삭제: $ai_script"
        fi
    done
done

log_success "모드팩 디렉토리 정리 완료"

# =============================================================================
# 5단계: 전역 설치 파일 및 스크립트 정리
# =============================================================================
log_header "5단계: 전역 파일 정리"

# 전역 바이너리 및 스크립트
GLOBAL_BINS=(
    "/usr/local/bin/modpack_switch"
    "/usr/local/bin/mc-ai-monitor"
    "/usr/local/bin/minecraft-ai"
    "/usr/local/bin/modpackai"
)

for bin_file in "${GLOBAL_BINS[@]}"; do
    if [[ -f "$bin_file" ]]; then
        backup_file "$bin_file"
        run "sudo rm -f '$bin_file'"
        log_info "전역 스크립트 삭제: $bin_file"
    fi
done

# 홈 디렉토리의 설치/관리 스크립트들
HOME_SCRIPTS=(
    "$HOME/install_mod.sh"
    "$HOME/cleanup_gcpvm.sh"
    "$HOME/sync_backend.sh"
    "$HOME/rag_quick_setup.sh"
    "$HOME/test_rag_results.sh"
    "$HOME/modpack_manager.sh"
)

for script in "${HOME_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        backup_file "$script"
        if confirm "홈 디렉토리 스크립트를 삭제하시겠습니까? ($(basename "$script"))"; then
            run "rm -f '$script'"
            log_info "스크립트 삭제: $script"
        fi
    fi
done

log_success "전역 파일 정리 완료"

# =============================================================================
# 6단계: 시스템 패키지 정리 (선택사항)
# =============================================================================
if ! $KEEP_SYSTEM_PACKAGES; then
    log_header "6단계: 시스템 패키지 정리"
    
    log_warn "⚠️  ModpackAI용으로 설치된 시스템 패키지를 제거합니다"
    
    # Python 패키지 (pip로 설치된 것들)
    PYTHON_PACKAGES=(
        "flask"
        "flask-cors" 
        "requests"
        "openai"
        "google-generativeai"
        "anthropic"
        "sentence-transformers"
        "faiss-cpu"
        "google-cloud-firestore"
        "google-cloud-aiplatform"
        "vertexai"
    )
    
    if command -v pip3 >/dev/null 2>&1; then
        for pkg in "${PYTHON_PACKAGES[@]}"; do
            if pip3 list 2>/dev/null | grep -q "^$pkg "; then
                if confirm "Python 패키지 '$pkg'를 제거하시겠습니까?"; then
                    run "pip3 uninstall -y '$pkg' || true"
                    log_info "Python 패키지 제거: $pkg"
                fi
            fi
        done
    fi
    
    # 시스템 패키지 (apt로 설치된 것들)
    SYSTEM_PACKAGES=(
        "python3-venv"
        "python3-pip"
        "curl"
        "wget"
        "unzip"
    )
    
    if command -v apt-get >/dev/null 2>&1; then
        for pkg in "${SYSTEM_PACKAGES[@]}"; do
            if dpkg -l | grep -q "^ii  $pkg "; then
                if confirm "시스템 패키지 '$pkg'를 제거하시겠습니까?"; then
                    run "sudo apt-get remove -y '$pkg'"
                    log_info "시스템 패키지 제거: $pkg"
                fi
            fi
        done
        
        # 불필요한 의존성 정리
        run "sudo apt-get autoremove -y"
        run "sudo apt-get autoclean"
    fi
    
    log_success "시스템 패키지 정리 완료"
else
    log_info "시스템 패키지 보존됨 (--remove-packages 사용하여 제거 가능)"
fi

# =============================================================================
# 7단계: 캐시 및 임시 파일 정리
# =============================================================================
log_header "7단계: 캐시 및 임시 파일 정리"

# Python 캐시
PYTHON_CACHE_DIRS=(
    "$HOME/.cache/pip"
    "$HOME/.local/lib/python*/site-packages/__pycache__"
)

for cache_dir in "${PYTHON_CACHE_DIRS[@]}"; do
    if [[ -d "$cache_dir" ]]; then
        if confirm "Python 캐시를 정리하시겠습니까? ($cache_dir)"; then
            run "rm -rf '$cache_dir'"
            log_info "캐시 삭제: $cache_dir"
        fi
    fi
done

# Java/Gradle 캐시
if [[ -d "$HOME/.gradle" ]]; then
    if confirm "Gradle 캐시(~/.gradle)를 정리하시겠습니까?"; then
        run "rm -rf '$HOME/.gradle'"
        log_info "Gradle 캐시 삭제"
    fi
fi

if [[ -d "$HOME/.m2/repository" ]]; then
    if confirm "Maven 캐시(~/.m2/repository)를 정리하시겠습니까?"; then
        run "rm -rf '$HOME/.m2/repository'"
        log_info "Maven 캐시 삭제"
    fi
fi

# 임시 파일들
TEMP_PATTERNS=(
    "/tmp/*modpack*"
    "/tmp/*minecraft*"
    "/tmp/gradle-*"
    "$HOME/nohup.out"
)

for pattern in "${TEMP_PATTERNS[@]}"; do
    for temp_file in $pattern; do
        [[ -e "$temp_file" ]] || continue
        run "rm -rf '$temp_file'"
        if $VERBOSE; then log_info "임시 파일 삭제: $temp_file"; fi
    done
done

log_success "캐시 및 임시 파일 정리 완료"

# =============================================================================
# 8단계: 사용자 설정 및 환경변수 정리
# =============================================================================
log_header "8단계: 사용자 환경 정리"

# .bashrc 에서 ModpackAI 관련 설정 제거
if [[ -f "$HOME/.bashrc" ]]; then
    backup_file "$HOME/.bashrc"
    
    # ModpackAI 관련 라인들 제거
    run "sed -i '/modpack/Id; /ModpackAI/Id; /minecraft.*ai/Id; /mc.*ai/Id' '$HOME/.bashrc'"
    log_info ".bashrc에서 ModpackAI 관련 설정 제거"
fi

# 환경변수 파일들 정리
ENV_FILES=(
    "$HOME/.env"
    "$HOME/.environment"
    "$HOME/minecraft.env"
)

for env_file in "${ENV_FILES[@]}"; do
    if [[ -f "$env_file" ]]; then
        backup_file "$env_file"
        if confirm "환경변수 파일을 삭제하시겠습니까? ($(basename "$env_file"))"; then
            run "rm -f '$env_file'"
            log_info "환경변수 파일 삭제: $env_file"
        fi
    fi
done

log_success "사용자 환경 정리 완료"

# =============================================================================
# 9단계: 검증 및 최종 정리
# =============================================================================
log_header "9단계: 검증 및 최종 정리"

# 남은 ModpackAI 흔적 검색
log_info "남은 ModpackAI 흔적 검색 중..."

REMAINING_FILES=()
while IFS= read -r -d '' file; do
    REMAINING_FILES+=("$file")
done < <(find "$HOME" -type f -iname "*modpack*ai*" -o -iname "*minecraft*ai*" 2>/dev/null | head -20 | tr '\n' '\0')

if [[ ${#REMAINING_FILES[@]} -gt 0 ]]; then
    log_warn "다음 파일들이 남아있습니다:"
    for file in "${REMAINING_FILES[@]}"; do
        echo "  - $file"
    done
    
    if confirm "이 파일들도 삭제하시겠습니까?"; then
        for file in "${REMAINING_FILES[@]}"; do
            run "rm -f '$file'"
        done
        log_info "추가 파일들 삭제 완료"
    fi
else
    log_success "ModpackAI 관련 파일 완전히 제거됨"
fi

# 프로세스 확인
if pgrep -f "modpack\|minecraft.*ai" >/dev/null 2>&1; then
    log_warn "일부 관련 프로세스가 아직 실행 중입니다"
    if $VERBOSE; then
        pgrep -af "modpack\|minecraft.*ai"
    fi
else
    log_success "관련 프로세스 완전히 정리됨"
fi

log_success "검증 완료"

# =============================================================================
# 완료 메시지
# =============================================================================
echo ""
log_header "🎉 GCP VM 초기화 완료"

echo ""
echo "📋 정리 요약:"
echo "  ✅ SystemD 서비스 제거 및 정리"
echo "  ✅ Python 백엔드 환경 완전 제거"
echo "  ✅ 프로젝트 소스 디렉토리 정리"
echo "  ✅ 모드팩 내 ModpackAI 흔적 제거"
echo "  ✅ 전역 스크립트 및 바이너리 정리"
if ! $KEEP_SYSTEM_PACKAGES; then
    echo "  ✅ 시스템 패키지 정리"
fi
echo "  ✅ 캐시 및 임시 파일 정리"
echo "  ✅ 사용자 환경 설정 정리"

if $BACKUP_CONFIGS && [[ -d "$HOME/modpackai_backup_"* ]]; then
    echo ""
    echo "💾 백업 파일 위치:"
    ls -d "$HOME/modpackai_backup_"* 2>/dev/null || true
fi

echo ""
echo "🚀 ADMIN_SETUP.md 재실행 준비 완료!"
echo ""
echo "다음 단계:"
echo "  1. 저장소 클론: git clone <repository-url>"
echo "  2. 가이드 실행: ./ADMIN_SETUP.md 또는 해당 설치 스크립트"
echo "  3. 필요시 백업된 설정 파일 복원"

if ! $ASSUME_YES; then
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
fi