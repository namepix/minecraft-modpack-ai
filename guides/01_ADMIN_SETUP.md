# 🛠️ GCP VM 관리자를 위한 AI 모드 추가 가이드

## 📋 개요

이 가이드는 **GCP VM Debian** 환경에서 기존 마인크래프트 모드팩 서버들에 AI 어시스턴트 기능을 추가하는 방법을 상세히 설명합니다.

**⚠️ 중요**: 현재 모드팩들(Forge/NeoForge/Fabric)은 Bukkit 플러그인을 직접 지원하지 않으므로, 하이브리드 서버 솔루션을 사용합니다.

### **🎯 지원하는 모드팩들**
```
✅ enigmatica_10 (NeoForge)    ✅ enigmatica_9e (NeoForge)
✅ enigmatica_6 (Forge)        ✅ integrated_MC (Forge) 
✅ atm10 (NeoForge)           ✅ beyond_depth (Forge)
✅ carpg (NeoForge)           ✅ cteserver (Forge)
✅ prominence_2 (Fabric)      ✅ mnm (Forge)
✅ test (NeoForge)
```

---

## 🚀 방법 1: 완전 자동 설치 (권장)

### **사전 준비사항**
- ✅ GCP VM Debian 11+ 환경
- ✅ SSH 접속 가능 (`ssh namepix080@YOUR-VM-IP`)
- ✅ 기존 모드팩 서버들이 `/home/namepix080/` 경로에 설치되어 있음
- ✅ Google API 키 준비 (https://aistudio.google.com/app/apikey)
- ✅ GCP 프로젝트 ID 및 Cloud Storage 버킷 준비 (RAG 기능용)

### **1단계: 프로젝트 다운로드**

**SSH로 GCP VM에 접속 후 다음 명령어 실행:**

```bash
cd ~
# 실제 프로젝트를 다운로드하거나 파일을 전송하세요
# 예시: scp -r minecraft-modpack-ai namepix080@YOUR-VM-IP:~/
cd minecraft-modpack-ai
```

### **2단계: 자동 설치 실행**

```bash
chmod +x install.sh
./install.sh
```

**이 스크립트가 자동으로 수행하는 작업:**
- ✅ Python 3.8+ 및 필수 패키지 설치
- ✅ Java 11+ 설치 확인
- ✅ Maven 설치 및 플러그인 빌드
- ✅ AI 백엔드 디렉토리 생성 (`/home/namepix080/minecraft-ai-backend/`)
- ✅ systemd 서비스 등록
- ✅ 모든 모드팩에 하이브리드 서버 및 플러그인 설치
- ✅ 방화벽 설정 (포트 5000, 25565)

### **3단계: API 키 설정 (필수)**

**3.1 환경 변수 파일 편집**
```bash
nano $HOME/minecraft-ai-backend/.env
```

**3.2 API 키 입력**
```env
# 🌟 Google API 키 (Gemini 2.5 Pro용, 필수)
GOOGLE_API_KEY=your-actual-google-api-key

# 📖 백업 모델 API 키들 (선택사항)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# 🌟 GCP 설정 (RAG 기능용, 필수)
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name

# 🔧 서버 설정
PORT=5000
DEBUG=false
LOG_LEVEL=INFO

# 🎮 현재 모드팩 설정 (자동으로 감지되지만 수동 설정 가능)
CURRENT_MODPACK_NAME=enigmatica_10
CURRENT_MODPACK_VERSION=1.23.0
```

**3.3 파일 저장**
- `Ctrl + X` → `Y` → `Enter`

### **4단계: 백엔드 서비스 시작**

```bash
sudo systemctl start mc-ai-backend
sudo systemctl enable mc-ai-backend
sudo systemctl status mc-ai-backend
```

### **5단계: 모드팩 서버에 하이브리드 지원 추가**

**각 모드팩 서버에 Bukkit 호환성을 추가합니다:**

```bash
# 자동 하이브리드 설치 스크립트 실행
cd ~/minecraft-modpack-ai
chmod +x setup_hybrid_servers.sh
./setup_hybrid_servers.sh
```

이 스크립트는 각 모드팩에 다음을 추가합니다:
- **Mohist/Arclight/CatServer** (Forge+Bukkit 하이브리드)
- **plugins/** 폴더 생성
- **ModpackAI-1.0.jar** 플러그인 설치
- **플러그인 설정 파일** 생성

### **6단계: 테스트**

**6.1 백엔드 API 테스트**
```bash
curl http://localhost:5000/health
```
예상 응답:
```json
{
  "status": "healthy",
  "current_model": "gemini",
  "available_models": {
    "gemini": true,
    "openai": false,
    "claude": false
  }
}
```

**6.2 모드팩 서버 시작**
```bash
cd ~/enigmatica_10
./start.sh
```

**6.3 게임 내 테스트**
```
/modpackai help
/ai 안녕하세요, 테스트입니다
```

---

## 🔧 방법 2: 수동 단계별 설치

### **1단계: 시스템 업데이트 및 필수 패키지 설치**

```bash
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-venv python3-dev \
  openjdk-17-jdk maven git curl wget unzip htop tree \
  build-essential pkg-config libssl-dev libffi-dev
```

### **2단계: AI 백엔드 설치**

```bash
# 백엔드 디렉토리 생성
mkdir -p $HOME/minecraft-ai-backend/{logs,uploads,backups,data}
cd $HOME/minecraft-ai-backend

# Python 가상환경 생성
python3 -m venv $HOME/minecraft-ai-env
source $HOME/minecraft-ai-env/bin/activate

# 프로젝트에서 백엔드 파일 복사
cd ~/minecraft-modpack-ai
cp -r backend/* $HOME/minecraft-ai-backend/
cp env.example $HOME/minecraft-ai-backend/.env

# Python 의존성 설치
cd $HOME/minecraft-ai-backend
pip install --upgrade pip
pip install -r requirements.txt
```

### **3단계: API 키 설정 (필수)**

```bash
# 환경 변수 파일 편집
nano $HOME/minecraft-ai-backend/.env
```

**다음 내용으로 API 키를 설정하세요:**

```env
# 🌟 Google API 키 (Gemini 2.5 Pro용, 필수)
GOOGLE_API_KEY=your-actual-google-api-key

# 📖 백업 모델 API 키들 (선택사항)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# 🌟 GCP 설정 (RAG 기능용, 필수)
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name

# 🔧 서버 설정
PORT=5000
DEBUG=false
LOG_LEVEL=INFO

# 🎮 현재 모드팩 설정 (자동으로 감지되지만 수동 설정 가능)
CURRENT_MODPACK_NAME=enigmatica_10
CURRENT_MODPACK_VERSION=1.23.0
```

**파일 저장**: `Ctrl + X` → `Y` → `Enter`

**API 키 획득:**
- Google AI Studio: https://aistudio.google.com/app/apikey
- OpenAI (선택): https://platform.openai.com/api-keys  
- Anthropic (선택): https://console.anthropic.com/

### **4단계: Minecraft 플러그인 빌드**

```bash
cd ~/minecraft-modpack-ai/minecraft_plugin
mvn clean package

# 빌드 결과 확인
ls -la target/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### **5단계: 모든 모드팩에 하이브리드 서버 및 플러그인 설치**

**전체 모드팩 목록 (GCP VM 기준):**
- **NeoForge**: `enigmatica_10`, `enigmatica_9e`, `atm10`, `carpg`, `test`  
- **Forge 1.20.1**: `integrated_MC`, `beyond_depth`, `cteserver`
- **Forge 1.16.5**: `enigmatica_6`, `mnm`
- **Fabric**: `prominence_2`

#### **5.1 NeoForge 모드팩들 설치 (5개)**

**대상 모드팩**: `enigmatica_10`, `enigmatica_9e`, `atm10`, `carpg`, `test`

```bash
# NeoForge 모드팩들에 공통 설치 스크립트
NEOFORGE_MODPACKS=("enigmatica_10" "enigmatica_9e" "atm10" "carpg" "test")

for modpack in "${NEOFORGE_MODPACKS[@]}"; do
  echo "🔧 $modpack 모드팩 설정 중..."
  cd "$HOME/$modpack"
  
  # Arclight NeoForge 하이브리드 서버 다운로드
  if [ ! -f "arclight-neoforge.jar" ]; then
    echo "📥 Arclight NeoForge 하이브리드 서버 다운로드 중..."
    wget -q -O arclight-neoforge.jar \
      "https://github.com/IzzelAliz/Arclight/releases/download/1.21-1.0.5/arclight-neoforge-1.21-1.0.5.jar"
  fi
  
  # 플러그인 디렉토리 생성 및 복사
  mkdir -p plugins/ModpackAI
  cp ~/minecraft-modpack-ai/minecraft_plugin/target/ModpackAI-1.0.jar plugins/
  
  # 플러그인 설정 파일 생성
  cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - $modpack

ai:
  server_url: "http://localhost:5000"
  modpack_name: "$modpack"
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
    cp start.sh start.sh.backup
  fi
  
  # AI 지원 시작 스크립트 생성
  cat > start_with_ai.sh << 'EOFSCRIPT'
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (Arclight NeoForge)..."

# GCP VM 사양에 맞는 메모리 설정
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
echo "Starting server with Arclight NeoForge hybrid..."

java $JVM_OPTS -jar arclight-neoforge.jar nogui
EOFSCRIPT

  chmod +x start_with_ai.sh
  echo "✅ $modpack 설정 완료"
  echo ""
done
```

#### **5.2 Forge 1.20.1 모드팩들 설치 (3개)**

**대상 모드팩**: `integrated_MC`, `beyond_depth`, `cteserver`

```bash
# Forge 1.20.1 모드팩들에 공통 설치 스크립트
FORGE_1201_MODPACKS=("integrated_MC" "beyond_depth" "cteserver")

for modpack in "${FORGE_1201_MODPACKS[@]}"; do
  echo "🔧 $modpack 모드팩 설정 중..."
  cd "$HOME/$modpack"
  
  # Mohist 1.20.1 하이브리드 서버 다운로드
  if [ ! -f "mohist-1.20.1.jar" ]; then
    echo "📥 Mohist 1.20.1 하이브리드 서버 다운로드 중..."
    wget -q -O mohist-1.20.1.jar \
      "https://mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"
  fi
  
  # 플러그인 디렉토리 생성 및 복사
  mkdir -p plugins/ModpackAI
  cp ~/minecraft-modpack-ai/minecraft_plugin/target/ModpackAI-1.0.jar plugins/
  
  # 플러그인 설정 파일 생성 (NeoForge와 동일)
  cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - $modpack

ai:
  server_url: "http://localhost:5000"
  modpack_name: "$modpack"
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
    cp start.sh start.sh.backup
  fi
  
  # AI 지원 시작 스크립트 생성
  cat > start_with_ai.sh << EOFSCRIPT
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (Mohist 1.20.1)..."

# 메모리 설정
MEMORY="-Xms4G -Xmx8G"

# JVM 최적화 옵션
JVM_ARGS="\$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \\
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions \\
  -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 \\
  -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \\
  -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 \\
  -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15"

echo "Java version: \$(java -version 2>&1 | head -n1)"
echo "Memory: \$MEMORY"
echo "Starting server with Mohist (Forge + Bukkit Hybrid)..."

java \$JVM_ARGS -jar mohist-1.20.1.jar nogui
EOFSCRIPT

  chmod +x start_with_ai.sh
  echo "✅ $modpack 설정 완료"
  echo ""
done
```

#### **5.3 Forge 1.16.5 모드팩들 설치 (2개)**

**대상 모드팩**: `enigmatica_6`, `mnm`

```bash
# Forge 1.16.5 모드팩들에 공통 설치 스크립트
FORGE_1165_MODPACKS=("enigmatica_6" "mnm")

for modpack in "${FORGE_1165_MODPACKS[@]}"; do
  echo "🔧 $modpack 모드팩 설정 중..."
  cd "$HOME/$modpack"
  
  # Mohist 1.16.5 하이브리드 서버 다운로드
  if [ ! -f "mohist-1.16.5.jar" ]; then
    echo "📥 Mohist 1.16.5 하이브리드 서버 다운로드 중..."
    wget -q -O mohist-1.16.5.jar \
      "https://mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"
  fi
  
  # 플러그인 디렉토리 생성 및 복사
  mkdir -p plugins/ModpackAI
  cp ~/minecraft-modpack-ai/minecraft_plugin/target/ModpackAI-1.0.jar plugins/
  
  # 플러그인 설정 파일 생성
  cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - $modpack

ai:
  server_url: "http://localhost:5000"
  modpack_name: "$modpack"
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
    cp start.sh start.sh.backup
  fi
  
  # AI 지원 시작 스크립트 생성
  cat > start_with_ai.sh << EOFSCRIPT
#!/bin/bash
echo "🚀 Starting $PWD with AI Assistant (Mohist 1.16.5)..."

# 메모리 설정
MEMORY="-Xms4G -Xmx8G"

# JVM 최적화 옵션
JVM_ARGS="\$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \\
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions \\
  -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 \\
  -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M \\
  -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5"

echo "Java version: \$(java -version 2>&1 | head -n1)"
echo "Memory: \$MEMORY"
echo "Starting server with Mohist (Forge + Bukkit Hybrid)..."

java \$JVM_ARGS -jar mohist-1.16.5.jar nogui
EOFSCRIPT

  chmod +x start_with_ai.sh
  echo "✅ $modpack 설정 완료"
  echo ""
done
```

#### **5.4 Fabric 모드팩 설치 (1개)**

**대상 모드팩**: `prominence_2`

```bash
echo "🔧 prominence_2 모드팩 설정 중..."
cd "$HOME/prominence_2"

# CardBoard Fabric 하이브리드 서버 다운로드
if [ ! -f "cardboard.jar" ]; then
  echo "📥 CardBoard Fabric 하이브리드 서버 다운로드 중..."
  wget -q -O cardboard.jar \
    "https://github.com/CardboardPowered/cardboard/releases/latest/download/cardboard-1.20.1.jar"
fi

# 플러그인 디렉토리 생성 및 복사
mkdir -p plugins/ModpackAI
cp ~/minecraft-modpack-ai/minecraft_plugin/target/ModpackAI-1.0.jar plugins/

# 플러그인 설정 파일 생성
cat > plugins/ModpackAI/config.yml << EOF
# ModpackAI 플러그인 설정 - prominence_2

ai:
  server_url: "http://localhost:5000"
  modpack_name: "prominence_2"
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
  cp start.sh start.sh.backup
fi

# AI 지원 시작 스크립트 생성
cat > start_with_ai.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting prominence_2 with AI Assistant (CardBoard Fabric)..."

# 메모리 설정
MEMORY="-Xms4G -Xmx6G"

# JVM 최적화 옵션
JVM_ARGS="$MEMORY -XX:+UseG1GC -XX:+ParallelRefProcEnabled \
  -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions"

echo "Java version: $(java -version 2>&1 | head -n1)"
echo "Memory: $MEMORY"
echo "Starting server with CardBoard (Fabric + Bukkit Hybrid)..."

java $JVM_ARGS -jar cardboard.jar nogui
EOF

chmod +x start_with_ai.sh
echo "✅ prominence_2 설정 완료"
```

### **6단계: systemd 서비스 설정**

```bash
# AI 백엔드 서비스 등록
sudo tee /etc/systemd/system/mc-ai-backend.service > /dev/null <<EOF
[Unit]
Description=Minecraft Modpack AI Backend
After=network.target

[Service]
Type=simple
User=namepix080
WorkingDirectory=/home/namepix080/minecraft-ai-backend
Environment=PATH=/home/namepix080/minecraft-ai-env/bin
ExecStart=/home/namepix080/minecraft-ai-env/bin/python /home/namepix080/minecraft-ai-backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable mc-ai-backend
sudo systemctl start mc-ai-backend
```

### **7단계: 관리 스크립트 설치**

```bash
# modpack_switch 스크립트 설치
sudo cp ~/minecraft-modpack-ai/modpack_switch.sh /usr/local/bin/modpack_switch
sudo chmod +x /usr/local/bin/modpack_switch

# 모니터링 스크립트 설치
sudo cp ~/minecraft-modpack-ai/monitor.sh /usr/local/bin/mc-ai-monitor
sudo chmod +x /usr/local/bin/mc-ai-monitor
```

### **8단계: 방화벽 설정**

```bash
# UFW 방화벽 규칙 설정
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 25565/tcp   # Minecraft 기본 포트
sudo ufw allow 5000/tcp    # AI 백엔드
sudo ufw --force enable
```

### **9단계: 설치 검증 및 테스트**

#### **9.1 백엔드 서비스 상태 확인**

```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 백엔드 API 테스트
curl http://localhost:5000/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "current_model": "gemini",
  "available_models": {
    "gemini": true,
    "openai": false,
    "claude": false
  }
}
```

#### **9.2 하나의 모드팩으로 테스트**

```bash
# enigmatica_10으로 테스트 시작
cd ~/enigmatica_10

# 하이브리드 서버로 시작
./start_with_ai.sh

# 서버가 시작되면 게임 내에서 테스트:
# /modpackai help
# /ai 안녕하세요, 테스트입니다
# /give @p book 1 (책을 들고 우클릭)
```

---

## 📁 설치 후 디렉토리 구조

```
/home/namepix080/
├── minecraft-modpack-ai/           # 프로젝트 소스
├── minecraft-ai-backend/           # AI 백엔드 서비스
│   ├── app.py                     # Flask 애플리케이션
│   ├── middleware/                # 보안 및 모니터링
│   ├── .env                       # API 키 설정
│   └── logs/                      # 로그 파일들
├── minecraft-ai-env/              # Python 가상환경
├── enigmatica_10/                 # 모드팩 서버
│   ├── plugins/                   # ← 새로 생성됨
│   │   ├── ModpackAI-1.0.jar     # AI 플러그인
│   │   └── ModpackAI/config.yml   # 플러그인 설정
│   ├── arclight-neoforge-1.21.jar # ← 하이브리드 서버
│   ├── start_with_ai.sh           # ← AI 지원 시작 스크립트
│   └── start.sh                   # 기존 시작 스크립트
├── enigmatica_6/
│   ├── plugins/                   # ← 새로 생성됨
│   ├── mohist-1.16.5.jar         # ← 하이브리드 서버
│   └── start_with_ai.sh           # ← AI 지원 시작 스크립트
└── [다른 모드팩들도 동일한 구조...]
```

---

## 🎮 사용법

### **1. AI 지원 서버 시작**

```bash
# 백엔드 상태 확인
sudo systemctl status mc-ai-backend

# 모드팩 서버 시작 (AI 지원)
cd ~/enigmatica_10
./start_with_ai.sh
```

### **2. 게임 내 사용**

```
# 기본 명령어
/modpackai help                    # 도움말 확인
/modpackai chat                    # AI 채팅 GUI 열기
/ai 철 블록은 어떻게 만들어?         # 바로 질문하기

# AI 어시스턴트 아이템 획득
/give @p book 1                    # 책 아이템 받기
# 책을 들고 우클릭하면 AI 채팅창 열림

# 제작법 조회
/modpackai recipe diamond          # 다이아몬드 제작법
/modpackai recipe "Applied Energistics 2 Controller"
```

### **3. 모드팩 전환**

```bash
# 현재 모드팩 확인
modpack_switch --current

# 모드팩 전환
modpack_switch enigmatica_6 1.11.0
modpack_switch atm10 4.1.0

# 사용 가능한 모드팩 목록
modpack_switch --list
```

---

## 🔧 관리 및 모니터링

### **백엔드 서비스 관리**

```bash
# 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 서비스 재시작
sudo systemctl restart mc-ai-backend

# 로그 확인
sudo journalctl -u mc-ai-backend -f

# 성능 모니터링
mc-ai-monitor

# API 상태 확인
curl http://localhost:5000/health
```

### **각 모드팩 서버 관리**

```bash
# 서버 시작 (AI 지원)
cd ~/enigmatica_10
./start_with_ai.sh

# 서버 시작 (기존 방식)
./start.sh

# 서버 상태 확인 (mcrcon 사용)
cd ~/mcrcon
./mcrcon -H localhost -P 25575 -p [rcon_password] "list"
```

### **로그 및 문제 해결**

```bash
# AI 백엔드 로그
tail -f ~/minecraft-ai-backend/logs/app.log

# 모드팩 서버 로그
tail -f ~/enigmatica_10/logs/latest.log

# 플러그인 로그 확인
grep "ModpackAI" ~/enigmatica_10/logs/latest.log

# 메모리 사용량 확인
free -h
htop
```

---

## 🚨 문제 해결

### **1. 플러그인이 로드되지 않는 경우**

```bash
# 하이브리드 서버 JAR 파일 확인
ls -la ~/enigmatica_10/*.jar

# plugins 폴더 권한 확인
ls -la ~/enigmatica_10/plugins/

# 플러그인 파일 권한 수정
chmod 644 ~/enigmatica_10/plugins/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### **2. AI가 응답하지 않는 경우**

```bash
# 백엔드 서비스 상태
sudo systemctl status mc-ai-backend

# API 연결 테스트
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"테스트","player_uuid":"test","modpack_name":"test","modpack_version":"1.0"}'

# API 키 확인
grep API_KEY ~/minecraft-ai-backend/.env

# 포트 사용 확인
netstat -tlnp | grep 5000
```

### **3. 메모리 부족 문제**

```bash
# 메모리 사용량 확인
free -h

# JVM 힙 크기 조정 (start_with_ai.sh에서)
# -Xmx8G를 -Xmx6G로 줄이기

# swap 파일 생성 (필요시)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **4. 방화벽 문제**

```bash
# GCP 방화벽 규칙 확인
gcloud compute firewall-rules list

# ufw 상태 확인
sudo ufw status

# 포트 열기
sudo ufw allow 25565/tcp  # Minecraft
sudo ufw allow 5000/tcp   # AI Backend
```

---

## 📊 성능 최적화

### **1. JVM 튜닝**

각 모드팩의 `start_with_ai.sh`에서 메모리 설정 조정:

```bash
# 대용량 모드팩 (ATM10, Enigmatica 10)
-Xms8G -Xmx12G

# 중간 크기 모드팩 (Enigmatica 6, Integrated MC)
-Xms6G -Xmx8G

# 가벼운 모드팩 (Beyond Depth, MnM)
-Xms4G -Xmx6G
```

### **2. AI 백엔드 최적화**

`~/.minecraft-ai-backend/.env` 파일에서:

```env
# 동시 요청 제한
MAX_CONCURRENT_REQUESTS=5

# 응답 캐싱 활성화
ENABLE_CACHING=true
CACHE_TTL=3600

# 로그 레벨 조정 (운영 시)
LOG_LEVEL=WARNING
```

### **3. 시스템 리소스 모니터링**

```bash
# 실시간 모니터링
mc-ai-monitor --realtime

# 리소스 사용량 알림 설정
crontab -e
# 추가: */5 * * * * /usr/local/bin/mc-ai-monitor --check-resources
```

---

## 🎯 체크리스트

### **설치 전 준비**
- [ ] GCP VM SSH 접속 확인
- [ ] Google API 키 발급
- [ ] 디스크 용량 확인 (최소 20GB 여유 공간)
- [ ] 기존 모드팩 서버들이 정상 작동하는지 확인

### **설치 과정**
- [ ] 프로젝트 다운로드 완료
- [ ] 자동 설치 스크립트 실행
- [ ] API 키 설정 완료
- [ ] 백엔드 서비스 시작 및 활성화
- [ ] 각 모드팩에 하이브리드 서버 설치
- [ ] 플러그인 설치 및 설정

### **테스트**
- [ ] 백엔드 API 응답 확인 (`curl http://localhost:5000/health`)
- [ ] 하나의 모드팩 서버를 AI 지원으로 시작
- [ ] 게임 내 `/modpackai help` 명령어 작동 확인
- [ ] AI 채팅 기능 테스트
- [ ] 제작법 조회 기능 테스트

### **운영 준비**
- [ ] systemd 서비스 자동 시작 설정
- [ ] 로그 로테이션 설정
- [ ] 정기적인 백업 스크립트 설정
- [ ] 모니터링 및 알림 설정

---

## 📞 지원

### **문제 발생 시 확인 순서**
1. **백엔드 서비스**: `sudo systemctl status mc-ai-backend`
2. **API 키 설정**: `grep API_KEY ~/minecraft-ai-backend/.env`
3. **네트워크 연결**: `curl http://localhost:5000/health`
4. **플러그인 로딩**: 게임 서버 로그에서 "ModpackAI" 검색
5. **메모리 사용량**: `free -h`

### **로그 수집**

```bash
# 종합 진단 정보 수집
cat > collect_logs.sh << 'EOF'
#!/bin/bash
echo "=== 시스템 정보 ===" > ~/ai_debug.log
uname -a >> ~/ai_debug.log
free -h >> ~/ai_debug.log
df -h >> ~/ai_debug.log

echo -e "\n=== 백엔드 상태 ===" >> ~/ai_debug.log
sudo systemctl status mc-ai-backend >> ~/ai_debug.log 2>&1

echo -e "\n=== 백엔드 로그 ===" >> ~/ai_debug.log
sudo journalctl -u mc-ai-backend --since "1 hour ago" >> ~/ai_debug.log

echo -e "\n=== API 테스트 ===" >> ~/ai_debug.log
curl -s http://localhost:5000/health >> ~/ai_debug.log 2>&1

echo -e "\n=== 환경 변수 ===" >> ~/ai_debug.log
grep -E "API_KEY|PORT|DEBUG" ~/minecraft-ai-backend/.env >> ~/ai_debug.log

echo "진단 정보가 ~/ai_debug.log에 저장되었습니다."
EOF

chmod +x collect_logs.sh
./collect_logs.sh
```

---

**🎮 GCP VM에서 AI 지원 모드팩 서버를 성공적으로 구축했습니다!** 🚀

이제 모든 모드팩에서 AI 어시스턴트 기능을 사용하여 더욱 풍부한 게임 경험을 제공할 수 있습니다.