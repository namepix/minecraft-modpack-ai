#!/bin/bash

# 🚀 마인크래프트 모드팩 AI 시스템 GCP VM 설치 스크립트
# GCP VM Debian 환경용 - namepix080@minecraft-test-modepack

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 현재 사용자 확인
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" != "namepix080" ]; then
    log_warning "이 스크립트는 namepix080 사용자용으로 최적화되어 있습니다."
    log_info "현재 사용자: $CURRENT_USER"
fi

# GCP VM 모드팩 디렉토리 목록 (실제 tree 출력 기준)
MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e" 
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

# 모드팩별 정보 (tree 출력에서 확인된 실제 정보)
declare -A MODPACK_TYPES=(
    ["enigmatica_10"]="neoforge-1.21"
    ["enigmatica_9e"]="neoforge-1.20.1"
    ["enigmatica_6"]="forge-1.16.5"
    ["integrated_MC"]="forge-1.20.1"
    ["atm10"]="neoforge-1.21"
    ["beyond_depth"]="forge-1.20.1"
    ["carpg"]="neoforge-1.21"
    ["cteserver"]="forge-1.20.1"
    ["prominence_2"]="fabric-1.20.1"
    ["mnm"]="forge-1.16.5"
    ["test"]="neoforge-1.21"
)

# 모드팩별 시작 스크립트 (실제 확인된 파일명)
declare -A START_SCRIPTS=(
    ["enigmatica_10"]="start.sh"
    ["enigmatica_9e"]="start.sh"
    ["enigmatica_6"]="start.sh"
    ["integrated_MC"]="start.sh"
    ["atm10"]="start.sh"
    ["beyond_depth"]="start.sh"
    ["carpg"]="start.sh"
    ["cteserver"]="start.sh"
    ["prominence_2"]="start.sh"
    ["mnm"]="start.sh"
    ["test"]="start.sh"
)

echo "🎮 마인크래프트 모드팩 AI 시스템 GCP VM 설치"
echo "════════════════════════════════════════════════════════"
echo ""

# 시스템 정보 확인
log_step "1. 시스템 정보 확인"
OS=$(lsb_release -si 2>/dev/null || echo "Unknown")
VERSION=$(lsb_release -sr 2>/dev/null || echo "Unknown")

if [ "$OS" != "Debian" ] && [ "$OS" != "Ubuntu" ]; then
    log_error "이 스크립트는 Debian/Ubuntu 시스템에서만 실행됩니다."
    exit 1
fi

log_success "운영체제: $OS $VERSION"
log_info "현재 사용자: $CURRENT_USER"
log_info "홈 디렉토리: $HOME"

# 기존 모드팩 확인
log_step "2. 기존 모드팩 서버 확인"
FOUND_MODPACKS=()
for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        FOUND_MODPACKS+=("$modpack")
        log_success "발견된 모드팩: $modpack (${MODPACK_TYPES[$modpack]})"
    else
        log_warning "모드팩 미발견: $modpack"
    fi
done

if [ ${#FOUND_MODPACKS[@]} -eq 0 ]; then
    log_error "설치된 모드팩을 찾을 수 없습니다."
    log_info "다음 경로에서 모드팩을 찾고 있습니다: $HOME"
    exit 1
fi

log_success "총 ${#FOUND_MODPACKS[@]}개 모드팩 발견"

# 시스템 업데이트
log_step "3. 시스템 패키지 업데이트"
sudo apt update -qq
sudo apt upgrade -y -qq

# 필수 패키지 설치
log_step "4. 필수 패키지 설치"
log_info "Java, Python, Maven 및 기타 도구 설치 중..."

sudo apt install -y -qq \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    maven \
    git \
    curl \
    wget \
    unzip \
    htop \
    tree \
    build-essential \
    pkg-config \
    libssl-dev \
    libffi-dev

# Java 버전 확인
JAVA_VERSION=$(java -version 2>&1 | head -n1 | cut -d'"' -f2)
log_success "Java 버전: $JAVA_VERSION"

# AI 백엔드 설치
log_step "5. AI 백엔드 설치"

# 백엔드 디렉토리 생성
log_info "백엔드 디렉토리 생성: $HOME/minecraft-ai-backend"
mkdir -p $HOME/minecraft-ai-backend/{logs,uploads,backups,data}

# Python 가상환경 생성
log_info "Python 가상환경 생성: $HOME/minecraft-ai-env"
python3 -m venv $HOME/minecraft-ai-env
source $HOME/minecraft-ai-env/bin/activate

# Python 패키지 설치
log_info "Python 의존성 설치 중..."
pip install --upgrade pip -q

# 프로젝트 위치 확인
PROJECT_DIR=$(pwd)
if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
    pip install -r "$PROJECT_DIR/backend/requirements.txt" -q
    log_success "Python 의존성 설치 완료"
else
    log_error "requirements.txt를 찾을 수 없습니다: $PROJECT_DIR/backend/requirements.txt"
    exit 1
fi

# 백엔드 파일 복사
log_info "백엔드 파일 복사 중..."
cp -r "$PROJECT_DIR/backend"/* $HOME/minecraft-ai-backend/

# 환경 변수 파일 설정
if [ ! -f $HOME/minecraft-ai-backend/.env ]; then
    if [ -f "$PROJECT_DIR/env.example" ]; then
        cp "$PROJECT_DIR/env.example" $HOME/minecraft-ai-backend/.env
        log_success "환경 변수 파일 생성: $HOME/minecraft-ai-backend/.env"
    else
        log_error "env.example 파일을 찾을 수 없습니다."
        exit 1
    fi
fi

# Minecraft 플러그인 빌드
log_step "6. Minecraft 플러그인 빌드"
cd "$PROJECT_DIR/minecraft_plugin"

log_info "Maven을 사용하여 플러그인 빌드 중..."

# Maven 캐시 문제 해결을 위한 정리
if [ -d "$HOME/.m2/repository" ]; then
    log_info "Maven 캐시 정리 중..."
    rm -rf "$HOME/.m2/repository"
fi

# 의존성 강제 업데이트와 함께 빌드
log_info "의존성 다운로드 및 컴파일 중..."
mvn clean package -U -Dmaven.test.skip=true

# 빌드 실패 시 상세 정보로 재시도
if [ ! -f "target/ModpackAI-1.0.jar" ]; then
    log_warning "초기 빌드 실패, 상세 로그로 재시도 중..."
    mvn clean package -X -Dmaven.test.skip=true
fi

# 실제로 생성되는 JAR 파일들 확인
SHADED_JAR="target/modpack-ai-plugin-1.0.0-shaded.jar"
ORIGINAL_JAR="target/modpack-ai-plugin-1.0.0.jar" 
MODPACK_JAR="target/ModpackAI-1.0.jar"

if [ -f "$SHADED_JAR" ]; then
    # shaded JAR 파일을 ModpackAI-1.0.jar로 복사
    cp "$SHADED_JAR" "target/ModpackAI-1.0.jar"
    log_success "플러그인 빌드 완료: target/ModpackAI-1.0.jar (from shaded)"
    PLUGIN_JAR="$PROJECT_DIR/minecraft_plugin/target/ModpackAI-1.0.jar"
elif [ -f "$ORIGINAL_JAR" ]; then
    # 원본 JAR 파일을 ModpackAI-1.0.jar로 복사
    cp "$ORIGINAL_JAR" "target/ModpackAI-1.0.jar"
    log_success "플러그인 빌드 완료: target/ModpackAI-1.0.jar (from original)"
    PLUGIN_JAR="$PROJECT_DIR/minecraft_plugin/target/ModpackAI-1.0.jar"
elif [ -f "$MODPACK_JAR" ]; then
    log_success "플러그인 빌드 완료: target/ModpackAI-1.0.jar"
    PLUGIN_JAR="$PROJECT_DIR/minecraft_plugin/target/ModpackAI-1.0.jar"
else
    log_error "플러그인 빌드 실패 - JAR 파일을 찾을 수 없습니다"
    log_info "생성된 파일들:"
    ls -la target/
    exit 1
fi

# 하이브리드 서버 설치 및 플러그인 설치
log_step "7. 모드팩별 하이브리드 서버 및 플러그인 설치"

for modpack in "${FOUND_MODPACKS[@]}"; do
    log_info "처리 중: $modpack (${MODPACK_TYPES[$modpack]})"
    
    cd "$HOME/$modpack"
    
    # plugins 디렉토리 생성
    mkdir -p plugins/ModpackAI
    
    # 플러그인 복사
    cp "$PLUGIN_JAR" plugins/
    log_info "  ✅ 플러그인 설치 완료"
    
    # 플러그인 설정 생성
    cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - $modpack

# AI 서버 설정
ai:
  server_url: "http://localhost:5000"
  modpack_name: "$modpack"
  modpack_version: "latest"

# AI 어시스턴트 아이템 설정
ai_item:
  material: "BOOK"
  name: "§6§l모드팩 AI 어시스턴트"
  lore:
    - "§7우클릭하여 AI와 대화하세요"
    - "§7모드팩 관련 질문에 답변해드립니다"
    - ""
    - "§e§l사용법:"
    - "§f- 우클릭: AI 채팅창 열기"
    - "§f- 제작법 질문 시 자동으로 표시"

# GUI 설정
gui:
  chat_title: "§6§l모드팩 AI 어시스턴트"
  chat_size: 54
  recipe_title: "§6§l제작법"
  recipe_size: 27

# 메시지 설정
messages:
  no_permission: "§c이 기능을 사용할 권한이 없습니다."
  ai_error: "§cAI 서버와 통신 중 오류가 발생했습니다."
  recipe_not_found: "§c제작법을 찾을 수 없습니다."
  item_given: "§aAI 어시스턴트 아이템을 받았습니다!"

# 권한 설정
permissions:
  require_permission: false
  node: "modpackai.use"
  admin_node: "modpackai.admin"

# 디버그 설정
debug:
  enabled: false
EOF
    
    log_info "  ✅ 플러그인 설정 생성 완료"
    
    # 하이브리드 서버 다운로드 및 설정
    modpack_type="${MODPACK_TYPES[$modpack]}"
    
    # 기존 시작 스크립트 백업
    if [ -f "${START_SCRIPTS[$modpack]}" ]; then
        cp "${START_SCRIPTS[$modpack]}" "${START_SCRIPTS[$modpack]}.backup"
        log_info "  📋 기존 시작 스크립트 백업: ${START_SCRIPTS[$modpack]}.backup"
    fi
    
    # 모드팩 타입별 하이브리드 서버 설정
    if [[ "$modpack_type" == *"neoforge"* ]]; then
        # NeoForge 하이브리드 서버 (Youer - MohistMC)
        if [ ! -f "youer-neoforge.jar" ]; then
            log_info "  📥 Youer NeoForge 하이브리드 서버 다운로드 중..."
            
            # Youer (NeoForge) 최신 버전 다운로드 시도
            if ! wget -q --timeout=30 -O youer-neoforge.jar "https://mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download"; then
                log_warning "  Youer 다운로드 실패, 대체 서버 시도 중..."
                
                # 대체: Mohist NeoForge (호환 가능)
                if ! wget -q --timeout=30 -O youer-neoforge.jar "https://mohistmc.com/api/v2/projects/mohist/versions/1.21/builds/latest/download"; then
                    log_error "  하이브리드 서버 다운로드 실패. 수동 설치 필요"
                    log_info "  다운로드 URL: https://mohistmc.com/downloads"
                    continue
                fi
            fi
        fi
        
        HYBRID_JAR="youer-neoforge.jar"
        
        # AI 지원 시작 스크립트 생성
        cat > start_with_ai.sh << 'EOFSCRIPT'
#!/bin/bash
echo "🚀 Starting modpack with AI Assistant..."

# 메모리 설정 (VM 사양에 맞게 조정)
MEMORY="-Xms4G -Xmx8G"

# JVM 최적화 옵션
JVM_ARGS="$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 \
  -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 \
  -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 \
  -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1"

echo "Starting with Youer (NeoForge + Paper/Bukkit Hybrid)..."
java $JVM_ARGS -jar youer-neoforge.jar nogui
EOFSCRIPT

    elif [[ "$modpack_type" == *"forge"* ]]; then
        # Forge 하이브리드 서버 (Mohist)
        if [[ "$modpack_type" == *"1.16.5"* ]]; then
            if [ ! -f "mohist-1.16.5.jar" ]; then
                log_info "  📥 Mohist 1.16.5 하이브리드 서버 다운로드 중..."
                if ! wget -q --timeout=30 -O mohist-1.16.5.jar "https://mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"; then
                    log_error "  Mohist 1.16.5 다운로드 실패"
                    log_info "  수동 다운로드: https://mohistmc.com/downloads"
                    continue
                fi
            fi
            HYBRID_JAR="mohist-1.16.5.jar"
        else
            if [ ! -f "mohist-1.20.1.jar" ]; then
                log_info "  📥 Mohist 1.20.1 하이브리드 서버 다운로드 중..."
                if ! wget -q --timeout=30 -O mohist-1.20.1.jar "https://mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"; then
                    log_error "  Mohist 1.20.1 다운로드 실패"
                    log_info "  수동 다운로드: https://mohistmc.com/downloads"
                    continue
                fi
            fi
            HYBRID_JAR="mohist-1.20.1.jar"
        fi
        
        # AI 지원 시작 스크립트 생성
        cat > start_with_ai.sh << EOFSCRIPT
#!/bin/bash
echo "🚀 Starting modpack with AI Assistant..."

# 메모리 설정
MEMORY="-Xms4G -Xmx8G"

# JVM 최적화 옵션
JVM_ARGS="\$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \\
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions \\
  -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 \\
  -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \\
  -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 \\
  -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15"

echo "Starting with Mohist (Forge + Bukkit Hybrid)..."
java \$JVM_ARGS -jar $HYBRID_JAR nogui
EOFSCRIPT

    elif [[ "$modpack_type" == *"fabric"* ]]; then
        # Fabric 하이브리드 서버 (CardBoard)
        if [ ! -f "cardboard.jar" ]; then
            log_info "  📥 CardBoard Fabric 하이브리드 서버 다운로드 중..."
            
            # CardBoard 다운로드 시도 (여러 URL)
            if ! wget -q --timeout=30 -O cardboard.jar "https://github.com/CardboardPowered/cardboard/releases/latest/download/cardboard-1.20.1.jar"; then
                log_warning "  GitHub에서 CardBoard 다운로드 실패, 대체 URL 시도 중..."
                
                # 대체 URL 시도
                if ! wget -q --timeout=30 -O cardboard.jar "https://github.com/CardboardPowered/cardboard/releases/download/1.20.1-4.0.6/cardboard-1.20.1-4.0.6.jar"; then
                    log_error "  CardBoard 다운로드 실패. 수동 설치 필요"
                    log_info "  다운로드 URL: https://github.com/CardboardPowered/cardboard/releases"
                    continue
                fi
            fi
        fi
        
        HYBRID_JAR="cardboard.jar"
        
        # AI 지원 시작 스크립트 생성
        cat > start_with_ai.sh << 'EOFSCRIPT'
#!/bin/bash
echo "🚀 Starting modpack with AI Assistant..."

# 메모리 설정
MEMORY="-Xms4G -Xmx6G"

# JVM 최적화 옵션
JVM_ARGS="$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions"

echo "Starting with CardBoard (Fabric + Bukkit Hybrid)..."
java $JVM_ARGS -jar cardboard.jar nogui
EOFSCRIPT

    fi
    
    chmod +x start_with_ai.sh
    log_info "  ✅ AI 지원 시작 스크립트 생성: start_with_ai.sh"
    log_success "모드팩 '$modpack' 설정 완료"
    echo ""
done

# systemd 서비스 설정
log_step "8. systemd 서비스 설정"

sudo tee /etc/systemd/system/mc-ai-backend.service > /dev/null <<EOF
[Unit]
Description=Minecraft Modpack AI Backend
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$HOME/minecraft-ai-backend
Environment=PATH=$HOME/minecraft-ai-env/bin
ExecStart=$HOME/minecraft-ai-env/bin/python $HOME/minecraft-ai-backend/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable mc-ai-backend
log_success "systemd 서비스 등록 완료"

# 관리 스크립트 설치
log_step "9. 관리 스크립트 설치"

# modpack_switch 스크립트
if [ -f "$PROJECT_DIR/modpack_switch.sh" ]; then
    sudo cp "$PROJECT_DIR/modpack_switch.sh" /usr/local/bin/modpack_switch
    sudo chmod +x /usr/local/bin/modpack_switch
    log_success "modpack_switch 스크립트 설치 완료"
fi

# 모니터링 스크립트
if [ -f "$PROJECT_DIR/monitor.sh" ]; then
    sudo cp "$PROJECT_DIR/monitor.sh" /usr/local/bin/mc-ai-monitor  
    sudo chmod +x /usr/local/bin/mc-ai-monitor
    log_success "모니터링 스크립트 설치 완료"
fi

# 방화벽 설정
log_step "10. 방화벽 설정"
log_info "UFW 방화벽 규칙 설정 중..."

sudo ufw allow 22/tcp      # SSH
sudo ufw allow 25565/tcp   # Minecraft 기본 포트
sudo ufw allow 5000/tcp    # AI 백엔드
sudo ufw --force enable > /dev/null 2>&1

log_success "방화벽 설정 완료"

# 설치 완료 및 다음 단계 안내
log_step "11. 설치 완료"

echo ""
echo "🎉 마인크래프트 모드팩 AI 시스템 설치 완료!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📊 설치 요약:"
echo "  🏠 AI 백엔드: $HOME/minecraft-ai-backend"
echo "  🐍 Python 환경: $HOME/minecraft-ai-env"  
echo "  🎮 설정된 모드팩: ${#FOUND_MODPACKS[@]}개"
echo "  ⚙️  systemd 서비스: mc-ai-backend"
echo ""
echo "📋 다음 단계 (필수):"
echo ""
echo "1️⃣ API 키 설정:"
echo "   nano $HOME/minecraft-ai-backend/.env"
echo "   # Google AI Studio에서 API 키 발급: https://aistudio.google.com/app/apikey"
echo ""
echo "2️⃣ AI 백엔드 서비스 시작:"
echo "   sudo systemctl start mc-ai-backend"
echo "   sudo systemctl status mc-ai-backend"
echo ""
echo "3️⃣ 백엔드 상태 확인:"
echo "   curl http://localhost:5000/health"
echo ""
echo "4️⃣ 모드팩 서버 시작 (AI 지원):"
echo "   cd ~/enigmatica_10"
echo "   ./start_with_ai.sh"
echo ""
echo "5️⃣ 게임 내 테스트:"
echo "   /modpackai help"
echo "   /give @p book 1"
echo "   # 책을 들고 우클릭하여 AI 채팅 테스트"
echo ""
echo "🛠️ 유용한 명령어:"
echo "  modpack_switch --list          # 사용 가능한 모드팩 목록"
echo "  mc-ai-monitor                  # 시스템 모니터링"
echo "  sudo journalctl -u mc-ai-backend -f  # 백엔드 로그 확인"
echo ""
echo "📚 문서:"
echo "  - guides/01_ADMIN_SETUP.md     # 상세 설치 가이드"
echo "  - guides/03_GAME_COMMANDS.md   # 게임 내 사용법"
echo "  - QUICK_START.md               # 빠른 시작 가이드"
echo ""

# API 키 설정 프롬프트
echo -e "${CYAN}💡 지금 바로 API 키를 설정하시겠습니까? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    log_info "환경 변수 파일을 엽니다..."
    echo "Google API 키를 다음 위치에 입력하세요:"
    echo "GOOGLE_API_KEY=your-actual-api-key"
    echo ""
    echo "저장: Ctrl+X → Y → Enter"
    echo ""
    sleep 3
    nano "$HOME/minecraft-ai-backend/.env"
    
    echo ""
    log_info "백엔드 서비스를 시작합니다..."
    sudo systemctl start mc-ai-backend
    sleep 3
    
    log_info "백엔드 상태를 확인합니다..."
    sudo systemctl status mc-ai-backend --no-pager
    
    echo ""
    log_info "API 상태를 테스트합니다..."
    if curl -s http://localhost:5000/health > /dev/null; then
        log_success "✅ AI 백엔드가 정상적으로 실행 중입니다!"
        echo ""
        echo "🎮 이제 모드팩 서버를 시작하세요:"
        echo "   cd ~/enigmatica_10"
        echo "   ./start_with_ai.sh"
    else
        log_warning "⚠️ 백엔드 연결에 문제가 있습니다. API 키를 확인하세요."
        echo "문제 해결: sudo journalctl -u mc-ai-backend -f"
    fi
fi

echo ""
echo "🚀 설치가 완료되었습니다. 즐거운 모드팩 플레이 되세요!"
echo ""