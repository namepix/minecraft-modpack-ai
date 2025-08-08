#!/bin/bash

# 🔧 하이브리드 서버 자동 설치 스크립트
# GCP VM의 모든 모드팩에 Bukkit 호환성 추가

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# GCP VM 모드팩 목록
MODPACKS=(
    "enigmatica_10:neoforge-1.21"
    "enigmatica_9e:neoforge-1.20.1" 
    "enigmatica_6:forge-1.16.5"
    "integrated_MC:forge-1.20.1"
    "atm10:neoforge-1.21"
    "beyond_depth:forge-1.20.1"
    "carpg:neoforge-1.21"
    "cteserver:forge-1.20.1"
    "prominence_2:fabric-1.20.1"
    "mnm:forge-1.16.5"
    "test:neoforge-1.21"
)

echo "🔧 하이브리드 서버 자동 설치 시작"
echo "════════════════════════════════════════"
echo ""

# 플러그인 JAR 파일 확인
if [ ! -f "minecraft_plugin/target/ModpackAI-1.0.jar" ]; then
    log_error "플러그인 JAR 파일을 찾을 수 없습니다."
    log_info "먼저 다음 명령어로 플러그인을 빌드하세요:"
    log_info "cd minecraft_plugin && mvn clean package"
    exit 1
fi

PLUGIN_JAR="$(pwd)/minecraft_plugin/target/ModpackAI-1.0.jar"
log_success "플러그인 JAR 확인: $PLUGIN_JAR"

# 각 모드팩 처리
for entry in "${MODPACKS[@]}"; do
    modpack_name="${entry%%:*}"
    modpack_type="${entry##*:}"
    
    if [ ! -d "$HOME/$modpack_name" ]; then
        log_warning "모드팩 디렉토리를 찾을 수 없습니다: $HOME/$modpack_name"
        continue
    fi
    
    log_info "처리 중: $modpack_name ($modpack_type)"
    cd "$HOME/$modpack_name"
    
    # plugins 디렉토리 생성
    mkdir -p plugins/ModpackAI
    
    # 플러그인 설치
    cp "$PLUGIN_JAR" plugins/
    
    # 플러그인 설정 생성
    cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - $modpack_name

ai:
  server_url: "http://localhost:5000"
  modpack_name: "$modpack_name"
  modpack_version: "latest"

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

gui:
  chat_title: "§6§l모드팩 AI 어시스턴트"
  chat_size: 54
  recipe_title: "§6§l제작법"
  recipe_size: 27

messages:
  no_permission: "§c이 기능을 사용할 권한이 없습니다."
  ai_error: "§cAI 서버와 통신 중 오류가 발생했습니다."
  recipe_not_found: "§c제작법을 찾을 수 없습니다."
  item_given: "§aAI 어시스턴트 아이템을 받았습니다!"

permissions:
  require_permission: false
  node: "modpackai.use"
  admin_node: "modpackai.admin"

debug:
  enabled: false
EOF
    
    # 기존 시작 스크립트 백업
    if [ -f "start.sh" ]; then
        if [ ! -f "start.sh.backup" ]; then
            cp start.sh start.sh.backup
            log_info "  📋 기존 시작 스크립트 백업됨"
        fi
    fi
    
    # 하이브리드 서버 설치
    if [[ "$modpack_type" == *"neoforge"* ]]; then
        # NeoForge - Youer (MohistMC) 사용
        if [ ! -f "youer-neoforge.jar" ]; then
            log_info "  📥 Youer NeoForge 하이브리드 서버 다운로드..."
            
            # Youer (NeoForge) 최신 버전 다운로드 시도
            if ! wget -q --timeout=30 --show-progress -O youer-neoforge.jar "https://api.mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download"; then
                log_warning "  Youer 다운로드 실패, Mohist NeoForge로 대체 시도..."
                
                # 대체: Mohist NeoForge
                if ! wget -q --timeout=30 --show-progress -O youer-neoforge.jar "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.21/builds/latest/download"; then
                    log_error "  하이브리드 서버 다운로드 실패"
                    continue
                fi
            fi
        fi
        
        # AI 지원 시작 스크립트 (여러 후보 JAR 자동 감지)
        cat > start_with_ai.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (NeoForge Hybrid)..."

# GCP VM 사양에 맞는 메모리 설정 (총 16GB 기준)
MEMORY="-Xms6G -Xmx10G"

# JVM 최적화 파라미터
JVM_OPTS="$MEMORY \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:+AlwaysPreTouch \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 \
  -XX:G1HeapWastePercent=5 \
  -XX:G1MixedGCCountTarget=4 \
  -XX:InitiatingHeapOccupancyPercent=15 \
  -XX:G1MixedGCLiveThresholdPercent=90 \
  -XX:G1RSetUpdatingPauseTimePercent=5 \
  -XX:SurvivorRatio=32 \
  -XX:+PerfDisableSharedMem \
  -XX:MaxTenuringThreshold=1"

echo "Java version: $(java -version 2>&1 | head -n1)"
echo "Memory: $MEMORY"
echo "Starting server..."

# 후보 JAR 자동 탐지 순서: youer-neoforge.jar, neoforge-hybrid.jar, arclight-neoforge*.jar
JAR_CANDIDATES=(
  "youer-neoforge.jar"
  "neoforge-hybrid.jar"
  $(ls -1 arclight-neoforge-*.jar 2>/dev/null | head -n1)
)

SELECTED_JAR=""
for jf in "${JAR_CANDIDATES[@]}"; do
  if [ -n "$jf" ] && [ -f "$jf" ] && [ $(stat -c%s "$jf" 2>/dev/null) -gt 1000 ]; then
    SELECTED_JAR="$jf"
    break
  fi
done

if [ -z "$SELECTED_JAR" ]; then
  echo "❌ 하이브리드 서버 JAR을 찾을 수 없습니다 (youer-neoforge.jar / neoforge-hybrid.jar / arclight-neoforge-*.jar)."
  echo "   파일명을 확인하거나 수동 설치 스크립트를 사용하세요: manual_install_hybrid.sh"
  exit 1
fi

echo "Using JAR: $SELECTED_JAR"
java $JVM_OPTS -jar "$SELECTED_JAR" nogui
EOF
        
    elif [[ "$modpack_type" == *"forge-1.16.5"* ]]; then
        # Forge 1.16.5 - Mohist 사용
        if [ ! -f "mohist-1.16.5.jar" ]; then
            log_info "  📥 Mohist 1.16.5 하이브리드 서버 다운로드..."
            if ! wget -q --timeout=30 --show-progress -O mohist-1.16.5.jar \
                "https://mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"; then
                log_error "  Mohist 1.16.5 다운로드 실패"
                continue
            fi
        fi
        
        cat > start_with_ai.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (Mohist 1.16.5)..."

MEMORY="-Xms4G -Xmx8G"

JVM_OPTS="$MEMORY \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:+AlwaysPreTouch \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M \
  -XX:G1ReservePercent=20 \
  -XX:G1HeapWastePercent=5"

echo "Java version: $(java -version 2>&1 | head -n1)"
echo "Memory: $MEMORY"
echo "Starting server..."

# 후보 자동 탐지: mohist-1.16.5.jar, mohist*.jar
JAR_CANDIDATES=(
  "mohist-1.16.5.jar"
  $(ls -1 mohist-*.jar 2>/dev/null | head -n1)
)

SELECTED_JAR=""
for jf in "${JAR_CANDIDATES[@]}"; do
  if [ -n "$jf" ] && [ -f "$jf" ] && [ $(stat -c%s "$jf" 2>/dev/null) -gt 1000 ]; then
    SELECTED_JAR="$jf"
    break
  fi
done

if [ -z "$SELECTED_JAR" ]; then
  echo "❌ Mohist JAR을 찾을 수 없습니다."
  exit 1
fi

echo "Using JAR: $SELECTED_JAR"
java $JVM_OPTS -jar "$SELECTED_JAR" nogui
EOF
        
    elif [[ "$modpack_type" == *"forge-1.20.1"* ]]; then
        # Forge 1.20.1 - Mohist 사용
        if [ ! -f "mohist-1.20.1.jar" ]; then
            log_info "  📥 Mohist 1.20.1 하이브리드 서버 다운로드..."
            if ! wget -q --timeout=30 --show-progress -O mohist-1.20.1.jar \
                "https://mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"; then
                log_error "  Mohist 1.20.1 다운로드 실패"
                continue
            fi
        fi
        
        cat > start_with_ai.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (Mohist 1.20.1)..."

MEMORY="-Xms4G -Xmx8G"

JVM_OPTS="$MEMORY \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+DisableExplicitGC \
  -XX:+AlwaysPreTouch \
  -XX:G1NewSizePercent=30 \
  -XX:G1MaxNewSizePercent=40 \
  -XX:G1HeapRegionSize=8M"

echo "Java version: $(java -version 2>&1 | head -n1)"
echo "Memory: $MEMORY"
echo "Starting server..."

# 후보 자동 탐지: mohist-1.20.1.jar, mohist*.jar
JAR_CANDIDATES=(
  "mohist-1.20.1.jar"
  $(ls -1 mohist-*.jar 2>/dev/null | head -n1)
)

SELECTED_JAR=""
for jf in "${JAR_CANDIDATES[@]}"; do
  if [ -n "$jf" ] && [ -f "$jf" ] && [ $(stat -c%s "$jf" 2>/dev/null) -gt 1000 ]; then
    SELECTED_JAR="$jf"
    break
  fi
done

if [ -z "$SELECTED_JAR" ]; then
  echo "❌ Mohist JAR을 찾을 수 없습니다."
  exit 1
fi

echo "Using JAR: $SELECTED_JAR"
java $JVM_OPTS -jar "$SELECTED_JAR" nogui
EOF
        
    elif [[ "$modpack_type" == *"fabric"* ]]; then
        # Fabric - CardBoard 사용
        if [ ! -f "cardboard-1.20.1.jar" ] && [ ! -f "cardboard.jar" ]; then
            log_info "  📥 CardBoard Fabric 하이브리드 서버 다운로드..."
            if ! wget -q --timeout=30 --show-progress -O cardboard-1.20.1.jar \
                "https://github.com/CardboardPowered/cardboard/releases/download/1.20.1-4.0.6/cardboard-1.20.1-4.0.6.jar"; then
                log_warning "  GitHub에서 CardBoard 다운로드 실패, 대체 URL 시도..."
                if ! wget -q --timeout=30 --show-progress -O cardboard-1.20.1.jar \
                    "https://github.com/Dueris/Banner/releases/latest/download/banner-1.20.1.jar"; then
                    log_error "  CardBoard 다운로드 실패"
                    continue
                fi
            fi
        fi
        
        cat > start_with_ai.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (CardBoard Fabric)..."

MEMORY="-Xms4G -Xmx6G"

JVM_OPTS="$MEMORY \
  -XX:+UseG1GC \
  -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 \
  -XX:+UnlockExperimentalVMOptions"

echo "Java version: $(java -version 2>&1 | head -n1)"
echo "Memory: $MEMORY"
echo "Starting server..."

# 후보 자동 탐지: cardboard-1.20.1.jar, cardboard.jar, banner-*.jar
JAR_CANDIDATES=(
  "cardboard-1.20.1.jar"
  "cardboard.jar"
  $(ls -1 banner-*.jar 2>/dev/null | head -n1)
)

SELECTED_JAR=""
for jf in "${JAR_CANDIDATES[@]}"; do
  if [ -n "$jf" ] && [ -f "$jf" ] && [ $(stat -c%s "$jf" 2>/dev/null) -gt 1000 ]; then
    SELECTED_JAR="$jf"
    break
  fi
done

if [ -z "$SELECTED_JAR" ]; then
  echo "❌ Fabric 하이브리드 JAR을 찾을 수 없습니다."
  exit 1
fi

echo "Using JAR: $SELECTED_JAR"
java $JVM_OPTS -jar "$SELECTED_JAR" nogui
EOF

    fi
    
    # 실행 권한 부여
    chmod +x start_with_ai.sh
    
    log_success "✅ $modpack_name 설정 완료 ($modpack_type)"
    echo ""
done

echo ""
echo "🎉 하이브리드 서버 설치 완료!"
echo "════════════════════════════════════════"
echo ""
echo "📋 설정된 구조:"
echo "  각 모드팩 디렉토리/"
echo "  ├── plugins/ModpackAI-1.0.jar    # AI 플러그인"
echo "  ├── plugins/ModpackAI/config.yml # 플러그인 설정"
echo "  ├── [하이브리드서버].jar           # Arclight/Mohist/CardBoard"
echo "  ├── start_with_ai.sh             # AI 지원 시작 스크립트"
echo "  └── start.sh.backup             # 기존 스크립트 백업"
echo ""
echo "🚀 사용법:"
echo "  cd ~/enigmatica_10"
echo "  ./start_with_ai.sh              # AI 지원으로 서버 시작"
echo "  ./start.sh                      # 기존 방식으로 서버 시작"
echo ""
echo "⚠️  주의사항:"
echo "  - AI 백엔드가 먼저 실행되어 있어야 합니다"
echo "  - 하이브리드 서버는 처음 실행 시 시간이 오래 걸릴 수 있습니다"
echo "  - 메모리 부족 시 start_with_ai.sh에서 -Xmx 값을 조정하세요"
echo ""