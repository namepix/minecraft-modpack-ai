#!/bin/bash

# 🤖 RAG 빠른 설정 스크립트
# 모드팩별 RAG 인덱스 구축 및 관리를 위한 원클릭 도구

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 프로젝트 루트 디렉토리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

show_help() {
    cat << EOF
🤖 RAG 빠른 설정 도구

사용법:
  $0 [명령어] [옵션]

명령어:
  build <모드팩_이름> <모드팩_버전> <모드팩_경로>  # RAG 인덱스 구축
  set-manual <모드팩_이름> <모드팩_버전>             # 수동 모드 설정
  set-auto                                        # 자동 모드 설정
  status                                          # 현재 상태 확인
  list                                            # 등록된 모드팩 목록
  help                                            # 도움말 표시

예시:
  $0 build "pixelmon_reforged" "9.1.12" "/home/user/pixelmon_reforged"
  $0 set-manual "pixelmon_reforged" "9.1.12"
  $0 set-auto
  $0 status
  $0 list

참고:
  - 첫 실행 시 GCP 설정이 필요합니다
  - Python 가상환경이 활성화되어야 합니다
  - .env 파일에 API 키가 설정되어야 합니다
EOF
}

check_requirements() {
    log_info "요구사항 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않음"
        exit 1
    fi
    
    # 백엔드 디렉토리 확인
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "백엔드 디렉토리를 찾을 수 없음: $BACKEND_DIR"
        exit 1
    fi
    
    # 필수 Python 모듈 확인
    cd "$BACKEND_DIR"
    if ! python3 -c "import gcp_rag_system" &> /dev/null; then
        log_error "GCP RAG 모듈을 찾을 수 없음. requirements.txt를 설치하세요."
        exit 1
    fi
    
    log_success "요구사항 확인 완료"
}

build_rag_index() {
    local name="$1"
    local version="$2"
    local path="$3"
    
    log_info "RAG 인덱스 구축: $name v$version"
    log_info "경로: $path"
    
    cd "$BACKEND_DIR"
    python3 rag_manager.py build "$name" "$version" "$path"
    
    if [ $? -eq 0 ]; then
        log_success "RAG 인덱스 구축 완료!"
        
        # 자동으로 수동 모드 설정 제안
        read -p "이 모드팩을 활성 모드팩으로 설정하시겠습니까? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            set_manual_modpack "$name" "$version"
        fi
    else
        log_error "RAG 인덱스 구축 실패"
        exit 1
    fi
}

set_manual_modpack() {
    local name="$1"
    local version="$2"
    
    log_info "수동 모드 설정: $name v$version"
    
    cd "$BACKEND_DIR"
    python3 config_manager.py set-manual "$name" "$version"
    
    if [ $? -eq 0 ]; then
        log_success "수동 모드 설정 완료!"
        show_status
    else
        log_error "수동 모드 설정 실패"
        exit 1
    fi
}

set_auto_mode() {
    log_info "자동 모드로 전환 중..."
    
    cd "$BACKEND_DIR"
    python3 config_manager.py set-auto
    
    if [ $? -eq 0 ]; then
        log_success "자동 모드 설정 완료!"
        show_status
    else
        log_error "자동 모드 설정 실패"
        exit 1
    fi
}

show_status() {
    log_info "현재 RAG 시스템 상태:"
    
    cd "$BACKEND_DIR"
    python3 config_manager.py status
}

list_modpacks() {
    log_info "등록된 모드팩 목록:"
    
    cd "$BACKEND_DIR"
    python3 rag_manager.py list
}

# 모드팩 경로 자동 탐지
auto_detect_modpack() {
    log_info "홈 디렉토리에서 모드팩 자동 탐지 중..."
    
    local found_modpacks=()
    
    # 홈 디렉토리에서 mods 폴더를 포함한 디렉토리 찾기
    while IFS= read -r -d '' modpack_dir; do
        local modpack_name=$(basename "$(dirname "$modpack_dir")")
        local mods_count=$(find "$modpack_dir" -name "*.jar" 2>/dev/null | wc -l)
        
        if [ "$mods_count" -gt 5 ]; then  # 5개 이상 JAR 파일이 있으면 모드팩으로 간주
            found_modpacks+=("$modpack_name|$(dirname "$modpack_dir")|$mods_count")
        fi
    done < <(find "$HOME" -maxdepth 3 -name "mods" -type d -print0 2>/dev/null)
    
    if [ ${#found_modpacks[@]} -eq 0 ]; then
        log_warning "모드팩을 찾을 수 없습니다."
        return 1
    fi
    
    log_success "발견된 모드팩:"
    for i in "${!found_modpacks[@]}"; do
        IFS='|' read -r name path mods_count <<< "${found_modpacks[$i]}"
        echo "  $((i+1)). $name ($mods_count개 모드)"
        echo "     경로: $path"
    done
    
    read -p "RAG 인덱스를 구축할 모드팩 번호를 선택하세요 (1-${#found_modpacks[@]}): " choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#found_modpacks[@]}" ]; then
        IFS='|' read -r selected_name selected_path _ <<< "${found_modpacks[$((choice-1))]}"
        
        read -p "모드팩 버전을 입력하세요 (기본값: 1.0.0): " version
        version=${version:-1.0.0}
        
        build_rag_index "$selected_name" "$version" "$selected_path"
    else
        log_error "잘못된 선택입니다."
        return 1
    fi
}

# 메인 함수
main() {
    echo "🤖 RAG 빠른 설정 도구"
    echo "================================"
    
    case "${1:-help}" in
        "build")
            if [ $# -ne 4 ]; then
                log_error "사용법: $0 build <모드팩_이름> <모드팩_버전> <모드팩_경로>"
                exit 1
            fi
            check_requirements
            build_rag_index "$2" "$3" "$4"
            ;;
        "auto-detect")
            check_requirements
            auto_detect_modpack
            ;;
        "set-manual")
            if [ $# -ne 3 ]; then
                log_error "사용법: $0 set-manual <모드팩_이름> <모드팩_버전>"
                exit 1
            fi
            check_requirements
            set_manual_modpack "$2" "$3"
            ;;
        "set-auto")
            check_requirements
            set_auto_mode
            ;;
        "status")
            check_requirements
            show_status
            ;;
        "list")
            check_requirements
            list_modpacks
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "알 수 없는 명령어: $1"
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"