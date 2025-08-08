#!/usr/bin/env bash
# 🧹 GCP VM 롤백/정리 스크립트 (모드 기반)
# 목적: 실패한 설치 이후, 충돌 없이 재설치가 가능하도록 "이전 상태"로 최대한 되돌림
# 범위: AI 백엔드, 가상환경, systemd 서비스, 하이브리드 흔적, 플러그인 흔적, 모드 JAR/설정(선택)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

DRY_RUN=false
ASSUME_YES=false
KEEP_MODS=false
KEEP_PLUGINS=true
PROJECT_DIR=""

usage() {
  cat <<EOF
사용법: $0 [옵션]
  --dry-run           실제 삭제 대신 예정 작업만 출력
  --yes, -y           모든 확인 프롬프트 생략(비대화식)
  --project-dir=DIR   프로젝트 루트 지정(예: ~/minecraft-modpack-ai)
  --keep-mods         모드팩 내 설치된 AI 모드 JAR/설정 보존(기본은 삭제)
  --remove-plugins    플러그인 흔적도 삭제(기본은 보존)

예시:
  $0 --dry-run
  $0 -y --remove-plugins
  $0 -y --project-dir=$HOME/minecraft-modpack-ai
EOF
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --yes|-y) ASSUME_YES=true ;;
    --project-dir=*) PROJECT_DIR="${arg#*=}" ;;
    --keep-mods) KEEP_MODS=true ;;
    --remove-plugins) KEEP_PLUGINS=false ;;
    -h|--help) usage; exit 0 ;;
    *) log_error "알 수 없는 옵션: $arg"; usage; exit 2 ;;
  esac
done

run() {
  if $DRY_RUN; then
    echo "DRY-RUN: $*"
  else
    eval "$@"
  fi
}

confirm() {
  if $ASSUME_YES; then return 0; fi
  read -p "$1 (y/N): " -n 1 -r; echo
  [[ $REPLY =~ ^[Yy]$ ]]
}

echo "🧹 설치 롤백/정리 시작"
echo "════════════════════════════════════════"
log_warn "⚠️ 모드팩 서버와 월드 데이터는 삭제하지 않습니다."
log_info "옵션: DRY_RUN=$DRY_RUN, KEEP_MODS=$KEEP_MODS, KEEP_PLUGINS=$KEEP_PLUGINS"

if ! $ASSUME_YES; then
  if ! confirm "정말로 AI 관련 파일/서비스를 정리하시겠습니까?"; then
    log_info "작업이 취소되었습니다"; exit 0
  fi
fi

# 0) 프로젝트 디렉토리 자동 탐지(선택)
auto_detect_project_dir() {
  if [[ -n "$PROJECT_DIR" && -d "$PROJECT_DIR" ]]; then
    echo "$PROJECT_DIR"; return 0
  fi
  local cand
  for cand in "$HOME"/minecraft-modpack-ai "$HOME"/mc_ai "$HOME"/*/minecraft-modpack-ai; do
    if [[ -d "$cand/backend" && -f "$cand/backend/app.py" ]]; then
      echo "$cand"; return 0
    fi
  done
  echo ""
}

PROJECT_DIR="$(auto_detect_project_dir)"
if [[ -n "$PROJECT_DIR" ]]; then
  log_info "프로젝트 경로 탐지: $PROJECT_DIR"
else
  log_warn "프로젝트 경로를 찾지 못했습니다(문제 없음). --project-dir 로 지정 가능"
fi

# 1) systemd 서비스 정지 및 제거 (여러 이름 대응)
log_info "1) systemd 서비스 정리"
SERVICES=("mc-ai-backend" "minecraft-ai-backend")
for svc in "${SERVICES[@]}"; do
  if systemctl list-unit-files | grep -q "^${svc}\.service"; then
    run "sudo systemctl stop $svc 2>/dev/null || true"
    run "sudo systemctl disable $svc 2>/dev/null || true"
    log_info "서비스 중지/비활성화: $svc"
  fi
  if [[ -f "/etc/systemd/system/${svc}.service" ]]; then
    run "sudo rm -f /etc/systemd/system/${svc}.service"
    log_info "서비스 유닛 삭제: ${svc}.service"
  fi
done
run "sudo systemctl daemon-reload"
log_success "systemd 정리 완료"

# 2) 백엔드 프로세스/가상환경/상태 정리
log_info "2) 백엔드 및 Python 환경 정리"
# 실행 중인 백엔드 프로세스 종료(백엔드 스크립트 경로 기반)
if pgrep -af "backend/app.py" >/dev/null 2>&1; then
  PIDS=$(pgrep -af "backend/app.py" | awk '{print $1}') || true
  for pid in $PIDS; do
    run "kill $pid || true"
    log_info "프로세스 종료: PID=$pid"
  done
fi

# 가상환경/백엔드 상태 디렉토리 제거(설치 스크립트 관례값 포함)
BACKEND_DIRS=(
  "$HOME/minecraft-ai-backend"
  "$HOME/minecraft-ai-env"
)
if [[ -n "$PROJECT_DIR" ]]; then
  BACKEND_DIRS+=("$PROJECT_DIR/backend/venv")
fi
for d in "${BACKEND_DIRS[@]}"; do
  if [[ -e "$d" ]]; then
    run "rm -rf '$d'"
    log_info "삭제: $d"
  fi
done
log_success "백엔드/가상환경 정리 완료"

# 3) Git 클론 디렉토리 정리(선택)
if [[ -n "$PROJECT_DIR" ]]; then
  if confirm "프로젝트 디렉토리를 삭제하시겠습니까? ($PROJECT_DIR)"; then
    run "rm -rf '$PROJECT_DIR'"
    log_info "삭제: $PROJECT_DIR"
  else
    log_info "프로젝트 디렉토리 보존"
  fi
fi

# 4) 모드팩 내 흔적 제거(모드/플러그인/하이브리드/시작 스크립트)
log_info "4) 모드팩 디렉토리 정리"

discover_modpacks() {
  local dirs=()
  shopt -s nullglob
  for d in "$HOME"/* "$HOME"/*/*; do
    [[ -d "$d" ]] || continue
    if [[ -d "$d/mods" || -d "$d/plugins" || -f "$d/server.properties" ]]; then
      dirs+=("$d")
    fi
  done
  printf '%s\n' "${dirs[@]}" | sort -u
}

mapfile -t MODPACK_DIRS < <(discover_modpacks)
for dir in "${MODPACK_DIRS[@]}"; do
  log_info "처리: $dir"

  # 플러그인 흔적(옵션)
  if ! $KEEP_PLUGINS && [[ -d "$dir/plugins" ]]; then
    for f in \
      "$dir/plugins/ModpackAI-"*.jar \
      "$dir/plugins/modpack-ai-plugin-"*.jar \
      "$dir/plugins/modpack-ai-plugin-"*-shaded.jar; do
      [[ -e "$f" ]] || continue
      run "rm -f '$f'"; log_info "  삭제(플러그인): $(basename "$f")"
    done
    if [[ -d "$dir/plugins/ModpackAI" ]]; then
      run "rm -rf '$dir/plugins/ModpackAI'"; log_info "  삭제: plugins/ModpackAI"
    fi
  fi

  # 하이브리드 서버 JAR 흔적 제거
  for f in \
    "$dir/youer-neoforge.jar" \
    "$dir/mohist-"*.jar \
    "$dir/cardboard"*.jar \
    "$dir/arclight-neoforge"*.jar \
    "$dir/neoforge-hybrid.jar"; do
    [[ -e "$f" ]] || continue
    run "rm -f '$f'"; log_info "  삭제(하이브리드): $(basename "$f")"
  done

  # 모드 JAR/설정(옵션: KEEP_MODS=false 일 때 삭제)
  if ! $KEEP_MODS && [[ -d "$dir/mods" ]]; then
    for f in \
      "$dir/mods/modpackai-"*.jar \
      "$dir/mods/modpack-ai-"*.jar \
      "$dir/mods/ModpackAI"*.jar; do
      [[ -e "$f" ]] || continue
      run "rm -f '$f'"; log_info "  삭제(모드): mods/$(basename "$f")"
    done
  fi
  if ! $KEEP_MODS; then
    # 구성 파일 몇 가지 관례 경로 제거
    for cfg in \
      "$dir/config/modpackai.json" \
      "$dir/config/modpackai"/*.json \
      "$dir/config/ModpackAI"/*.json; do
      [[ -e "$cfg" ]] || continue
      run "rm -f '$cfg'"; log_info "  삭제(설정): $(echo "$cfg" | sed "s#^$dir/##")"
    done
  fi

  # AI 시작 스크립트 제거 및 백업 복원
  if [[ -f "$dir/start_with_ai.sh" ]]; then
    run "rm -f '$dir/start_with_ai.sh'"; log_info "  삭제: start_with_ai.sh"
  fi
  if [[ -f "$dir/start.sh.backup" ]]; then
    if [[ -f "$dir/start.sh" ]] && grep -q "AI Assistant\|modpackai" "$dir/start.sh" 2>/dev/null; then
      run "cp '$dir/start.sh.backup' '$dir/start.sh'"; log_info "  복원: start.sh"
    fi
    run "rm -f '$dir/start.sh.backup'"; log_info "  삭제: start.sh.backup"
  fi

  log_success "  정리 완료: $dir"
done

# 5) 전역 스크립트/바이너리 정리
log_info "5) 전역 스크립트 정리"
for bin in \
  "/usr/local/bin/modpack_switch" \
  "/usr/local/bin/mc-ai-monitor"; do
  if [[ -e "$bin" ]]; then
    run "sudo rm -f '$bin'"; log_info "삭제: $bin"
  fi
done
log_success "전역 스크립트 정리 완료"

# 6) 캐시 정리(선택)
log_info "6) 캐시 정리 옵션"
if [[ -d "$HOME/.m2/repository" ]]; then
  if confirm "Maven 캐시(~/.m2/repository)을 정리하시겠습니까?"; then
    run "rm -rf '$HOME/.m2/repository'"; log_info "Maven 캐시 삭제"
  fi
fi
if [[ -d "$HOME/.gradle" ]]; then
  if confirm "Gradle 캐시(~/.gradle)을 정리하시겠습니까?"; then
    run "rm -rf '$HOME/.gradle'"; log_info "Gradle 캐시 삭제"
  fi
fi

echo ""
echo "🎉 정리 완료"
echo "════════════════════════════════════════"
echo ""
echo "📌 요약"
echo "  - systemd 서비스: mc-ai-backend/minecraft-ai-backend 정리"
echo "  - 백엔드/가상환경: 삭제 완료"
echo "  - 모드팩: 하이브리드/시작 스크립트 및 (옵션) 모드/플러그인 제거"
echo "  - 전역 스크립트: 제거"
echo "  - 캐시: 선택적 정리"
echo ""
echo "다시 설치하려면:"
echo "  1) 저장소 준비 후 cd <프로젝트>"
echo "  2) ./install.sh  또는  ./install_mod.sh"