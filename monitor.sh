#!/bin/bash

# Minecraft Modpack AI Assistant 모니터링 스크립트
# 성능 메트릭, 알림 기능 추가

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 알림 함수
send_notification() {
    local message="$1"
    local level="$2"
    
    # Discord Webhook (선택사항)
    if [ ! -z "$DISCORD_WEBHOOK_URL" ]; then
        curl -H "Content-Type: application/json" \
             -d "{\"content\":\"[$level] $message\"}" \
             "$DISCORD_WEBHOOK_URL" > /dev/null 2>&1
    fi
    
    # 로그 파일에 기록
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $message" >> /var/log/mc_ai_monitor.log
}

echo "=== Minecraft Modpack AI Assistant 모니터링 ==="
echo "시간: $(date)"
echo ""

# 1. 백엔드 서버 상태 확인
log_info "백엔드 서버 상태 확인 중..."
if systemctl is-active --quiet mc-ai-backend; then
    log_info "✅ 백엔드 서비스 실행 중"
else
    log_error "❌ 백엔드 서비스 중단됨"
    send_notification "백엔드 서비스가 중단되었습니다." "ERROR"
    exit 1
fi

# 2. API 응답 확인
log_info "API 응답 확인 중..."
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health || echo "000")
if [ "$API_RESPONSE" = "200" ]; then
    log_info "✅ API 정상 응답 (HTTP $API_RESPONSE)"
else
    log_error "❌ API 응답 오류 (HTTP $API_RESPONSE)"
    send_notification "API 응답에 문제가 있습니다. (HTTP $API_RESPONSE)" "ERROR"
fi

# 3. 데이터베이스 상태 확인
log_info "데이터베이스 상태 확인 중..."
DB_FILES=("chat_history.db" "recipes.db" "language_mappings.db")
for db_file in "${DB_FILES[@]}"; do
    if [ -f "$HOME/minecraft-ai-backend/$db_file" ]; then
        DB_SIZE=$(du -h "$HOME/minecraft-ai-backend/$db_file" | cut -f1)
        log_info "✅ $db_file 존재 (크기: $DB_SIZE)"
    else
        log_warn "⚠️ $db_file 없음"
        send_notification "$db_file 데이터베이스 파일이 없습니다." "WARN"
    fi
done

# 4. 플러그인 파일 확인
PLUGIN_FILES=(
    "$HOME/enigmatica_10/plugins/ModpackAI-1.0.jar"
    "$HOME/integrated_MC/plugins/ModpackAI-1.0.jar"
    "$HOME/atm10/plugins/ModpackAI-1.0.jar"
)
for plugin_file in "${PLUGIN_FILES[@]}"; do
    if [ -f "$plugin_file" ]; then
        PLUGIN_SIZE=$(du -h "$plugin_file" | cut -f1)
        log_info "✅ 플러그인 파일 존재 (경로: $plugin_file, 크기: $PLUGIN_SIZE)"
    else
        log_warn "⚠️ 플러그인 파일 없음 (경로: $plugin_file)"
        send_notification "Minecraft 플러그인 파일이 없습니다. (경로: $plugin_file)" "WARN"
    fi
done

# 5. 시스템 리소스 확인
log_info "시스템 리소스 확인 중..."

# CPU 사용률
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    log_warn "⚠️ CPU 사용률 높음: ${CPU_USAGE}%"
    send_notification "CPU 사용률이 높습니다: ${CPU_USAGE}%" "WARN"
else
    log_info "✅ CPU 사용률: ${CPU_USAGE}%"
fi

# 메모리 사용률
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    log_warn "⚠️ 메모리 사용률 높음: ${MEMORY_USAGE}%"
    send_notification "메모리 사용률이 높습니다: ${MEMORY_USAGE}%" "WARN"
else
    log_info "✅ 메모리 사용률: ${MEMORY_USAGE}%"
fi

# 디스크 사용률
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ "$DISK_USAGE" -gt 85 ]; then
    log_warn "⚠️ 디스크 사용률 높음: ${DISK_USAGE}%"
    send_notification "디스크 사용률이 높습니다: ${DISK_USAGE}%" "WARN"
else
    log_info "✅ 디스크 사용률: ${DISK_USAGE}%"
fi

# 6. 최근 로그 확인
log_info "최근 로그 확인 중..."
RECENT_ERRORS=$(journalctl -u mc-ai-backend --since "1 hour ago" | grep -i error | wc -l)
if [ "$RECENT_ERRORS" -gt 0 ]; then
    log_warn "⚠️ 최근 1시간 동안 $RECENT_ERRORS개의 오류 발생"
    send_notification "최근 1시간 동안 $RECENT_ERRORS개의 오류가 발생했습니다." "WARN"
else
    log_info "✅ 최근 1시간 동안 오류 없음"
fi

# 7. 성능 메트릭 수집
log_info "성능 메트릭 수집 중..."

# API 응답 시간
API_RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:5000/health)
if (( $(echo "$API_RESPONSE_TIME > 2.0" | bc -l) )); then
    log_warn "⚠️ API 응답 시간 느림: ${API_RESPONSE_TIME}초"
    send_notification "API 응답 시간이 느립니다: ${API_RESPONSE_TIME}초" "WARN"
else
    log_info "✅ API 응답 시간: ${API_RESPONSE_TIME}초"
fi

# 데이터베이스 크기 추이
log_info "데이터베이스 크기 추이:"
for db_file in "${DB_FILES[@]}"; do
    if [ -f "$HOME/minecraft-ai-backend/$db_file" ]; then
        DB_SIZE_BYTES=$(stat -c%s "$HOME/minecraft-ai-backend/$db_file")
        DB_SIZE_MB=$(echo "scale=2; $DB_SIZE_BYTES / 1024 / 1024" | bc)
        log_info "  - $db_file: ${DB_SIZE_MB}MB"
    fi
done

# 8. 네트워크 연결 확인
log_info "네트워크 연결 확인 중..."
if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    log_info "✅ 인터넷 연결 정상"
else
    log_error "❌ 인터넷 연결 문제"
    send_notification "인터넷 연결에 문제가 있습니다." "ERROR"
fi

echo ""
log_info "모니터링 완료 - $(date)" 