#!/bin/bash

# 마인크래프트 모드팩 AI - 모드팩 변경 스크립트
# 사용법: ./modpack_switch.sh [모드팩명] [버전]

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 설정 파일 경로
CONFIG_FILE="$HOME/minecraft-ai-backend/.env"
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
    echo "  $0                    # 설정 파일에서 모드팩 정보 읽어서 분석"
    echo "  $0 <모드팩명>         # 지정한 모드팩 분석 (버전 자동 추출 시도)"
    echo "  $0 <모드팩명> <버전>  # 지정한 모드팩과 버전으로 분석"
    echo "  $0 --list             # 사용 가능한 모드팩 목록 표시"
    echo "  $0 --help             # 이 도움말 표시"
    echo ""
    echo "옵션:"
    echo "  <모드팩명>    분석할 모드팩의 이름"
    echo "  <버전>        모드팩 버전 (선택사항)"
    echo "  --list        사용 가능한 모드팩 목록 표시"
    echo "  --help        이 도움말 표시"
    echo ""
    echo "설정 파일 (.env)에서 읽는 정보:"
    echo "  CURRENT_MODPACK_NAME    현재 사용할 모드팩 이름"
    echo "  CURRENT_MODPACK_VERSION 현재 사용할 모드팩 버전"
    echo "  MODPACK_UPLOAD_DIR      모드팩 파일 디렉토리"
    echo ""
    echo "예시:"
    echo "  $0                      # 설정 파일에서 읽어서 분석"
    echo "  $0 CreateModpack        # CreateModpack 분석"
    echo "  $0 FTBRevelation 1.0.0  # FTBRevelation v1.0.0 분석"
    echo ""
    echo "설정:"
    echo "  모드팩 디렉토리: $MODPACKS_DIR"
    echo "  백엔드 URL: $BACKEND_URL"
}

# 설정 파일에서 모드팩 정보 읽기
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        # 모드팩 디렉토리 읽기
        local config_modpacks_dir=$(grep "^MODPACK_UPLOAD_DIR=" "$CONFIG_FILE" | cut -d'=' -f2)
        if [ -n "$config_modpacks_dir" ]; then
            MODPACKS_DIR="$config_modpacks_dir"
        fi
        
        # 현재 모드팩 정보 읽기
        CURRENT_MODPACK_NAME=$(grep "^CURRENT_MODPACK_NAME=" "$CONFIG_FILE" | cut -d'=' -f2)
        CURRENT_MODPACK_VERSION=$(grep "^CURRENT_MODPACK_VERSION=" "$CONFIG_FILE" | cut -d'=' -f2)
        
        log_info "설정 파일에서 정보 로드:"
        log_info "  모드팩 디렉토리: $MODPACKS_DIR"
        if [ -n "$CURRENT_MODPACK_NAME" ]; then
            log_info "  현재 모드팩: $CURRENT_MODPACK_NAME"
        fi
        if [ -n "$CURRENT_MODPACK_VERSION" ]; then
            log_info "  현재 버전: $CURRENT_MODPACK_VERSION"
        fi
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
            local filename=$(basename "$file")
            local size=$(du -h "$file" | cut -f1)
            echo "  📦 $filename ($size)"
            found=true
        fi
    done
    
    if [ "$found" = false ]; then
        log_warning "모드팩 파일을 찾을 수 없습니다: $MODPACKS_DIR"
        log_info "모드팩 파일을 업로드하세요: $MODPACKS_DIR"
    fi
}

# 모드팩 파일에서 버전 추출 시도
extract_version_from_file() {
    local modpack_file="$1"
    local modpack_name="$2"
    
    # 파일명에서 버전 추출 시도
    local filename=$(basename "$modpack_file")
    
    # 패턴 1: modpack_name_version.zip
    if [[ "$filename" =~ ${modpack_name}_([0-9]+\.[0-9]+(\.[0-9]+)?)\.(zip|jar)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    
    # 패턴 2: modpack_name-version.zip
    if [[ "$filename" =~ ${modpack_name}-([0-9]+\.[0-9]+(\.[0-9]+)?)\.(zip|jar)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    
    # 패턴 3: modpack_name version.zip
    if [[ "$filename" =~ ${modpack_name}[[:space:]]+([0-9]+\.[0-9]+(\.[0-9]+)?)\.(zip|jar)$ ]]; then
        echo "${BASH_REMATCH[1]}"
        return 0
    fi
    
    return 1
}

# 모드팩 파일 찾기
find_modpack_file() {
    local modpack_name="$1"
    local version="$2"
    
    # 버전이 지정되지 않은 경우, 파일명에서 추출 시도
    if [ -z "$version" ]; then
        # 가능한 파일명 패턴들 (버전 없음)
        local patterns=(
            "$MODPACKS_DIR/${modpack_name}.zip"
            "$MODPACKS_DIR/${modpack_name}.jar"
            "$MODPACKS_DIR/${modpack_name,,}.zip"  # 소문자
            "$MODPACKS_DIR/${modpack_name,,}.jar"
        )
        
        for pattern in "${patterns[@]}"; do
            if [ -f "$pattern" ]; then
                # 파일에서 버전 추출 시도
                local extracted_version=$(extract_version_from_file "$pattern" "$modpack_name")
                if [ -n "$extracted_version" ]; then
                    log_info "파일명에서 버전 추출: $extracted_version"
                    version="$extracted_version"
                else
                    log_warning "버전을 추출할 수 없어 기본값(1.0)을 사용합니다"
                    version="1.0"
                fi
                echo "$pattern"
                return 0
            fi
        done
    else
        # 버전이 지정된 경우
        local patterns=(
            "$MODPACKS_DIR/${modpack_name}_${version}.zip"
            "$MODPACKS_DIR/${modpack_name}_${version}.jar"
            "$MODPACKS_DIR/${modpack_name}-${version}.zip"
            "$MODPACKS_DIR/${modpack_name}-${version}.jar"
            "$MODPACKS_DIR/${modpack_name,,}_${version}.zip"  # 소문자
            "$MODPACKS_DIR/${modpack_name,,}_${version}.jar"
            "$MODPACKS_DIR/${modpack_name,,}-${version}.zip"
            "$MODPACKS_DIR/${modpack_name,,}-${version}.jar"
        )
        
        for pattern in "${patterns[@]}"; do
            if [ -f "$pattern" ]; then
                echo "$pattern"
                return 0
            fi
        done
    fi
    
    return 1
}

# 모드팩 분석 실행
analyze_modpack() {
    local modpack_name="$1"
    local version="${2:-1.0}"
    
    log_info "모드팩 분석 시작: $modpack_name v$version"
    
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
    log_info "백엔드에 모드팩 분석 요청 중..."
    
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
        log_error "모드팩 분석 실패: $error_msg"
        return 1
    else
        log_success "모드팩 분석이 완료되었습니다!"
        
        # 응답에서 상세 정보 추출
        local mods_count=$(echo "$response" | grep -o '"mods_count":[0-9]*' | cut -d':' -f2)
        local recipes_count=$(echo "$response" | grep -o '"recipes_count":[0-9]*' | cut -d':' -f2)
        local items_count=$(echo "$response" | grep -o '"items_count":[0-9]*' | cut -d':' -f2)
        local mappings_added=$(echo "$response" | grep -o '"language_mappings_added":[0-9]*' | cut -d':' -f2)
        
        echo ""
        echo "📊 분석 결과:"
        echo "  🎮 모드팩: $modpack_name v$version"
        echo "  📦 모드 수: $mods_count"
        echo "  🛠️ 제작법 수: $recipes_count"
        echo "  🎯 아이템 수: $items_count"
        echo "  🌐 언어 매핑: $mappings_added개 추가"
        echo ""
        
        # 설정 파일 업데이트
        update_config_file "$modpack_name" "$version"
        
        log_info "이제 게임 내에서 AI 어시스턴트를 사용할 수 있습니다!"
        return 0
    fi
}

# 설정 파일 업데이트
update_config_file() {
    local modpack_name="$1"
    local version="$2"
    
    if [ -f "$CONFIG_FILE" ]; then
        log_info "설정 파일 업데이트 중..."
        
        # 임시 파일 생성
        local temp_file=$(mktemp)
        
        # 기존 설정 복사하면서 모드팩 정보 업데이트
        while IFS= read -r line; do
            if [[ "$line" =~ ^CURRENT_MODPACK_NAME= ]]; then
                echo "CURRENT_MODPACK_NAME=$modpack_name" >> "$temp_file"
            elif [[ "$line" =~ ^CURRENT_MODPACK_VERSION= ]]; then
                echo "CURRENT_MODPACK_VERSION=$version" >> "$temp_file"
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$CONFIG_FILE"
        
        # 새로운 설정이 없으면 추가
        if ! grep -q "^CURRENT_MODPACK_NAME=" "$temp_file"; then
            echo "CURRENT_MODPACK_NAME=$modpack_name" >> "$temp_file"
        fi
        if ! grep -q "^CURRENT_MODPACK_VERSION=" "$temp_file"; then
            echo "CURRENT_MODPACK_VERSION=$version" >> "$temp_file"
        fi
        
        # 원본 파일 교체
        mv "$temp_file" "$CONFIG_FILE"
        log_success "설정 파일이 업데이트되었습니다"
    else
        log_warning "설정 파일이 없어 업데이트를 건너뜁니다"
    fi
}

# 메인 함수
main() {
    # 설정 로드
    load_config
    
    # 인수 확인
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --list|-l)
            list_modpacks
            exit 0
            ;;
        "")
            # 인수가 없으면 설정 파일에서 읽기
            if [ -z "$CURRENT_MODPACK_NAME" ]; then
                log_error "설정 파일에 모드팩 정보가 없습니다"
                log_info "사용법: $0 <모드팩명> [버전]"
                log_info "또는 설정 파일에 CURRENT_MODPACK_NAME을 추가하세요"
                exit 1
            fi
            
            log_info "설정 파일에서 모드팩 정보를 읽어서 분석합니다"
            analyze_modpack "$CURRENT_MODPACK_NAME" "$CURRENT_MODPACK_VERSION"
            exit $?
            ;;
        *)
            local modpack_name="$1"
            local version="$2"
            
            if [ -z "$modpack_name" ]; then
                log_error "모드팩명을 지정해주세요"
                show_help
                exit 1
            fi
            
            analyze_modpack "$modpack_name" "$version"
            exit $?
            ;;
    esac
}

# 스크립트 실행
main "$@" 