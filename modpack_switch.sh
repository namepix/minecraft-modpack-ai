#!/bin/bash

# 마인크래프트 모드팩 AI - 모드팩 변경 스크립트
# 사용법: ./modpack_switch.sh <모드팩명> [버전]

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정 파일 경로
CONFIG_FILE="/opt/mc_ai_backend/.env"
MODPACKS_DIR="/tmp/modpacks"
BACKEND_URL="http://localhost:5000"

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

# 도움말 표시
show_help() {
    echo "마인크래프트 모드팩 AI - 모드팩 변경 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0 <모드팩명> [버전]"
    echo "  $0 --list"
    echo "  $0 --help"
    echo ""
    echo "옵션:"
    echo "  <모드팩명>    변경할 모드팩의 이름"
    echo "  [버전]        모드팩 버전 (선택사항, 기본값: 1.0)"
    echo "  --list        사용 가능한 모드팩 목록 표시"
    echo "  --help        이 도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 CreateModpack"
    echo "  $0 FTBRevelation 1.0.0"
    echo "  $0 AllTheMods 1.19.2"
    echo ""
    echo "설정:"
    echo "  모드팩 디렉토리: $MODPACKS_DIR"
    echo "  백엔드 URL: $BACKEND_URL"
}

# 설정 파일에서 모드팩 디렉토리 읽기
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        MODPACKS_DIR=$(grep "^MODPACK_UPLOAD_DIR=" "$CONFIG_FILE" | cut -d'=' -f2)
        if [ -z "$MODPACKS_DIR" ]; then
            MODPACKS_DIR="/tmp/modpacks"
        fi
        log_info "설정 파일에서 모드팩 디렉토리 로드: $MODPACKS_DIR"
    else
        log_warning "설정 파일을 찾을 수 없습니다: $CONFIG_FILE"
        log_info "기본 모드팩 디렉토리 사용: $MODPACKS_DIR"
    fi
}

# 백엔드 서비스 상태 확인
check_backend() {
    log_info "백엔드 서비스 상태 확인 중..."
    
    if ! curl -s "$BACKEND_URL/health" > /dev/null; then
        log_error "백엔드 서비스에 연결할 수 없습니다: $BACKEND_URL"
        log_info "백엔드 서비스를 시작하세요: sudo systemctl start mc-ai-backend"
        return 1
    fi
    
    log_success "백엔드 서비스가 정상 실행 중입니다"
    return 0
}

# 사용 가능한 모드팩 목록 표시
list_modpacks() {
    log_info "사용 가능한 모드팩 목록:"
    echo ""
    
    if [ ! -d "$MODPACKS_DIR" ]; then
        log_error "모드팩 디렉토리가 존재하지 않습니다: $MODPACKS_DIR"
        log_info "디렉토리를 생성하세요: sudo mkdir -p $MODPACKS_DIR"
        return 1
    fi
    
    local found=false
    for file in "$MODPACKS_DIR"/*.zip "$MODPACKS_DIR"/*.jar; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            size=$(du -h "$file" | cut -f1)
            modified=$(stat -c %y "$file" | cut -d' ' -f1)
            echo "  📦 $filename"
            echo "     크기: $size | 수정일: $modified"
            echo ""
            found=true
        fi
    done
    
    if [ "$found" = false ]; then
        log_warning "모드팩 파일을 찾을 수 없습니다: $MODPACKS_DIR"
        log_info "모드팩 파일을 업로드하세요: scp your-modpack.zip username@server-ip:$MODPACKS_DIR/"
    fi
}

# 모드팩 파일 찾기
find_modpack_file() {
    local modpack_name="$1"
    local version="$2"
    
    # 가능한 파일명 패턴들
    local patterns=(
        "$MODPACKS_DIR/${modpack_name}_${version}.zip"
        "$MODPACKS_DIR/${modpack_name}_${version}.jar"
        "$MODPACKS_DIR/${modpack_name}.zip"
        "$MODPACKS_DIR/${modpack_name}.jar"
        "$MODPACKS_DIR/${modpack_name,,}_${version}.zip"  # 소문자
        "$MODPACKS_DIR/${modpack_name,,}_${version}.jar"
        "$MODPACKS_DIR/${modpack_name,,}.zip"
        "$MODPACKS_DIR/${modpack_name,,}.jar"
    )
    
    for pattern in "${patterns[@]}"; do
        if [ -f "$pattern" ]; then
            echo "$pattern"
            return 0
        fi
    done
    
    return 1
}

# 모드팩 변경 실행
switch_modpack() {
    local modpack_name="$1"
    local version="${2:-1.0}"
    
    log_info "모드팩 변경 시작: $modpack_name v$version"
    
    # 1. 백엔드 서비스 확인
    if ! check_backend; then
        return 1
    fi
    
    # 2. 모드팩 파일 찾기
    log_info "모드팩 파일 검색 중..."
    local modpack_file
    if modpack_file=$(find_modpack_file "$modpack_name" "$version"); then
        log_success "모드팩 파일 발견: $modpack_file"
    else
        log_error "모드팩 파일을 찾을 수 없습니다: $modpack_name v$version"
        log_info "사용 가능한 모드팩 목록을 확인하세요: $0 --list"
        return 1
    fi
    
    # 3. 파일 크기 및 권한 확인
    local file_size=$(du -h "$modpack_file" | cut -f1)
    log_info "파일 크기: $file_size"
    
    if [ ! -r "$modpack_file" ]; then
        log_error "파일을 읽을 수 없습니다: $modpack_file"
        log_info "권한을 수정하세요: sudo chmod 644 $modpack_file"
        return 1
    fi
    
    # 4. 백엔드 API 호출
    log_info "백엔드에 모드팩 변경 요청 중..."
    
    local response
    response=$(curl -s -X POST "$BACKEND_URL/api/modpack/switch" \
        -H "Content-Type: application/json" \
        -d "{
            \"modpack_path\": \"$modpack_file\",
            \"modpack_name\": \"$modpack_name\",
            \"modpack_version\": \"$version\"
        }")
    
    # 5. 응답 처리
    if echo "$response" | grep -q '"error"'; then
        local error_msg=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        log_error "모드팩 변경 실패: $error_msg"
        return 1
    else
        log_success "모드팩 변경이 완료되었습니다!"
        
        # 응답에서 상세 정보 추출
        local mods_count=$(echo "$response" | grep -o '"mods_count":[0-9]*' | cut -d':' -f2)
        local recipes_count=$(echo "$response" | grep -o '"recipes_count":[0-9]*' | cut -d':' -f2)
        local items_count=$(echo "$response" | grep -o '"items_count":[0-9]*' | cut -d':' -f2)
        local mappings_added=$(echo "$response" | grep -o '"language_mappings_added":[0-9]*' | cut -d':' -f2)
        
        echo ""
        echo "📊 변경 결과:"
        echo "  🎮 모드팩: $modpack_name v$version"
        echo "  📦 모드 수: $mods_count"
        echo "  🛠️ 제작법 수: $recipes_count"
        echo "  🎯 아이템 수: $items_count"
        echo "  🌐 언어 매핑: $mappings_added개 추가"
        echo ""
        
        log_info "이제 게임 내에서 AI 어시스턴트를 사용할 수 있습니다!"
        return 0
    fi
}

# 메인 함수
main() {
    # 설정 로드
    load_config
    
    # 인수 확인
    if [ $# -eq 0 ]; then
        log_error "모드팩명을 지정해주세요"
        show_help
        exit 1
    fi
    
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --list|-l)
            list_modpacks
            exit 0
            ;;
        *)
            local modpack_name="$1"
            local version="$2"
            
            if [ -z "$modpack_name" ]; then
                log_error "모드팩명을 지정해주세요"
                show_help
                exit 1
            fi
            
            switch_modpack "$modpack_name" "$version"
            exit $?
            ;;
    esac
}

# 스크립트 실행
main "$@" 