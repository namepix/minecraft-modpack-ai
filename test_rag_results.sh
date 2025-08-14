#!/bin/bash

# 🔍 RAG 결과 빠른 테스트 스크립트
# RAG 인덱스 구축 후 검색 결과를 즉시 확인하는 도구

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 백엔드 서버 확인
check_backend() {
    log_info "백엔드 서버 상태 확인 중..."
    
    if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
        log_error "백엔드 서버가 실행되지 않음 (http://localhost:5000)"
        echo "백엔드 서버를 시작하세요:"
        echo "  cd $BACKEND_DIR"
        echo "  python app.py"
        exit 1
    fi
    
    log_success "백엔드 서버 연결 확인"
}

# RAG 상태 확인
check_rag_status() {
    log_info "RAG 시스템 상태 확인 중..."
    
    response=$(curl -s http://localhost:5000/gcp-rag/status)
    if echo "$response" | grep -q '"gcp_rag_available": true'; then
        log_success "GCP RAG 시스템 활성화됨"
        return 0
    else
        log_warning "GCP RAG 시스템 비활성화됨"
        return 1
    fi
}

# 등록된 모드팩 목록
list_modpacks() {
    log_info "등록된 모드팩 목록 조회 중..."
    
    response=$(curl -s http://localhost:5000/gcp-rag/modpacks)
    
    if echo "$response" | grep -q '"success": true'; then
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
modpacks = data.get('modpacks', [])
if modpacks:
    print('📦 등록된 모드팩:')
    for i, mp in enumerate(modpacks, 1):
        name = mp.get('modpack_name', 'Unknown')
        version = mp.get('modpack_version', '1.0.0')
        count = mp.get('document_count', 0)
        print(f'  {i}. {name} v{version} ({count}개 문서)')
else:
    print('📦 등록된 모드팩이 없습니다.')
"
    else
        log_error "모드팩 목록 조회 실패"
    fi
}

# RAG 검색 테스트
test_search() {
    local modpack_name="$1"
    local modpack_version="$2"
    local query="$3"
    
    log_test "검색 테스트: '$query' in $modpack_name v$modpack_version"
    
    response=$(curl -s -X POST http://localhost:5000/gcp-rag/search \
        -H "Content-Type: application/json" \
        -d "{
            \"query\": \"$query\",
            \"modpack_name\": \"$modpack_name\",
            \"modpack_version\": \"$modpack_version\",
            \"top_k\": 3,
            \"min_score\": 0.6
        }")
    
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        results = data.get('results', [])
        print(f'    🔍 검색 결과: {len(results)}개')
        
        for i, result in enumerate(results[:3], 1):
            similarity = result.get('similarity', 0)
            doc_type = result.get('doc_type', 'unknown')
            text = result.get('text', '')[:100] + '...'
            print(f'    {i}. [{doc_type}] 유사도: {similarity:.3f}')
            print(f'       {text}')
    else:
        print(f'    ❌ 검색 실패: {data.get(\"error\", \"unknown error\")}')
except Exception as e:
    print(f'    ❌ 응답 파싱 실패: {e}')
"
    echo
}

# 채팅 테스트
test_chat() {
    local modpack_name="$1"
    local modpack_version="$2"
    local message="$3"
    
    log_test "채팅 테스트: '$message' in $modpack_name v$modpack_version"
    
    response=$(curl -s -X POST http://localhost:5000/chat \
        -H "Content-Type: application/json" \
        -d "{
            \"message\": \"$message\",
            \"player_uuid\": \"test-user\",
            \"modpack_name\": \"$modpack_name\",
            \"modpack_version\": \"$modpack_version\"
        }")
    
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        rag_info = data.get('rag', {})
        model = data.get('model', 'unknown')
        response_text = data.get('response', '')
        
        print(f'    🤖 AI 모델: {model}')
        print(f'    📊 RAG 사용: {\"Yes\" if rag_info.get(\"used\") else \"No\"}')
        print(f'    🎯 RAG 히트: {rag_info.get(\"hits\", 0)}개')
        print(f'    📝 응답 길이: {len(response_text)}자')
        print(f'    💬 응답 미리보기: {response_text[:150]}...')
    else:
        print(f'    ❌ 채팅 실패: {data.get(\"error\", \"unknown error\")}')
except Exception as e:
    print(f'    ❌ 응답 파싱 실패: {e}')
"
    echo
}

# 대화형 테스트
interactive_test() {
    echo
    echo "🎮 대화형 RAG 테스트"
    echo "===================="
    
    # 모드팩 선택
    echo "사용 가능한 모드팩 목록:"
    list_modpacks
    echo
    
    read -p "테스트할 모드팩 이름: " modpack_name
    read -p "모드팩 버전 (기본: 1.0.0): " modpack_version
    modpack_version=${modpack_version:-1.0.0}
    
    # Enigmatica 10 전용 테스트 쿼리
    if [[ "$modpack_name" == *"enigmatica"* ]]; then
        test_queries=(
            "thermal expansion machine"
            "create contraption setup"
            "mekanism reactor"
            "applied energistics storage"
            "automation guide"
            "power generation"
            "iron ingot recipe"
        )
    # Prominence 2 전용 테스트 쿼리  
    elif [[ "$modpack_name" == *"prominence"* ]]; then
        test_queries=(
            "tinkers construct weapon"
            "blood magic ritual"
            "botania mana setup"
            "thaumcraft research"
            "combat equipment"
            "magic progression"
            "diamond sword recipe"
        )
    else
        # 일반 테스트 쿼리
        test_queries=(
            "iron ingot recipe"
            "crafting table"
            "furnace recipe"
            "chest recipe"
            "diamond gear"
        )
    fi
    
    echo
    echo "🔍 검색 테스트 시작..."
    echo "----------------------"
    
    for query in "${test_queries[@]}"; do
        test_search "$modpack_name" "$modpack_version" "$query"
    done
    
    echo
    echo "💬 채팅 테스트 시작..."
    echo "--------------------"
    
    chat_messages=(
        "철 블록을 만드는 방법을 알려줘"
        "이 모드팩에서 가장 효율적인 전력 생산 방법은?"
        "자동화 시스템을 구축하려면 어떤 모드를 사용해야 해?"
    )
    
    for message in "${chat_messages[@]}"; do
        test_chat "$modpack_name" "$modpack_version" "$message"
    done
}

# 빠른 테스트 (미리 정의된 모드팩)
quick_test() {
    local modpack_name="$1"
    local modpack_version="${2:-1.0.0}"
    
    echo
    echo "⚡ 빠른 테스트: $modpack_name v$modpack_version"
    echo "============================================"
    
    # 기본 검색 테스트
    basic_queries=("iron ingot" "crafting table" "furnace")
    
    for query in "${basic_queries[@]}"; do
        test_search "$modpack_name" "$modpack_version" "$query"
    done
    
    # 기본 채팅 테스트
    test_chat "$modpack_name" "$modpack_version" "철 블록 만드는 방법 알려줘"
}

# 도움말
show_help() {
    cat << EOF
🔍 RAG 결과 빠른 테스트 도구

사용법:
  $0 [명령어] [옵션]

명령어:
  interactive          대화형 테스트 모드
  quick <모드팩_이름>    빠른 테스트 (기본 쿼리)
  search <모드팩> <버전> <쿼리>  단일 검색 테스트
  chat <모드팩> <버전> <메시지>  단일 채팅 테스트
  status               RAG 시스템 상태 확인
  list                 등록된 모드팩 목록
  help                 도움말 표시

예시:
  $0 interactive
  $0 quick enigmatica_10
  $0 search "enigmatica_10" "1.0.0" "thermal expansion"
  $0 chat "prominence_2" "1.0.0" "how to make iron block"
  $0 status
  $0 list

참고:
  - 백엔드 서버가 실행 중이어야 합니다 (http://localhost:5000)
  - GCP RAG가 설정되어야 정확한 결과를 얻을 수 있습니다
  - Enigmatica 10과 Prominence 2에 최적화된 테스트 쿼리를 제공합니다
EOF
}

# 메인 함수
main() {
    echo "🔍 RAG 결과 빠른 테스트 도구"
    echo "============================"
    
    # 백엔드 확인
    check_backend
    
    case "${1:-interactive}" in
        "interactive")
            check_rag_status
            interactive_test
            ;;
        "quick")
            if [ $# -lt 2 ]; then
                log_error "사용법: $0 quick <모드팩_이름> [버전]"
                exit 1
            fi
            check_rag_status
            quick_test "$2" "${3:-1.0.0}"
            ;;
        "search")
            if [ $# -lt 4 ]; then
                log_error "사용법: $0 search <모드팩> <버전> <쿼리>"
                exit 1
            fi
            test_search "$2" "$3" "$4"
            ;;
        "chat")
            if [ $# -lt 4 ]; then
                log_error "사용법: $0 chat <모드팩> <버전> <메시지>"
                exit 1
            fi
            test_chat "$2" "$3" "$4"
            ;;
        "status")
            check_rag_status
            ;;
        "list")
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
    
    echo
    log_success "테스트 완료!"
}

# 스크립트 실행
main "$@"