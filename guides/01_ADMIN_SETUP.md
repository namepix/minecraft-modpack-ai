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
- ✅ Java 17+ 설치 확인
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

## 🔧 방법 2: 단계별 설치

### **1단계: AI 백엔드 설치**
```bash
cd ~/minecraft-modpack-ai/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **2단계: NeoForge 모드 빌드**

1) 프로젝트 경로로 이동
```bash
cd ~/minecraft-modpack-ai/minecraft_mod
```

2) 플러그인 저장소 설정(settings.gradle/ settings.gradle.kts)
- Groovy DSL(`settings.gradle`) 사용 시 다음 블록을 포함해야 합니다:
```groovy
pluginManagement {
  repositories {
    maven { url 'https://maven.neoforged.net/releases' }
    gradlePluginPortal()
    mavenCentral()
  }
}
dependencyResolutionManagement {
  repositories {
    maven { url 'https://maven.neoforged.net/releases' }
    mavenCentral()
  }
}
rootProject.name = 'modpackai'
```
- Kotlin DSL(`settings.gradle.kts`)을 사용한다면:
```kotlin
pluginManagement {
  repositories {
    maven("https://maven.neoforged.net/releases")
    gradlePluginPortal()
    mavenCentral()
  }
}
dependencyResolutionManagement {
  repositories {
    maven("https://maven.neoforged.net/releases")
    mavenCentral()
  }
}
rootProject.name = "modpackai"
```

3) Gradle 래퍼 사용(권장) 및 최신화
- 시스템에 설치된 Debian 패키지 gradle(4.x)은 너무 구버전입니다. 사용하지 마세요.
- 래퍼가 있으면 바로 사용:
```bash
if [ -x ./gradlew ]; then ./gradlew --version; fi
```
- 래퍼가 없거나 구버전이면 임시 Gradle로 래퍼 생성/업데이트:
```bash
# 임시 Gradle 8.10.2 설치(세션 한정 PATH)
wget -q https://services.gradle.org/distributions/gradle-8.10.2-bin.zip -O /tmp/gradle.zip
sudo mkdir -p /opt/gradle && sudo unzip -q /tmp/gradle.zip -d /opt/gradle
export PATH=/opt/gradle/gradle-8.10.2/bin:$PATH

# 래퍼 생성/업데이트 후 래퍼만 사용
gradle wrapper --gradle-version 8.10.2
./gradlew --version
```

4) 빌드 실행
```bash
./gradlew --refresh-dependencies clean build
```

5) 참고: build.gradle(또는 build.gradle.kts)에 플러그인 선언이 있어야 합니다
```groovy
plugins {
  id 'net.neoforged.gradle' version '7.0.80'
}
```
Kotlin DSL일 경우 문법만 다르고 내용은 동일합니다.

6) 쉬운 방법: 자동 준비/빌드 스크립트 사용(권장)
```bash
cd ~/minecraft-modpack-ai
chmod +x scripts/prepare_mod_build.sh
./scripts/prepare_mod_build.sh
```
설명:
- Gradle 8.10.2 임시 설치 및 래퍼 생성/사용을 자동 처리
- settings.gradle(.kts)에 NeoForged 저장소가 없으면 백업 후 안전하게 작성
- `./gradlew --refresh-dependencies clean build` 실행 후 결과 JAR 경로 안내

### **3단계: 모드 설치**
```bash
# 빌드된 모드를 각 모드팩에 복사
for modpack in ~/*/; do
    if [ -d "$modpack/mods" ]; then
        # 정확한 파일명 확인 후 복사
        MOD_FILE=$(find build/libs -name "modpackai-*.jar" | head -1)
        if [ -n "$MOD_FILE" ]; then
            cp "$MOD_FILE" "$modpack/mods/"
            echo "ModpackAI 모드 설치 완료: $modpack"
        fi
    fi
done
```

### **4단계: 백엔드 서비스 설정**
```bash
# install_mod.sh 스크립트의 서비스 설정 부분 실행
cd ~/minecraft-modpack-ai
./install_mod.sh --service-only
```

### **5단계: RAG 준비(선택, 권장)**
```bash
# 모드팩 디렉토리를 분석하여 RAG 인덱스 자동 구축(분석+구축 한 번에)
curl -s -X POST http://localhost:5000/api/modpack/switch \
  -H 'Content-Type: application/json' \
  -d '{"modpack_path":"~/enigmatica_10","modpack_name":"Enigmatica 10","modpack_version":"1.0.0"}' | jq .

# 상태 확인
curl -s http://localhost:5000/rag/status | jq .

# 필요 시 수동 구축도 가능
curl -s -X POST http://localhost:5000/rag/build \
  -H 'Content-Type: application/json' \
  -d '{"docs":[{"text":"다이아몬드 블록=다이아 주괴x9","source":"wiki"}]}' | jq .

# 인덱스 영속화
curl -s -X POST http://localhost:5000/rag/save | jq .
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

# Java 버전 확인 (Java 17+ 필요)
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
gradle --version

# 빌드 캐시 정리
cd ~/minecraft-modpack-ai/minecraft_mod
./gradlew clean build

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
- [ ] Java 17+ 설치 확인
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