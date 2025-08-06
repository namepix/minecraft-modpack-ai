#!/bin/bash

# 마인크래프트 AI 시스템 비상 대처 스크립트
# 모드팩 서버 데이터는 절대 건드리지 않는 안전한 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_emergency() {
    echo -e "${RED}[EMERGENCY]${NC} $1"
}

# 배너 출력
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🚨 AI 시스템 비상 대처                    ║"
    echo "║                                                              ║"
    echo "║  ⚠️  모드팩 서버 데이터는 절대 건드리지 않습니다           ⚠️  ║"
    echo "║  ✅  AI 시스템만 안전하게 제어합니다                      ✅  ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 안전 체크 - 모드팩 서버 실행 상태 확인
check_modpack_servers() {
    log_info "모드팩 서버 실행 상태 확인 중..."
    
    local running_servers=()
    for server_dir in $HOME/*/; do
        if [ -f "${server_dir}start.sh" ] && [ -d "${server_dir}mods" ]; then
            local server_name=$(basename "$server_dir")
            if pgrep -f "$server_name" > /dev/null; then
                running_servers+=("$server_name")
                log_info "  🟢 $server_name: 실행 중"
            else
                log_info "  ⚪ $server_name: 중지됨"
            fi
        fi
    done
    
    if [ ${#running_servers[@]} -gt 0 ]; then
        log_success "실행 중인 모드팩 서버: ${running_servers[*]}"
        return 0
    else
        log_warning "실행 중인 모드팩 서버가 없습니다"
        return 1
    fi
}

# AI 시스템 상태 진단
diagnose_ai_system() {
    log_info "🔍 AI 시스템 상태 진단 시작..."
    echo ""
    
    local issues=0
    
    # 1. AI 백엔드 서비스 상태
    log_info "1️⃣ AI 백엔드 서비스 확인:"
    if systemctl is-active --quiet mc-ai-backend; then
        log_success "  ✅ AI 백엔드 서비스 실행 중"
    else
        log_error "  ❌ AI 백엔드 서비스 중단됨"
        ((issues++))
    fi
    
    # 2. API 응답 확인
    log_info "2️⃣ AI API 응답 확인:"
    local api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
    if [ "$api_response" = "200" ]; then
        log_success "  ✅ AI API 정상 응답 (HTTP 200)"
    else
        log_error "  ❌ AI API 응답 오류 (HTTP $api_response)"
        ((issues++))
    fi
    
    # 3. 시스템 리소스 확인
    log_info "3️⃣ 시스템 리소스 확인:"
    
    # CPU 사용률
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d',' -f1)
    if (( $(echo "$cpu_usage > 80" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "  ⚠️ CPU 사용률 높음: ${cpu_usage}%"
    else
        log_success "  ✅ CPU 사용률 정상: ${cpu_usage}%"
    fi
    
    # 메모리 사용률
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$mem_usage > 85" | bc -l 2>/dev/null || echo 0) )); then
        log_warning "  ⚠️ 메모리 사용률 높음: ${mem_usage}%"
    else
        log_success "  ✅ 메모리 사용률 정상: ${mem_usage}%"
    fi
    
    # 디스크 사용률
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    if [ "$disk_usage" -gt 90 ]; then
        log_warning "  ⚠️ 디스크 사용률 높음: ${disk_usage}%"
    else
        log_success "  ✅ 디스크 사용률 정상: ${disk_usage}%"
    fi
    
    # 4. AI 백엔드 디렉토리 확인
    log_info "4️⃣ AI 백엔드 디렉토리 확인:"
    if [ -d "$HOME/minecraft-ai-backend" ]; then
        log_success "  ✅ AI 백엔드 디렉토리 존재"
        
        # 중요 파일들 확인
        local important_files=(".env" "app.py" "chat_history.db")
        for file in "${important_files[@]}"; do
            if [ -f "$HOME/minecraft-ai-backend/$file" ]; then
                log_success "    ✅ $file 존재"
            else
                log_error "    ❌ $file 누락"
                ((issues++))
            fi
        done
    else
        log_error "  ❌ AI 백엔드 디렉토리 누락"
        ((issues++))
    fi
    
    # 5. 플러그인 파일 확인
    log_info "5️⃣ 플러그인 파일 확인:"
    local plugin_issues=0
    for server_dir in $HOME/*/; do
        if [ -f "${server_dir}start.sh" ] && [ -d "${server_dir}mods" ]; then
            local server_name=$(basename "$server_dir")
            local plugin_file="${server_dir}plugins/ModpackAI-1.0.jar"
            
            if [ -f "$plugin_file" ]; then
                log_success "    ✅ $server_name: 플러그인 설치됨"
            else
                log_warning "    ⚠️ $server_name: 플러그인 미설치"
                ((plugin_issues++))
            fi
        fi
    done
    
    if [ $plugin_issues -eq 0 ]; then
        log_success "  ✅ 모든 모드팩에 플러그인 설치됨"
    else
        log_warning "  ⚠️ $plugin_issues개 모드팩에 플러그인 미설치"
    fi
    
    echo ""
    if [ $issues -eq 0 ]; then
        log_success "🎉 진단 완료: 심각한 문제 없음"
        return 0
    else
        log_error "⚠️ 진단 완료: $issues개 문제 발견"
        return 1
    fi
}

# AI 백엔드 서비스만 재시작 (가장 안전한 방법)
restart_ai_backend() {
    log_info "🔄 AI 백엔드 서비스 재시작 중..."
    
    # 현재 모드팩 서버 상태 저장
    check_modpack_servers
    local modpack_status=$?
    
    # AI 백엔드만 재시작
    sudo systemctl restart mc-ai-backend
    sleep 3
    
    # 결과 확인
    if systemctl is-active --quiet mc-ai-backend; then
        log_success "✅ AI 백엔드 재시작 완료"
        
        # API 응답 테스트
        sleep 2
        local api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
        if [ "$api_response" = "200" ]; then
            log_success "✅ AI API 정상 작동 확인"
        else
            log_warning "⚠️ AI API 응답 확인 필요 (HTTP $api_response)"
        fi
        
        # 모드팩 서버 상태 재확인
        echo ""
        log_info "모드팩 서버 상태 재확인 중..."
        check_modpack_servers
        
        return 0
    else
        log_error "❌ AI 백엔드 재시작 실패"
        return 1
    fi
}

# AI 시스템 완전 비활성화 (모드팩 서버는 그대로 유지)
disable_ai_system() {
    log_emergency "🛑 AI 시스템 완전 비활성화 시작..."
    
    # 확인 메시지
    echo ""
    log_warning "⚠️  이 작업은 다음을 수행합니다:"
    echo "  - AI 백엔드 서비스 중지 및 비활성화"
    echo "  - 모든 모드팩에서 AI 플러그인 제거"
    echo ""
    log_success "✅ 모드팩 서버 데이터는 절대 건드리지 않습니다:"
    echo "  - world/ (월드 데이터)"
    echo "  - config/ (모드 설정)" 
    echo "  - mods/ (모드 파일)"
    echo "  - start.sh (서버 스크립트)"
    echo ""
    
    read -p "정말로 AI 시스템을 비활성화하시겠습니까? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log_info "비활성화가 취소되었습니다."
        return 0
    fi
    
    echo ""
    log_info "AI 시스템 비활성화 진행 중..."
    
    # 1. AI 백엔드 서비스 중지
    log_info "1️⃣ AI 백엔드 서비스 중지 중..."
    if systemctl is-active --quiet mc-ai-backend; then
        sudo systemctl stop mc-ai-backend
        sudo systemctl disable mc-ai-backend
        log_success "  ✅ AI 백엔드 서비스 중지됨"
    else
        log_info "  ℹ️ AI 백엔드 서비스가 이미 중지되어 있습니다"
    fi
    
    # 2. 플러그인 제거 (plugins 폴더의 AI 관련 파일만)
    log_info "2️⃣ AI 플러그인 제거 중..."
    local removed_plugins=0
    
    for server_dir in $HOME/*/; do
        if [ -f "${server_dir}start.sh" ] && [ -d "${server_dir}mods" ]; then
            local server_name=$(basename "$server_dir")
            local plugin_file="${server_dir}plugins/ModpackAI-1.0.jar"
            local plugin_config="${server_dir}plugins/ModpackAI/"
            
            # AI 플러그인 파일 제거
            if [ -f "$plugin_file" ]; then
                rm -f "$plugin_file"
                log_success "    ✅ $server_name: AI 플러그인 제거됨"
                ((removed_plugins++))
            fi
            
            # AI 플러그인 설정 폴더 제거
            if [ -d "$plugin_config" ]; then
                rm -rf "$plugin_config"
                log_success "    ✅ $server_name: AI 설정 제거됨"
            fi
        fi
    done
    
    log_success "  ✅ $removed_plugins개 모드팩에서 AI 플러그인 제거 완료"
    
    echo ""
    log_success "🎉 AI 시스템 비활성화 완료!"
    echo ""
    log_info "📋 현재 상태:"
    echo "  🟢 모드팩 서버: 영향 없음 (정상 작동)"
    echo "  🔴 AI 백엔드: 비활성화됨"
    echo "  🔴 AI 플러그인: 제거됨"
    echo ""
    log_info "💡 AI 시스템 재활성화:"
    echo "  - AI 백엔드: sudo systemctl start mc-ai-backend"
    echo "  - 플러그인: 각 모드팩 plugins 폴더에 ModpackAI-1.0.jar 복사"
    
    return 0
}

# AI 백엔드만 활성화 (플러그인은 수동으로)
enable_ai_backend() {
    log_info "🚀 AI 백엔드 활성화 중..."
    
    # 1. AI 백엔드 디렉토리 확인
    if [ ! -d "$HOME/minecraft-ai-backend" ]; then
        log_error "❌ AI 백엔드가 설치되지 않았습니다."
        log_info "먼저 ./install.sh를 실행하여 설치하세요."
        return 1
    fi
    
    # 2. 서비스 활성화
    sudo systemctl enable mc-ai-backend
    sudo systemctl start mc-ai-backend
    
    sleep 3
    
    # 3. 상태 확인
    if systemctl is-active --quiet mc-ai-backend; then
        log_success "✅ AI 백엔드 활성화 완료"
        
        # API 응답 테스트
        local api_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health 2>/dev/null || echo "000")
        if [ "$api_response" = "200" ]; then
            log_success "✅ AI API 정상 작동"
        else
            log_warning "⚠️ AI API 응답 확인 필요"
        fi
        
        echo ""
        log_info "📋 다음 단계 (선택사항):"
        echo "  - 게임 내 AI 사용을 원하면 각 모드팩에 플러그인 설치:"
        echo "    cp ~/minecraft-ai-backend/minecraft_plugin/target/ModpackAI-1.0.jar ~/enigmatica_10/plugins/"
        
    else
        log_error "❌ AI 백엔드 활성화 실패"
        log_info "로그 확인: sudo journalctl -u mc-ai-backend -n 20"
        return 1
    fi
}

# 백업에서 AI 시스템 복구
restore_ai_from_backup() {
    log_info "📦 백업에서 AI 시스템 복구 중..."
    
    # 백업 목록 확인
    local backups=($(ls -1 $HOME/minecraft-ai-backend.backup.* 2>/dev/null | sort -r))
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_error "❌ 사용 가능한 백업이 없습니다."
        return 1
    fi
    
    echo ""
    log_info "사용 가능한 백업 목록:"
    for i in "${!backups[@]}"; do
        local backup="${backups[$i]}"
        local backup_name=$(basename "$backup")
        local backup_date=$(echo "$backup_name" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
        echo "  $((i+1)). $backup_date"
    done
    
    echo ""
    read -p "복구할 백업 번호를 선택하세요 (1-${#backups[@]}): " choice
    
    if [[ ! "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#backups[@]} ]; then
        log_error "잘못된 선택입니다."
        return 1
    fi
    
    local selected_backup="${backups[$((choice-1))]}"
    log_info "선택된 백업: $(basename "$selected_backup")"
    
    # 확인
    read -p "정말로 이 백업으로 복구하시겠습니까? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log_info "복구가 취소되었습니다."
        return 0
    fi
    
    # 복구 진행
    log_info "복구 진행 중..."
    
    # 1. AI 백엔드 서비스 중지
    sudo systemctl stop mc-ai-backend 2>/dev/null || true
    
    # 2. 현재 AI 백엔드 백업 (안전장치)
    if [ -d "$HOME/minecraft-ai-backend" ]; then
        local safety_backup="$HOME/minecraft-ai-backend.safety.$(date +%Y%m%d_%H%M%S)"
        cp -r "$HOME/minecraft-ai-backend" "$safety_backup"
        log_info "현재 상태 안전 백업: $(basename "$safety_backup")"
    fi
    
    # 3. 백업에서 복구
    rm -rf "$HOME/minecraft-ai-backend"
    cp -r "$selected_backup" "$HOME/minecraft-ai-backend"
    
    # 4. 서비스 재시작
    sudo systemctl start mc-ai-backend
    sleep 3
    
    # 5. 상태 확인
    if systemctl is-active --quiet mc-ai-backend; then
        log_success "✅ 백업에서 복구 완료!"
    else
        log_error "❌ 복구 후 서비스 시작 실패"
        log_info "로그 확인: sudo journalctl -u mc-ai-backend -n 20"
        return 1
    fi
}

# 도움말 표시
show_help() {
    echo ""
    echo "🚨 마인크래프트 AI 시스템 비상 대처 스크립트"
    echo ""
    echo "사용법:"
    echo "  $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --status     전체 시스템 상태 진단"
    echo "  --restart    AI 백엔드 서비스만 재시작 (가장 안전)"
    echo "  --disable    AI 시스템 완전 비활성화 (모드팩 서버는 유지)"
    echo "  --enable     AI 백엔드만 활성화"
    echo "  --restore    백업에서 AI 시스템 복구"
    echo "  --help       이 도움말 표시"
    echo ""
    echo "🔒 안전 보장:"
    echo "  ✅ 모드팩 서버 데이터는 절대 건드리지 않습니다"
    echo "  ✅ world/, config/, mods/ 폴더는 완전히 보호됩니다"
    echo "  ✅ AI 시스템만 안전하게 제어합니다"
    echo ""
    echo "🚨 긴급 상황 대처 순서:"
    echo "  1. $0 --status     (문제 진단)"
    echo "  2. $0 --restart    (AI만 재시작)"
    echo "  3. $0 --disable    (AI 완전 비활성화)"
    echo ""
}

# 메인 함수
main() {
    print_banner
    
    case "$1" in
        --status|-s)
            check_modpack_servers
            echo ""
            diagnose_ai_system
            ;;
        --restart|-r)
            restart_ai_backend
            ;;
        --disable|-d)
            disable_ai_system
            ;;
        --enable|-e)
            enable_ai_backend
            ;;
        --restore|-b)
            restore_ai_from_backup
            ;;
        --help|-h|"")
            show_help
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"