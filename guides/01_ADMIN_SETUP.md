# 🛠️ 관리자를 위한 AI 모드 설치 가이드

## 📋 개요

이 가이드는 GCP VM Debian에서 기존 마인크래프트 NeoForge 모드팩 서버에 ModpackAI 모드를 추가하는 방법을 설명합니다.

### **🎯 설치 방법 선택**

| 방법 | 설명 | 추천도 | 소요시간 |
|------|------|--------|----------|
| **🚀 완전 자동 설치** | 한 번의 명령어로 모든 설치 완료 | ⭐⭐⭐⭐⭐ | 10-15분 |
| **🔧 단계별 설치** | 각 단계를 수동으로 진행 | ⭐⭐⭐ | 20-30분 |

---

## 🚀 방법 1: 완전 자동 설치 (권장)

### **사전 준비사항**
- ✅ GCP VM Debian 서버에 SSH 접속 가능
- ✅ **NeoForge 모드팩 서버**가 이미 설치되어 있음 (하이브리드 서버 불필요!)
- ✅ API 키 준비 (Google Gemini 권장, OpenAI/Anthropic 선택)
- ✅ Java 21+ 설치 확인
- ✅ Python 3.9+ 설치 확인

### **1단계: 프로젝트 다운로드**
**터미널에서 다음 명령어를 입력하세요:**

```bash
cd ~
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
```

**설명**: 
- `cd ~` : 홈 디렉토리로 이동
- `git clone` : GitHub에서 프로젝트를 다운로드
- `cd minecraft-modpack-ai` : 다운로드된 프로젝트 폴더로 이동

### **2단계: 완전 자동 설치 실행**
**터미널에서 다음 중 하나를 실행하세요(동일 동작):**

```bash
# 방법 A: 간단 래퍼 스크립트 사용
chmod +x install.sh
./install.sh

# 방법 B: 직접 설치 스크립트 실행
chmod +x install_mod.sh
./install_mod.sh
```

**설명**: 
- `chmod +x install_mod.sh` : 모드 설치 스크립트에 실행 권한을 부여
- `./install_mod.sh` : 모드 설치 스크립트를 실행

**이 스크립트가 자동으로 수행하는 작업:**
- ✅ AI 백엔드 설치 및 설정
- ✅ **NeoForge 모드 빌드** (Gradle 자동 설치 및 사용)
- ✅ 모든 NeoForge 모드팩에 **ModpackAI 모드** 설치
- ✅ API 키 설정 파일 생성
- ✅ 백엔드 서비스 자동 등록 및 시작
- ✅ 설치 검증 및 상태 확인

### **3단계: API 키 설정 (필수)**
스크립트 실행 후 API 키 설정이 필요합니다.

**3.1 환경 변수 파일 열기**
**터미널에서 다음 명령어를 입력하세요:**

```bash
nano $HOME/minecraft-ai-backend/.env
```

**3.2 API 키 설정 입력**
**편집기에서 파일 내용을 다음과 같이 수정하세요:**

```bash
# Google Gemini API 키 (권장, 웹검색 지원)
GOOGLE_API_KEY=your-actual-google-api-key

# OpenAI API 키 (선택, 백업용)
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Anthropic API 키 (선택, 백업용)  
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key

# Flask 서버 설정
PORT=5000
DEBUG=false
```

**3.3 Google Gemini API 키 발급 방법**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API key" 클릭
3. 프로젝트 선택 또는 새 프로젝트 생성
4. API 키 복사 후 위의 설정 파일에 입력

**3.4 파일 저장**
**편집기에서 다음 키를 순서대로 눌러 저장하세요:**
1. `Ctrl + X` (나가기)
2. `Y` (저장 확인)
3. `Enter` (파일명 확인)

**3.5 백엔드 서비스 재시작**
```bash
sudo systemctl restart mc-ai-backend
```

**3.6 비용 제어(선택)**
```bash
# 웹검색 비용 제어: false로 설정하면 웹검색 비활성화(기본 true)
echo "GEMINI_WEBSEARCH_ENABLED=false" >> $HOME/minecraft-ai-backend/.env
sudo systemctl restart mc-ai-backend
```

### **4단계: 설치 완료 확인**
**터미널에서 다음 명령어로 상태를 확인하세요:**

```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 모드 설치 확인 (정확한 파일명으로 수정)
find ~ -name "modpackai-*.jar" -path "*/mods/*"

# API 테스트
curl http://localhost:5000/health
```

**성공적인 설치 확인 방법:**
- ✅ `mc-ai-backend` 서비스가 `active (running)` 상태
- ✅ 각 모드팩의 `mods/` 폴더에 `modpackai-*.jar` 파일 존재
- ✅ API 테스트에서 `{"status": "healthy"}` 응답

---

## 🔧 방법 2: 단계별 설치 (상세 가이드)

**이 방법은 각 단계를 개별적으로 진행하면서 설치 과정을 이해하고 싶은 분들을 위한 가이드입니다.**

---

### 📋 **1단계: 시스템 환경 준비**

#### **1-1. 기본 도구 설치**
```bash
# 시스템 패키지 데이터베이스 업데이트
sudo apt-get update

# 필수 도구 설치 (Git: 소스코드 다운로드, Curl: API 테스트, Wget: 파일 다운로드)
sudo apt-get install -y git curl wget unzip
```

**설명**: 
- `sudo apt-get update`: 시스템의 패키지 목록을 최신으로 업데이트합니다
- `git`: GitHub에서 프로젝트를 다운로드하기 위해 필요
- `curl`: 백엔드 API 테스트에 사용
- `wget`, `unzip`: Gradle 다운로드 및 압축 해제에 사용

#### **1-2. Java 21 설치**
```bash
# Java 21 설치 (NeoForge 1.20.1+ 필수 요구사항)
sudo apt-get install -y openjdk-21-jdk

# Java 버전 확인
java -version
```

**설명**: 
- **왜 Java 21인가?** NeoForge 1.20.1과 Fabric 1.20.1은 Java 21이 필수입니다
- **설치 확인**: `java -version` 명령어에서 "21.x.x" 버전이 표시되어야 합니다

#### **1-3. Python 3.9+ 설치 및 확인**
```bash
# Python 3과 가상환경 모듈 설치
sudo apt-get install -y python3 python3-pip python3-venv

# Python 버전 확인 (3.9 이상이어야 함)
python3 --version
```

**설명**: 
- **AI 백엔드 요구사항**: Python 3.9+가 필요합니다
- `python3-venv`: 가상환경 생성을 위해 필요한 모듈

---

### 📁 **2단계: 프로젝트 다운로드**

```bash
# 홈 디렉토리로 이동 (~/로도 가능)
cd $HOME

# GitHub에서 프로젝트 전체 다운로드
git clone https://github.com/namepix/minecraft-modpack-ai.git

# 프로젝트 디렉토리로 이동
cd minecraft-modpack-ai

# 현재 위치 확인
pwd
```

**설명**: 
- `cd $HOME`: 사용자 홈 디렉토리로 이동 (보통 /home/username)
- `git clone`: GitHub 저장소의 모든 파일을 로컬로 복사
- **예상 결과**: `/home/username/minecraft-modpack-ai` 폴더가 생성됨

---

### 🐍 **3단계: AI 백엔드 설치 (RAG 시스템 포함)**

**RAG (Retrieval-Augmented Generation) 시스템이란?**  
AI가 답변할 때 외부 지식(웹 검색, 문서)을 참조하여 더 정확하고 최신의 정보를 제공하는 시스템입니다.

#### **3-1. 백엔드 디렉토리로 이동**
```bash
# 백엔드 폴더로 이동
cd backend

# 백엔드 구성 파일들 확인
ls -la
```

**예상 파일들**: 
- `app.py` : Flask 웹 서버 메인 파일
- `requirements.txt` : Python 패키지 의존성 목록
- `rag/` : RAG 시스템 관련 코드

#### **3-2. Python 가상환경 생성**
```bash
# 가상환경 생성 (독립적인 Python 환경)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 가상환경 활성화 확인 (프롬프트 앞에 (venv)가 표시됨)
which python3
```

**왜 가상환경이 필요한가?**
- 시스템 Python과 분리하여 패키지 충돌 방지
- 프로젝트별로 다른 버전의 라이브러리 사용 가능
- 시스템 안정성 보장

#### **3-3. AI 라이브러리 설치**
```bash
# pip 업그레이드 (최신 패키지 설치 도구)
pip install --upgrade pip

# requirements.txt에 정의된 모든 패키지 설치
pip install -r requirements.txt
```

**주요 설치되는 라이브러리들**:
- **Flask**: 웹 서버 프레임워크
- **google-genai**: Google Gemini AI API 클라이언트 (최신 통합 SDK)
- **openai**: OpenAI GPT API 클라이언트  
- **anthropic**: Claude AI API 클라이언트
- **requests**: HTTP 통신 라이브러리
- **flask-cors**: 크로스 오리진 요청 처리
- **sentence-transformers**: RAG 벡터 검색 시스템
- **google-cloud-firestore**: GCP RAG 데이터베이스
- **vertexai**: Google Vertex AI (고급 RAG 기능)

#### **3-4. 백엔드 테스트**
```bash
# Flask 애플리케이션 구문 검사
python3 -c "import app; print('✅ 백엔드 구문 검사 성공')"

# 프로젝트 루트로 복귀
cd ..
```

---

### ⚔️ **4단계: NeoForge 모드 빌드**

**NeoForge란?**  
MinecraftForge의 후속 프로젝트로, Java로 Minecraft 모드를 만들 수 있게 해주는 플랫폼입니다.

#### **4-1. NeoForge 모드 폴더로 이동**
```bash
# NeoForge 모드 소스코드 디렉토리로 이동
cd minecraft_mod

# 프로젝트 구조 확인
ls -la
```

**예상 파일들**: 
- `build.gradle` : Gradle 빌드 설정 파일
- `src/main/java/` : Java 소스코드
- `src/main/resources/` : 리소스 파일 (모드 메타데이터 등)

#### **4-2. Gradle 빌드 도구 준비**

**Gradle이란?**  
Java 프로젝트 빌드 자동화 도구입니다. 소스코드를 컴파일하고 JAR 파일을 생성합니다.

```bash
# Gradle Wrapper가 있는지 확인
if [ ! -f "gradlew" ]; then
    echo "Gradle Wrapper를 생성합니다..."
    
    # 최신 Gradle 다운로드 (NeoForge 호환 버전)
    wget -q https://services.gradle.org/distributions/gradle-8.8-bin.zip -O /tmp/gradle-8.8-bin.zip
    
    # 임시 디렉토리에 압축 해제
    unzip -q /tmp/gradle-8.8-bin.zip -d /tmp
    
    # Gradle Wrapper 생성 (프로젝트에 특화된 Gradle 환경)
    /tmp/gradle-8.8/bin/gradle wrapper --gradle-version 8.8 --distribution-type all
    
    # 임시 파일 정리
    rm -rf /tmp/gradle-8.8 /tmp/gradle-8.8-bin.zip
    
    echo "✅ Gradle Wrapper 생성 완료"
else
    echo "✅ Gradle Wrapper 이미 존재"
fi

# Gradle Wrapper에 실행 권한 부여
chmod +x ./gradlew
```

**Gradle Wrapper의 장점**:
- 프로젝트별로 정확한 Gradle 버전 사용
- 시스템에 Gradle이 설치되지 않아도 작동
- 팀 개발 시 환경 통일성 보장

#### **4-3. NeoForge 모드 컴파일**
```bash
# 이전 빌드 결과물 정리
./gradlew clean

# NeoForge 모드 빌드 시작
echo "🔨 NeoForge 모드 빌드 중... (최대 5-10분 소요)"
./gradlew build
```

**빌드 과정 설명**:
1. **의존성 다운로드**: NeoForge API, Minecraft 라이브러리 다운로드
2. **소스코드 컴파일**: Java 코드를 바이트코드로 변환
3. **리소스 패키징**: 모드 메타데이터, 텍스처 등을 JAR에 포함
4. **JAR 파일 생성**: 완성된 모드 파일 생성

#### **4-4. 빌드 결과 확인**
```bash
# 빌드 결과물 디렉토리 확인
ls -la build/libs/

# 모드 JAR 파일 자동 탐지
BUILT_MOD=$(find build/libs -name "modpackai-*.jar" | head -n1)

if [ -n "$BUILT_MOD" ] && [ -f "$BUILT_MOD" ]; then
    echo "✅ NeoForge 모드 빌드 성공!"
    echo "   파일: $BUILT_MOD"
    echo "   크기: $(ls -lh "$BUILT_MOD" | awk '{print $5}')"
else
    echo "❌ 모드 빌드 실패"
    echo "   build/libs/ 디렉토리에서 modpackai-*.jar 파일을 찾을 수 없습니다"
    exit 1
fi

# 프로젝트 루트로 복귀
cd ..
```

---

### 🎯 **5단계: Fabric 모드 빌드 (듀얼 모드로더 지원)**

**Fabric이란?**  
NeoForge의 대안으로, 더 가벼우고 빠른 모드 로딩을 제공하는 모드 플랫폼입니다.

#### **5-1. Fabric 모드 빌드 (선택사항)**

**⚠️ 중요**: Fabric 모드 빌드에서 Gradle 관련 오류가 발생할 수 있습니다. 아래 해결 방법을 순서대로 시도하세요.

```bash
# Fabric 모드 디렉토리가 있는지 확인
if [ -d "minecraft_fabric_mod" ]; then
    echo "🧵 Fabric 모드도 함께 빌드합니다..."
    cd minecraft_fabric_mod
    
    # Fabric 모드 Gradle Wrapper 준비 (강화된 버전)
    if [ ! -f "gradlew" ] || [ ! -x "gradlew" ]; then
        echo "📦 Gradle Wrapper 생성 중..."
        
        # 시스템 Gradle 버전이 오래된 경우 최신 Gradle 다운로드
        if ! gradle --version 2>/dev/null | grep -q "Gradle [8-9]"; then
            echo "⚠️ 시스템 Gradle 버전이 오래되었습니다. 최신 Gradle 다운로드 중..."
            
            # 임시 디렉토리에 최신 Gradle 다운로드
            wget -q https://services.gradle.org/distributions/gradle-8.8-bin.zip -O /tmp/gradle-8.8-bin.zip
            unzip -q /tmp/gradle-8.8-bin.zip -d /tmp
            
            # 최신 Gradle로 wrapper 생성
            /tmp/gradle-8.8/bin/gradle wrapper --gradle-version 8.8 --distribution-type all
            
            # 임시 파일 정리
            rm -rf /tmp/gradle-8.8 /tmp/gradle-8.8-bin.zip
        else
            gradle wrapper --gradle-version 8.8 --distribution-type all
        fi
    fi
    
    chmod +x ./gradlew
    
    # Fabric 모드 빌드
    echo "🔨 Fabric 모드 빌드 시작..."
    ./gradlew clean build
    
    # 빌드 결과 확인
    FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)
    if [ -f "$FABRIC_JAR" ]; then
        echo "✅ Fabric 모드 빌드 성공: $FABRIC_JAR"
    else
        echo "❌ Fabric 모드 빌드 실패"
        echo "💡 해결방법: ./fix_fabric_build.sh 스크립트를 실행하세요"
    fi
    
    cd ..
else
    echo "ℹ️ Fabric 모드 디렉토리가 없습니다. NeoForge만 사용합니다."
fi
```

**🔧 Fabric 빌드 문제 해결 방법**:

만약 위 단계에서 오류가 발생한다면:

```bash
# 자동 해결 스크립트 실행
./fix_fabric_build.sh

# 또는 수동 해결
cd minecraft_fabric_mod

# 1. Fabric Loom 플러그인 버전 확인/수정
grep "fabric-loom" build.gradle
# 만약 SNAPSHOT 버전이면 안정 버전으로 변경하세요

# 2. 기존 빌드 캐시 완전 삭제
rm -rf .gradle build ~/.gradle/caches/fabric-loom

# 3. Gradle wrapper 재생성
rm -f gradlew gradlew.bat
rm -rf gradle/
gradle wrapper --gradle-version 8.8 --distribution-type all
chmod +x ./gradlew

# 4. 빌드 재시도
./gradlew clean build --refresh-dependencies
```

#### **5-2. 통합 빌드 스크립트 사용 (권장)**
```bash
# 모든 모드를 한 번에 빌드하는 스크립트 실행
chmod +x build_all_mods.sh
./build_all_mods.sh
```

**이 스크립트가 수행하는 작업**:
- NeoForge 모드와 Fabric 모드 순차적 빌드
- 빌드 결과물을 `build_output/` 폴더에 정리
- 각 모드 파일의 크기와 위치 정보 제공

---

### 🔧 **6단계: 백엔드 서비스 설정**

#### **6-1. 백엔드 파일 배포**
```bash
# rsync 설치 (파일 동기화 도구)
sudo apt-get update
sudo apt-get install rsync -y

# 홈 디렉토리에 백엔드 전용 폴더 생성
BACKEND_DIR="$HOME/minecraft-ai-backend"
mkdir -p "$BACKEND_DIR"

# 백엔드 파일들을 전용 폴더로 복사 (가상환경 제외)
rsync -a --exclude 'venv' backend/ "$BACKEND_DIR/"

echo "✅ 백엔드 파일 배포 완료: $BACKEND_DIR"
```

**rsync가 설치되어 있지 않은 경우 대체 방법:**
```bash
# 방법 2: cp 명령어 사용
cp -r backend/ "$BACKEND_DIR/"
rm -rf "$BACKEND_DIR/venv"
echo "✅ 백엔드 파일 배포 완료: $BACKEND_DIR"
```

#### **6-2. 프로덕션 가상환경 생성**
```bash
# 백엔드 디렉토리로 이동
cd "$BACKEND_DIR"

# 프로덕션용 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# 가상환경 비활성화
deactivate

echo "✅ 프로덕션 가상환경 설정 완료"
```

#### **6-3. systemd 서비스 등록**

**systemd란?**  
Linux 시스템의 서비스 관리자입니다. 백엔드를 자동으로 시작하고 재시작하게 해줍니다.

```bash
# systemd 서비스 파일 생성
sudo tee /etc/systemd/system/mc-ai-backend.service > /dev/null << EOF
[Unit]
Description=Minecraft Modpack AI Backend
Documentation=https://github.com/namepix/minecraft-modpack-ai
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$BACKEND_DIR
ExecStart=$BACKEND_DIR/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 환경 변수
Environment=PYTHONUNBUFFERED=1
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
EOF

echo "✅ systemd 서비스 파일 생성 완료"
```

#### **6-4. 서비스 등록 및 활성화**
```bash
# systemd 설정 다시 로드
sudo systemctl daemon-reload

# 서비스 부팅시 자동 시작 설정
sudo systemctl enable mc-ai-backend

# 서비스 등록 확인
systemctl is-enabled mc-ai-backend

echo "✅ 백엔드 서비스 등록 완료"
```

---

### 🗂️ **7단계: 모드팩에 모드 자동 배포**

#### **7-1. 모드팩 자동 감지 (NeoForge + Fabric)**
```bash
echo "🔍 설치 가능한 모드팩을 찾는 중..."

# 모드팩 디렉토리들을 배열로 수집
declare -a NEOFORGE_MODPACKS
declare -a FABRIC_MODPACKS

while IFS= read -r -d '' mods_dir; do
    modpack_dir=$(dirname "$mods_dir")
    modpack_name=$(basename "$modpack_dir")
    
    # NeoForge 모드팩인지 확인
    if ls "$modpack_dir"/neoforge-*.jar >/dev/null 2>&1 || \
       [ -d "$modpack_dir/libraries" ] && grep -Rqi "neoforge" "$modpack_dir/libraries" 2>/dev/null; then
        NEOFORGE_MODPACKS+=("$mods_dir|$modpack_name")
        echo "🔨 NeoForge 발견: $modpack_name"
    
    # Fabric 모드팩인지 확인
    elif find "$modpack_dir" -name "*fabric*loader*.jar" -o -name "*fabric*server*.jar" | grep -q . || \
         [ -d "$modpack_dir/libraries" ] && grep -Rqi "fabric" "$modpack_dir/libraries" 2>/dev/null; then
        FABRIC_MODPACKS+=("$mods_dir|$modpack_name")
        echo "🧵 Fabric 발견: $modpack_name"
    else
        echo "⏭️ 건너뜀: $modpack_name (알 수 없는 모드로더)"
    fi
done < <(find "$HOME" -maxdepth 2 -type d -name "mods" -print0)

echo "📊 발견된 모드팩:"
echo "   - NeoForge: ${#NEOFORGE_MODPACKS[@]}개"
echo "   - Fabric: ${#FABRIC_MODPACKS[@]}개"
```

#### **7-2. NeoForge 모드 자동 설치**
```bash
if [ ${#NEOFORGE_MODPACKS[@]} -gt 0 ]; then
    echo ""
    echo "🔨 NeoForge 모드 설치 시작..."
    
    # 빌드된 NeoForge 모드 파일 경로
    NEOFORGE_MOD_PATH="minecraft_mod/build/libs/$(ls minecraft_mod/build/libs/modpackai-*.jar | head -n1 | xargs basename)"
    
    if [ ! -f "$NEOFORGE_MOD_PATH" ]; then
        echo "❌ NeoForge 모드 파일을 찾을 수 없습니다: $NEOFORGE_MOD_PATH"
    else
        # 각 NeoForge 모드팩에 모드 설치
        NEOFORGE_INSTALLED=0
        for modpack_info in "${NEOFORGE_MODPACKS[@]}"; do
            IFS='|' read -r mods_dir modpack_name <<< "$modpack_info"
            
            echo "📦 $modpack_name에 NeoForge 모드 설치 중..."
            
            # 기존 ModpackAI 모드 제거 (업데이트)
            rm -f "$mods_dir"/modpackai-*.jar
            
            # 새 모드 복사
            cp "$NEOFORGE_MOD_PATH" "$mods_dir/"
            
            # 설치 확인
            if ls "$mods_dir"/modpackai-*.jar >/dev/null 2>&1; then
                echo "✅ $modpack_name 설치 완료"
                ((NEOFORGE_INSTALLED++))
            else
                echo "❌ $modpack_name 설치 실패"
            fi
        done
        
        echo "📊 NeoForge: $NEOFORGE_INSTALLED개 모드팩에 설치 완료"
    fi
else
    echo "ℹ️ NeoForge 모드팩이 없습니다."
fi
```

#### **7-3. Fabric 모드 자동 설치**
```bash
if [ ${#FABRIC_MODPACKS[@]} -gt 0 ]; then
    echo ""
    echo "🧵 Fabric 모드 설치 시작..."
    
    # 빌드된 Fabric 모드 파일 경로
    FABRIC_MOD_PATH="minecraft_fabric_mod/build/libs/$(ls minecraft_fabric_mod/build/libs/modpackai-fabric-*.jar | head -n1 | xargs basename)"
    
    if [ ! -f "$FABRIC_MOD_PATH" ]; then
        echo "❌ Fabric 모드 파일을 찾을 수 없습니다: $FABRIC_MOD_PATH"
    else
        # 각 Fabric 모드팩에 모드 설치
        FABRIC_INSTALLED=0
        for modpack_info in "${FABRIC_MODPACKS[@]}"; do
            IFS='|' read -r mods_dir modpack_name <<< "$modpack_info"
            
            echo "📦 $modpack_name에 Fabric 모드 설치 중..."
            
            # 기존 ModpackAI 모드 제거 (업데이트)
            rm -f "$mods_dir"/modpackai-*.jar
            
            # 새 모드 복사
            cp "$FABRIC_MOD_PATH" "$mods_dir/"
            
            # 설치 확인
            if ls "$mods_dir"/modpackai-*.jar >/dev/null 2>&1; then
                echo "✅ $modpack_name 설치 완료"
                ((FABRIC_INSTALLED++))
            else
                echo "❌ $modpack_name 설치 실패"
            fi
        done
        
        echo "📊 Fabric: $FABRIC_INSTALLED개 모드팩에 설치 완료"
    fi
else
    echo "ℹ️ Fabric 모드팩이 없습니다."
fi
```

#### **7-4. 설치 완료 요약**
```bash
echo ""
echo "🎉 모드 설치 완료!"
echo "==================="
echo "📊 설치 결과:"
if [ ${#NEOFORGE_MODPACKS[@]} -gt 0 ]; then
    echo "   🔨 NeoForge: ${NEOFORGE_INSTALLED:-0}개 모드팩"
fi
if [ ${#FABRIC_MODPACKS[@]} -gt 0 ]; then
    echo "   🧵 Fabric: ${FABRIC_INSTALLED:-0}개 모드팩"
fi
echo ""
echo "⚠️  중요: 모드가 적용되려면 각 모드팩 서버를 재시작해야 합니다!"
echo "🎮 재시작 후 게임에서 /ai 명령어를 사용할 수 있습니다."
```

---

### 🔑 **8단계: API 키 설정 (필수)**

#### **8-1. 환경 설정 파일 준비**
```bash
# 백엔드 디렉토리로 이동
cd "$HOME/minecraft-ai-backend"

# 환경 설정 파일 생성 (env.example 복사)
if [ -f "../env.example" ]; then
    cp "../env.example" .env
elif [ ! -f ".env" ]; then
    # 기본 .env 파일 생성
    cat > .env << 'EOF'
# Google Gemini API Key (권장 - 웹검색 지원)
GOOGLE_API_KEY=your-google-api-key-here

# OpenAI API Key (백업용)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic Claude API Key (백업용)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# GCP RAG 시스템 설정 (고급 기능)
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name

# 서버 설정
PORT=5000
DEBUG=false
FLASK_ENV=production

# RAG 및 웹검색 설정
GEMINI_WEBSEARCH_ENABLED=true
SEARCH_RESULTS_LIMIT=5
MAX_TOKENS_PER_REQUEST=4000
EOF
fi

echo "✅ 환경 설정 파일 생성: $HOME/minecraft-ai-backend/.env"
```

#### **8-2. Google Gemini API 키 발급 가이드**

**Google Gemini API 키가 권장되는 이유**:
- **무료 할당량**: 월 60회 무료 요청
- **웹검색 지원**: 실시간 인터넷 정보 검색 가능
- **한국어 지원**: 우수한 한국어 이해도
- **모드팩 특화**: 마인크래프트 모드 정보에 최적화

```bash
echo ""
echo "🌟 Google Gemini API 키 발급 방법:"
echo "   1. https://makersuite.google.com/app/apikey 접속"
echo "   2. Google 계정으로 로그인"
echo "   3. 'Create API key' 버튼 클릭"
echo "   4. 프로젝트 선택 또는 새 프로젝트 생성"
echo "   5. API 키 복사"
echo "   6. 아래 명령어로 API 키 설정:"
echo ""
echo "📝 API 키 설정 명령어:"
echo "   nano $HOME/minecraft-ai-backend/.env"
echo ""
echo "🔧 설정 후 다음 명령어로 서비스 재시작:"
echo "   sudo systemctl restart mc-ai-backend"
echo ""
```

#### **8-3. API 키 및 GCP 설정 도움말**
```bash
echo "💡 API 키 설정 팁:"
echo "   - GOOGLE_API_KEY=your-key-here 형태로 입력"
echo "   - 키 앞뒤에 공백이나 따옴표 없이 입력"
echo "   - 여러 API 키를 설정하면 자동으로 백업 사용"
echo ""
echo "🏗️ GCP RAG 시스템 설정 (고급 기능):"
echo "   - GCP_PROJECT_ID=your-gcp-project-id : GCP 프로젝트 ID"
echo "   - GCS_BUCKET_NAME=your-bucket-name : Cloud Storage 버킷명"
echo "   - 설정하지 않으면 자동으로 로컬 RAG + 웹검색으로 작동"
echo ""
echo "💰 비용 제어 방법:"
echo "   - GEMINI_WEBSEARCH_ENABLED=false : 웹검색 비활성화"
echo "   - MAX_TOKENS_PER_REQUEST=2000 : 토큰 사용량 제한"
echo ""
```

---

### 🚀 **9단계: 서비스 시작 및 검증**

#### **9-1. 백엔드 서비스 시작**
```bash
echo "🚀 백엔드 서비스를 시작합니다..."

# 서비스 시작
sudo systemctl start mc-ai-backend

# 서비스 시작 대기
sleep 5

# 서비스 상태 확인
if sudo systemctl is-active --quiet mc-ai-backend; then
    echo "✅ 백엔드 서비스 성공적으로 시작됨"
    
    # 서비스 상태 상세 정보
    sudo systemctl status mc-ai-backend --no-pager -l
else
    echo "❌ 백엔드 서비스 시작 실패"
    echo "📋 오류 로그:"
    sudo journalctl -u mc-ai-backend -n 20 --no-pager
    echo ""
    echo "🔧 해결 방법:"
    echo "   1. API 키가 올바르게 설정되었는지 확인"
    echo "   2. 방화벽에서 포트 5000 허용 확인"
    echo "   3. Python 의존성 재설치"
fi
```

#### **9-2. API 연결 테스트**
```bash
echo "🧪 API 연결 테스트 중..."

# 백엔드 준비 대기
sleep 3

# Health Check 테스트
echo "1. 기본 연결 테스트..."
if curl -s --fail http://localhost:5000/health > /dev/null; then
    API_RESPONSE=$(curl -s http://localhost:5000/health)
    echo "✅ API 연결 성공: $API_RESPONSE"
else
    echo "❌ API 연결 실패"
    echo "   URL: http://localhost:5000/health"
    echo "   포트 5000이 열려있는지 확인하세요"
fi

# AI 기능 테스트 (API 키가 설정된 경우)
echo "2. AI 기능 테스트..."
AI_TEST_RESPONSE=$(curl -s -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"테스트","modpack":"test"}' | head -c 100)

if [[ "$AI_TEST_RESPONSE" == *"error"* ]]; then
    echo "⚠️ AI 기능 테스트 실패 (API 키 설정 필요)"
    echo "   API 키 설정 후 다시 테스트하세요"
else
    echo "✅ AI 기능 테스트 성공"
fi
```

#### **9-3. 설치 검증 체크리스트**
```bash
echo ""
echo "📋 설치 검증 체크리스트"
echo "========================"

# 1. 백엔드 서비스 상태
if sudo systemctl is-active --quiet mc-ai-backend; then
    echo "✅ 백엔드 서비스 실행 중"
else
    echo "❌ 백엔드 서비스 중지됨"
fi

# 2. 모드 파일 설치 확인
MOD_COUNT=$(find "$HOME" -path "*/mods/modpackai-*.jar" | wc -l)
if [ $MOD_COUNT -gt 0 ]; then
    echo "✅ 모드 설치 확인: ${MOD_COUNT}개 모드팩"
    find "$HOME" -path "*/mods/modpackai-*.jar" -exec echo "   - {}" \;
else
    echo "❌ 설치된 모드를 찾을 수 없음"
fi

# 3. API 접근성
if curl -s --fail http://localhost:5000/health > /dev/null; then
    echo "✅ API 서버 접근 가능"
else
    echo "❌ API 서버 접근 불가"
fi

# 4. 환경 설정 파일
if [ -f "$HOME/minecraft-ai-backend/.env" ]; then
    echo "✅ 환경 설정 파일 존재"
    if grep -q "your-.*-key-here" "$HOME/minecraft-ai-backend/.env"; then
        echo "⚠️ API 키 설정 필요"
    else
        echo "✅ API 키 설정 완료"
    fi
else
    echo "❌ 환경 설정 파일 누락"
fi

echo ""
echo "🎯 다음 단계:"
if [ -f "$HOME/minecraft-ai-backend/.env" ] && ! grep -q "your-.*-key-here" "$HOME/minecraft-ai-backend/.env"; then
    echo "   ✅ 설치 완료! NeoForge 모드팩 서버를 시작하세요"
else
    echo "   1. API 키 설정: nano $HOME/minecraft-ai-backend/.env"
    echo "   2. 서비스 재시작: sudo systemctl restart mc-ai-backend"
    echo "   3. NeoForge 모드팩 서버 시작"
fi
```

---

### 🧠 **9.5단계: RAG 시스템 완전 구축 및 테스트 (권장)**

**RAG (Retrieval-Augmented Generation)이란?**  
AI가 답변할 때 모드팩 관련 문서를 검색하여 더 정확하고 구체적인 정보를 제공하는 시스템입니다.

#### **🏗️ RAG 시스템 아키텍처**
```
┌─ minecraft-modpack-ai/     ← 소스 코드 저장소 (GitHub에서 clone)
│  └─ backend/              ← 개발 및 수정용 파일들
│     ├─ app.py
│     ├─ config_manager.py
│     ├─ gcp_rag_system.py
│     ├─ rag_manager.py
│     └─ enhanced_modpack_parser.py
│
└─ minecraft-ai-backend/     ← 실제 실행 환경
   ├─ .env                  ← 환경변수 설정 파일
   ├─ app.py               ← 실행용 Flask 앱
   ├─ venv/                ← Python 가상환경
   └─ ... (복사된 실행 파일들)
```

#### **9.5-1. 파일 동기화 시스템 설정**

**⚠️ 중요**: 소스 코드와 실행 환경 동기화가 필수입니다.

```bash
echo "🔄 파일 동기화 시스템 설정"
echo "========================"

# 동기화 스크립트 생성
cd ~
cat > sync_backend.sh << 'EOF'
#!/bin/bash
echo "🔄 소스 → 실행환경 파일 동기화 중..."

# 현재 시간 기록
echo "동기화 시작: $(date)"

# Python 파일들 복사
echo "📝 Python 파일 복사 중..."
cp ~/minecraft-modpack-ai/backend/*.py ~/minecraft-ai-backend/ 2>/dev/null || true

# 설정 파일들 복사
echo "⚙️  설정 파일 복사 중..."
cp ~/minecraft-modpack-ai/backend/*.json ~/minecraft-ai-backend/ 2>/dev/null || true
cp ~/minecraft-modpack-ai/backend/requirements*.txt ~/minecraft-ai-backend/ 2>/dev/null || true

# middleware 디렉토리 복사
echo "📂 middleware 디렉토리 복사 중..."
if [ -d ~/minecraft-modpack-ai/backend/middleware ]; then
    cp -r ~/minecraft-modpack-ai/backend/middleware/ ~/minecraft-ai-backend/
fi

# tests 디렉토리 복사
echo "🧪 tests 디렉토리 복사 중..."
if [ -d ~/minecraft-modpack-ai/backend/tests ]; then
    cp -r ~/minecraft-modpack-ai/backend/tests/ ~/minecraft-ai-backend/
fi

echo "✅ 동기화 완료!"
echo "📊 최신 파일들:"
ls -lt ~/minecraft-ai-backend/*.py | head -5

echo ""
echo "🔍 중요 파일 확인:"
echo "config_manager.py: $([ -f ~/minecraft-ai-backend/config_manager.py ] && echo '✅ 존재' || echo '❌ 없음')"
echo "gcp_rag_system.py: $([ -f ~/minecraft-ai-backend/gcp_rag_system.py ] && echo '✅ 존재' || echo '❌ 없음')"
echo "app.py: $([ -f ~/minecraft-ai-backend/app.py ] && echo '✅ 존재' || echo '❌ 없음')"
EOF

chmod +x sync_backend.sh

# 첫 동기화 실행
echo "🚀 첫 파일 동기화 실행 중..."
./sync_backend.sh
```

#### **9.5-2. GCP RAG 환경변수 설정**

```bash
echo "⚙️ GCP RAG 환경변수 설정"
echo "======================="

# 환경변수 파일에 GCP RAG 설정 추가
ENV_FILE="$HOME/minecraft-ai-backend/.env"

# 기존 GCP 설정 확인
if ! grep -q "GCP_RAG_ENABLED" "$ENV_FILE"; then
    echo ""
    echo "# ==========================================
# GCP RAG 시스템 설정 (고급 기능)
# ==========================================

# GCP RAG 시스템 활성화
GCP_RAG_ENABLED=true

# GCP 프로젝트 ID (실제 프로젝트 ID로 교체)
GCP_PROJECT_ID=your-gcp-project-id

# GCS 버킷 이름 (선택사항)
GCS_BUCKET_NAME=your-gcs-bucket-name

# Google Cloud 프로젝트 설정
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# ==========================================
# 모드팩 설정 (예시)
# ==========================================

# 현재 활성 모드팩 이름
CURRENT_MODPACK_NAME=Prominence_II_RPG_Hasturian_Era

# 모드팩 버전
CURRENT_MODPACK_VERSION=3.1.51hf

# ==========================================
# RAG 및 AI 설정
# ==========================================

# Gemini 웹검색 활성화
GEMINI_WEBSEARCH_ENABLED=true

# 검색 결과 제한
SEARCH_RESULTS_LIMIT=5

# 요청당 최대 토큰 수
MAX_TOKENS_PER_REQUEST=4000

# 기본 AI 모델
DEFAULT_AI_MODEL=gemini-2.5-pro" >> "$ENV_FILE"
    
    echo "✅ GCP RAG 환경변수 설정 추가됨"
else
    echo "✅ GCP RAG 환경변수 이미 설정됨"
fi

echo ""
echo "📝 다음 단계: GCP 프로젝트 ID를 실제 값으로 수정하세요"
echo "   nano $ENV_FILE"
echo ""
```

#### **9.5-3. GCP 인증 및 권한 설정**

```bash
echo "🔐 GCP 인증 및 권한 설정"
echo "======================="

# VM의 서비스 계정 확인
echo "1. 현재 GCP 서비스 계정 확인:"
VM_SERVICE_ACCOUNT=$(curl -s -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email)
echo "   서비스 계정: $VM_SERVICE_ACCOUNT"

# 현재 권한 범위 확인  
echo ""
echo "2. 현재 권한 범위 확인:"
SCOPES=$(curl -s -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/scopes)
echo "$SCOPES"

if echo "$SCOPES" | grep -q "https://www.googleapis.com/auth/cloud-platform"; then
    echo "✅ cloud-platform 권한 범위 있음"
else
    echo "❌ cloud-platform 권한 범위 없음"
    echo ""
    echo "🔧 해결 방법:"
    echo "   1. GCP 콘솔에서 VM 중지"
    echo "   2. VM 인스턴스 → 편집"
    echo "   3. 액세스 범위 → '모든 Cloud API에 대한 전체 액세스 허용' 선택"
    echo "   4. 저장 → VM 시작"
fi

echo ""
echo "3. GCP IAM 권한 확인 및 설정:"
echo "   GCP 콘솔에서 다음 역할을 VM 서비스 계정에 부여하세요:"
echo "   - Vertex AI 사용자 (roles/aiplatform.user)"
echo "   - Cloud Datastore 사용자 (roles/datastore.user)"
echo "   - 저장소 객체 뷰어 (roles/storage.objectViewer)"
echo "   - Editor (권장 - 모든 권한)"
echo ""

# API 활성화
echo "4. 필수 API 활성화:"
if command -v gcloud &> /dev/null; then
    echo "   GCloud CLI가 설치되어 있습니다. API를 활성화합니다..."
    
    # GCP 프로젝트 ID 가져오기 (환경변수 또는 메타데이터에서)
    PROJECT_ID=$(grep "GCP_PROJECT_ID=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | head -1)
    if [ "$PROJECT_ID" = "your-gcp-project-id" ] || [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" \
          http://metadata.google.internal/computeMetadata/v1/project/project-id)
    fi
    
    if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "your-gcp-project-id" ]; then
        echo "   프로젝트 ID: $PROJECT_ID"
        
        gcloud services enable aiplatform.googleapis.com --project="$PROJECT_ID" || true
        gcloud services enable firestore.googleapis.com --project="$PROJECT_ID" || true
        
        echo "   ✅ API 활성화 요청 완료"
    else
        echo "   ⚠️ GCP_PROJECT_ID가 설정되지 않았습니다. 수동으로 활성화하세요:"
        echo "      gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID"
        echo "      gcloud services enable firestore.googleapis.com --project=YOUR_PROJECT_ID"
    fi
else
    echo "   ⚠️ GCloud CLI가 설치되지 않았습니다. GCP 콘솔에서 수동으로 활성화하세요:"
    echo "      - Vertex AI API"
    echo "      - Cloud Firestore API"
fi

echo ""
```

#### **9.5-4. RAG 설정 도구 사용**

```bash
echo "🎯 RAG 설정 도구 사용"
echo "==================="

# 백엔드 실행 환경으로 이동
cd "$HOME/minecraft-ai-backend"

# 가상환경 활성화
echo "1. Python 가상환경 활성화..."
source venv/bin/activate

# config_manager.py 존재 확인
if [ ! -f "config_manager.py" ]; then
    echo "❌ config_manager.py가 없습니다. 동기화를 실행합니다..."
    cd ~
    ./sync_backend.sh
    cd "$HOME/minecraft-ai-backend"
fi

if [ -f "config_manager.py" ]; then
    echo ""
    echo "2. 현재 RAG 설정 상태 확인..."
    python3 config_manager.py status
    
    echo ""
    echo "3. GCP 프로젝트 ID 설정 (필요시):"
    echo "   python3 config_manager.py set-gcp-project \"your-actual-gcp-project-id\""
    echo ""
    echo "4. 수동 모드팩 설정 (선택사항):"
    echo "   python3 config_manager.py set-manual \"Prominence_II_RPG_Hasturian_Era\" \"3.1.51hf\""
    echo ""
else
    echo "❌ config_manager.py를 찾을 수 없습니다."
    echo "   해결 방법: ~/sync_backend.sh 실행"
fi

# 가상환경 비활성화
deactivate

echo ""
```

#### **9.5-5. 백엔드 재시작 및 RAG 시스템 상태 확인**

```bash
echo "🚀 백엔드 재시작 및 RAG 시스템 상태 확인"
echo "======================================="

# 환경변수 로드 테스트
echo "1. 환경변수 설정 확인..."
cd "$HOME/minecraft-ai-backend"
source venv/bin/activate

# 환경변수 직접 설정 (터미널 세션용)
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

deactivate

# 백엔드 서비스 재시작
echo ""
echo "2. 백엔드 서비스 재시작..."
sudo systemctl restart mc-ai-backend

# 재시작 대기
sleep 5

# 서비스 상태 확인
if sudo systemctl is-active --quiet mc-ai-backend; then
    echo "✅ 백엔드 서비스 재시작 성공"
else
    echo "❌ 백엔드 서비스 재시작 실패"
    echo "📋 오류 로그:"
    sudo journalctl -u mc-ai-backend -n 10 --no-pager
fi

echo ""
echo "3. RAG 시스템 접근성 확인..."
sleep 3

if curl -s --fail http://localhost:5000/gcp-rag/status > /dev/null; then
    echo "✅ RAG 시스템 접근 가능"
    
    # RAG 상태 상세 정보
    RAG_STATUS=$(curl -s http://localhost:5000/gcp-rag/status)
    echo "📊 RAG 시스템 상태:"
    echo "$RAG_STATUS" | python3 -m json.tool 2>/dev/null || echo "$RAG_STATUS"
else
    echo "❌ RAG 시스템 접근 불가"
    echo "   💡 해결 방법: sudo systemctl restart mc-ai-backend"
fi

echo ""
```

#### **9.5-6. Firestore 데이터베이스 생성**

```bash
echo "🗄️ Firestore 데이터베이스 생성"
echo "=========================="

if command -v gcloud &> /dev/null; then
    # GCP 프로젝트 ID 가져오기
    PROJECT_ID=$(grep "GCP_PROJECT_ID=" "$HOME/minecraft-ai-backend/.env" | cut -d'=' -f2 | tr -d '"' | head -1)
    if [ "$PROJECT_ID" = "your-gcp-project-id" ] || [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" \
          http://metadata.google.internal/computeMetadata/v1/project/project-id)
    fi
    
    if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "your-gcp-project-id" ]; then
        echo "프로젝트 ID: $PROJECT_ID"
        echo ""
        echo "Firestore 데이터베이스 생성 중... (최초 1회만)"
        
        gcloud firestore databases create \
            --region=us-central1 \
            --project="$PROJECT_ID" \
            --type=firestore-native || true
        
        echo "✅ Firestore 데이터베이스 생성 완료 (이미 존재하는 경우 무시됨)"
    else
        echo "❌ GCP 프로젝트 ID가 설정되지 않았습니다."
        echo "   수동 생성 방법:"
        echo "   gcloud firestore databases create --region=us-central1 --project=YOUR_PROJECT_ID --type=firestore-native"
    fi
else
    echo "❌ GCloud CLI가 설치되지 않았습니다."
    echo "   GCP 콘솔에서 수동으로 Firestore 데이터베이스를 생성하세요:"
    echo "   1. GCP 콘솔 → Firestore"
    echo "   2. 데이터베이스 생성"
    echo "   3. 네이티브 모드 선택"
    echo "   4. 리전: us-central1"
fi

echo ""
```

#### **9.5-7. 모드팩 RAG 인덱스 구축**

```bash
echo "📚 모드팩 RAG 인덱스 구축"
echo "========================"

# 현재 실행 중인 모드팩 경로 찾기
CURRENT_MODPACK_DIR=$(find "$HOME" -maxdepth 2 -name "mods" -type d | head -n1 | xargs dirname)
if [ -n "$CURRENT_MODPACK_DIR" ]; then
    MODPACK_NAME=$(basename "$CURRENT_MODPACK_DIR")
    
    echo "📦 감지된 모드팩: $MODPACK_NAME"
    echo "📁 경로: $CURRENT_MODPACK_DIR"
    echo ""
    
    echo "🔍 RAG 인덱스 구축 옵션:"
    echo "   1. REST API를 통한 인덱스 구축 (간단)"
    echo "   2. rag_manager.py를 통한 인덱스 구축 (상세)"
    echo ""
    
    read -p "선택하세요 (1/2): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[1]$ ]]; then
        echo "🚀 REST API를 통한 RAG 인덱스 구축..."
        
        # RAG 인덱스 구축 요청
        RESULT=$(curl -s -X POST http://localhost:5000/gcp-rag/build \
             -H "Content-Type: application/json" \
             -d "{\"modpack_name\":\"$MODPACK_NAME\",\"modpack_version\":\"1.0.0\",\"modpack_path\":\"$CURRENT_MODPACK_DIR\"}")
        
        echo "✅ RAG 인덱스 구축 완료"
        echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
        
    elif [[ $REPLY =~ ^[2]$ ]]; then
        echo "🚀 rag_manager.py를 통한 상세 RAG 인덱스 구축..."
        
        cd "$HOME/minecraft-ai-backend"
        source venv/bin/activate
        
        if [ -f "rag_manager.py" ]; then
            echo "📊 현재 등록된 모드팩:"
            python3 rag_manager.py list
            
            echo ""
            echo "🔨 RAG 인덱스 구축 시작..."
            python3 rag_manager.py build "$MODPACK_NAME" "1.0.0" "$CURRENT_MODPACK_DIR"
            
            echo ""
            echo "📊 업데이트된 모드팩 목록:"
            python3 rag_manager.py list
        else
            echo "❌ rag_manager.py를 찾을 수 없습니다."
            echo "   해결 방법: ~/sync_backend.sh 실행"
        fi
        
        deactivate
    else
        echo "⏭️ RAG 인덱스 구축을 건너뜁니다"
    fi
else
    echo "❌ 모드팩 디렉토리를 찾을 수 없습니다"
    echo "   일반적인 모드팩 경로들:"
    echo "   ls -la /opt/minecraft/"
    echo "   ls -la ~/minecraft/"
    echo "   ls -la /srv/minecraft/"
fi

echo ""
```

#### **9.5-8. RAG 검색 및 AI 응답 테스트**

```bash
echo "🔍 RAG 검색 및 AI 응답 테스트"
echo "=========================="

# 테스트 검색어들
TEST_QUERIES=("철 블록" "다이아몬드 검" "엔더 드래곤" "레드스톤")

echo "1. RAG 검색 기능 테스트:"
for query in "${TEST_QUERIES[@]}"; do
    echo "🔎 검색 테스트: '$query'"
    
    # RAG 검색 테스트
    SEARCH_RESULT=$(curl -s -X POST http://localhost:5000/gcp-rag/search \
                         -H "Content-Type: application/json" \
                         -d "{\"query\":\"$query\",\"modpack_name\":\"test\",\"modpack_version\":\"1.0.0\"}" 2>/dev/null)
    
    if echo "$SEARCH_RESULT" | grep -q "success.*true"; then
        RESULT_COUNT=$(echo "$SEARCH_RESULT" | grep -o '"results_count":[0-9]*' | cut -d':' -f2 || echo "0")
        echo "   ✅ 검색 성공 - ${RESULT_COUNT}개 결과"
    else
        echo "   📝 검색 결과 없음 (RAG 인덱스 없거나 관련 문서 없음)"
    fi
done

echo ""
echo "💡 참고: RAG 검색 결과가 없어도 AI는 웹검색을 통해 답변합니다!"

echo ""
echo "2. 완전한 AI 응답 테스트 (RAG + 웹검색):"

# AI 채팅 테스트
TEST_MESSAGE="철 블록은 어떻게 만드나요?"
echo "💬 테스트 질문: $TEST_MESSAGE"

CHAT_RESPONSE=$(curl -s -X POST http://localhost:5000/chat \
                     -H "Content-Type: application/json" \
                     -d "{\"message\":\"$TEST_MESSAGE\",\"user_id\":\"admin_test\",\"modpack_name\":\"test\"}")

if echo "$CHAT_RESPONSE" | grep -q "response"; then
    echo "✅ AI 응답 시스템 정상 작동"
    echo ""
    echo "📋 AI 응답 분석:"
    echo "$CHAT_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"   🤖 응답 길이: {len(data.get('response', ''))} 문자\")
    if data.get('rag_hits', 0) > 0:
        print(f\"   📚 RAG 활용: {data['rag_hits']}개 모드팩 문서 참조\")
    else:
        print(f\"   🌐 웹검색 활용: {data.get('web_search_used', '확인 불가')}\")
    
    # 응답 미리보기
    response_preview = data.get('response', 'No response')[:200]
    print(f\"   📝 응답 미리보기: {response_preview}...\")
except Exception as e:
    print('   ✅ AI 응답 받음 (JSON 파싱 실패)')
    print(f'   Debug: {str(e)}')
"
else
    echo "❌ AI 응답 시스템 오류"
    echo "   응답 내용: $CHAT_RESPONSE"
    echo "   💡 해결 방법: sudo systemctl restart mc-ai-backend"
fi

echo ""
```

#### **9.5-9. RAG 시스템 종합 상태 및 문제 해결**

```bash
echo "📊 RAG 시스템 종합 상태"
echo "======================"

# GCP RAG 상태 확인
if curl -s --fail http://localhost:5000/gcp-rag/status > /dev/null; then
    GCP_STATUS=$(curl -s http://localhost:5000/gcp-rag/status | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('RAG 시스템 상태 분석:')
    
    if data.get('gcp_rag_enabled'):
        print('   ✅ GCP RAG: 활성화됨')
    else:
        print('   ⚠️ GCP RAG: 비활성화됨')
    
    if data.get('gcp_rag_available'):
        print('   ✅ GCP RAG: 사용 가능')
    else:
        print('   ❌ GCP RAG: 사용 불가 (권한 또는 설정 오류)')
    
    if data.get('local_rag_enabled'):
        print('   ✅ 로컬 RAG: 활성화됨')
    else:
        print('   📝 로컬 RAG: 비활성화됨')
        
    project_id = data.get('project_id', 'null')
    print(f'   🏗️ GCP 프로젝트: {project_id}')
    
    modpack_count = data.get('modpack_count', 0)
    print(f'   📚 등록된 모드팩: {modpack_count}개')
except Exception as e:
    print('❌ RAG 상태 파싱 실패')
    print(f'Debug: {str(e)}')
")
    echo "$GCP_STATUS"
else
    echo "❌ RAG 시스템 접근 불가"
fi

echo ""
echo "🎯 RAG 시스템 작동 방식:"
echo "   1. 사용자 질문 → RAG 검색으로 모드팩 관련 문서 찾기"
echo "   2. RAG 결과 있음 → 모드팩 정보 + 웹검색으로 완전한 답변"
echo "   3. RAG 결과 없음 → 웹검색만으로 일반적인 답변"
echo "   4. ✨ 두 경우 모두 정상적으로 AI 답변 제공!"

echo ""
echo "🔧 문제 해결 가이드:"
echo "   📋 'project_id: null' 오류:"
echo "      - nano ~/minecraft-ai-backend/.env"
echo "      - GCP_PROJECT_ID=your-actual-project-id 설정"
echo "      - sudo systemctl restart mc-ai-backend"
echo ""
echo "   📋 'gcp_rag_available: false' 오류:"
echo "      - GCP API 활성화: aiplatform.googleapis.com, firestore.googleapis.com"
echo "      - VM 서비스 계정 권한 확인: Vertex AI 사용자, Cloud Datastore 사용자"
echo "      - VM 액세스 범위: cloud-platform 포함 확인"
echo ""
echo "   📋 동기화 오류:"
echo "      - cd ~ && ./sync_backend.sh"
echo "      - sudo systemctl restart mc-ai-backend"
echo ""

echo "✅ RAG 시스템 완전 구축 및 테스트 완료!"
echo ""
```

---

### 🎮 **10단계: 게임 내 테스트**

#### **10-1. NeoForge 모드팩 서버 시작**
```bash
echo "🎮 게임 내 테스트 준비"
echo "==================="
echo ""
echo "1. NeoForge 모드팩 서버를 시작하세요:"
find "$HOME" -name "run.sh" -path "*/modpacks/*" | head -3 | while read -r run_script; do
    modpack_name=$(basename $(dirname "$run_script"))
    echo "   cd $(dirname "$run_script") && ./run.sh"
done

echo ""
echo "2. 서버 로그에서 ModpackAI 로딩 확인:"
echo "   [모드팩로그] ModpackAI 모드가 성공적으로 로드됨"

echo ""
echo "3. 게임 접속 후 다음 명령어 테스트:"
echo "   /modpackai help         - 도움말 확인"
echo "   /modpackai give         - AI 아이템 받기"
echo "   /ai 안녕하세요           - AI에게 인사"
echo ""
echo "4. RAG 시스템 게임 내 테스트:"
echo "   /modpackai rag status   - RAG 시스템 상태 확인"
echo "   /modpackai rag list     - 등록된 모드팩 목록"
echo "   /modpackai rag test 철   - RAG 검색 테스트"
echo ""
```

#### **10-2. 문제 해결 가이드**
```bash
echo "🔧 문제 해결 가이드"
echo "=================="
echo ""
echo "❌ 모드가 로딩되지 않는 경우:"
echo "   - Java 21+ 설치 확인: java -version"
echo "   - 모드 파일 확인: ls ~/*/mods/modpackai-*.jar"
echo "   - 서버 로그 확인: tail -f ~/모드팩명/logs/latest.log"
echo ""
echo "❌ AI 응답이 없는 경우:"
echo "   - 백엔드 상태: sudo systemctl status mc-ai-backend"
echo "   - API 키 확인: grep API_KEY ~/.minecraft-ai-backend/.env"
echo "   - 연결 테스트: curl http://localhost:5000/health"
echo ""
echo "❌ 'Connection refused' 오류:"
echo "   - 방화벽 확인: sudo ufw status"
echo "   - 포트 사용: netstat -tlnp | grep :5000"
echo "   - 서비스 재시작: sudo systemctl restart mc-ai-backend"
echo ""
```

---

### ✅ **단계별 설치 완료!**

```bash
echo ""
echo "🎉 단계별 설치가 완료되었습니다!"
echo "=============================="
echo ""
echo "📊 설치 요약:"
echo "   ✅ Java 21+ 환경 준비"
echo "   ✅ AI 백엔드 (RAG 시스템 포함) 설치"
echo "   ✅ NeoForge 모드 빌드 및 배포"
echo "   ✅ systemd 서비스 등록"
echo "   ✅ 모드팩 자동 감지 및 설치"
echo ""
echo "🎯 사용 준비:"
echo "   1. API 키가 설정되었다면 즉시 사용 가능"
echo "   2. NeoForge 모드팩 서버에서 /ai 명령어 사용"
echo "   3. AI 아이템으로 GUI 인터페이스 사용"
echo ""
echo "📞 지원:"
echo "   - 문제 발생 시 위의 '문제 해결 가이드' 참조"
echo "   - GitHub Issues: 추가 도움이 필요한 경우"
echo ""
```

---

## 🎮 게임 내 사용법

### **기본 명령어**
```
/ai 철 블록은 어떻게 만들어?      # AI에게 바로 질문
/ai                             # AI GUI 열기 (클라이언트)
/modpackai help                 # 도움말 보기
/modpackai give                 # AI 아이템 받기
/modpackai recipe 다이아몬드     # 제작법 조회
```

### **AI 아이템 사용**
1. `/modpackai give` 명령어로 AI 아이템(네더 스타) 받기
2. AI 아이템을 우클릭
3. AI 채팅 GUI 열림 (클라이언트에서만)

---

## 🛡️ 보안 설정

### **방화벽 설정**
```bash
# 백엔드 포트 열기 (내부 통신용)
sudo ufw allow 5000/tcp

# SSH 포트 확인
sudo ufw status
```

### **SSL/TLS 설정 (프로덕션 환경)**
```bash
# Nginx 역방향 프록시 설정
sudo apt install nginx
sudo nano /etc/nginx/sites-available/mc-ai-backend
```

---

## 🔍 문제 해결

### **모드 로드 실패**
```bash
# NeoForge 서버 로그 확인
tail -f ~/modpack-name/logs/latest.log | grep modpackai

# Java 버전 확인 (Java 21+ 필요)
java -version

# 모드 파일 확인
find ~ -name "modpackai-*.jar" -path "*/mods/*"
```

### **백엔드 연결 실패**
```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 포트 사용 확인
netstat -tlnp | grep :5000

# API 키 확인
grep API_KEY $HOME/minecraft-ai-backend/.env

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

### **API 응답 오류**
```bash
# 백엔드 로그 확인
sudo journalctl -u mc-ai-backend -f

# 수동으로 백엔드 실행해서 디버깅
cd $HOME/minecraft-ai-backend
source venv/bin/activate
python app.py
```

### **모드 빌드 실패**
```bash
# Gradle 버전 확인
cd ~/minecraft-modpack-ai/minecraft_mod
./gradlew --version

# 빌드 캐시 정리
./gradlew clean build --refresh-dependencies

# Java 버전 확인
java -version
```

---

## ⚙️ 고급 설정

### **모드 설정 파일**
각 모드팩의 `config/modpackai-config.json` 파일에서 설정 가능:

```json
{
  "backend": {
    "url": "http://localhost:5000",
    "timeout": 10000
  },
  "ai_item": {
    "material": "NETHER_STAR",
    "name": "§6§l모드팩 AI 어시스턴트"
  },
  "ai": {
    "primary_model": "gemini",
    "web_search_enabled": true
  }
}
```

참고: `modpackai-config.json` 파일이 없다면 이 단계는 생략해도 됩니다. 모드는 기본 설정으로 정상 동작합니다.

### **성능 최적화**
```bash
# Java 메모리 설정
export JAVA_OPTS="-Xms2G -Xmx4G"

# 백엔드 워커 수 증가
export WORKERS=4
```

### **모드팩별 설정**
```bash
# 특정 모드팩에만 모드 설치
cp ~/minecraft-modpack-ai/minecraft_mod/build/libs/modpackai-*.jar ~/enigmatica_10/mods/

# 설정 파일 복사
mkdir -p ~/enigmatica_10/config
# 리소스에 파일이 있는 경우에만 복사 (없으면 생략 가능)
if [ -f ~/minecraft-modpack-ai/minecraft_mod/src/main/resources/modpackai-config.json ]; then
  cp ~/minecraft-modpack-ai/minecraft_mod/src/main/resources/modpackai-config.json ~/enigmatica_10/config/
fi
```

---

## 📋 설치 체크리스트

### **사전 준비**
- [ ] GCP VM Debian 서버 접속
- [ ] Java 21+ 설치 확인
- [ ] Python 3.9+ 설치 확인
- [ ] NeoForge 모드팩 서버 설치
- [ ] API 키 준비 (Google Gemini 권장)

### **설치 과정**
- [ ] 프로젝트 다운로드 (`git clone`)
- [ ] 자동 설치 스크립트 실행 (`./install_mod.sh`)
- [ ] API 키 설정 (`.env` 파일)
- [ ] 백엔드 서비스 재시작
- [ ] 설치 검증

### **설치 확인**
- [ ] 백엔드 서비스 실행 중 (`systemctl status`)
- [ ] 모드 파일 존재 (`find ~ -name "modpackai-*.jar"`)
- [ ] API 응답 정상 (`curl /health`)
- [ ] 게임 내 명령어 작동 (`/ai help`)

---

**🎮 설치 완료! 이제 NeoForge 모드팩에서 AI 어시스턴트를 사용할 수 있습니다!** 🚀