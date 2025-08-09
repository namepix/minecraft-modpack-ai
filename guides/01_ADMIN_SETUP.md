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

## 🔧 방법 2: 단계별 설치 (수정됨)

#### 1단계: 기본 도구 및 Java 21 설치
```bash
# 시스템 패키지 업데이트 및 필수 도구 설치
sudo apt-get update
sudo apt-get install -y git curl wget

# Java 21 (Temurin) 설치
sudo apt-get install -y temurin-21-jdk
```

#### 2단계: 프로젝트 클론
```bash
# GitHub에서 프로젝트 클론
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
```

#### 3단계: NeoForge 모드 빌드
```bash
# 모드 디렉토리로 이동
cd minecraft_mod

# Gradle Wrapper 생성 (프로젝트에 맞는 Gradle 버전 설정)
# 참고: 시스템에 설치된 gradle이 오래되었을 수 있으므로, 이 방법이 가장 안정적입니다.
gradle wrapper --gradle-version 8.8 --distribution-type all

# Gradle Wrapper를 사용하여 모드 빌드 (이제 ./gradlew 사용)
# 이 명령은 필요한 모든 파일을 다운로드하고 모드를 컴파일합니다.
./gradlew build
```
- **성공 시**: `minecraft_mod/build/libs/modpackai-1.0.0.jar` 와 같은 파일이 생성됩니다.
- **오류 발생 시**: Java 버전이 21이 맞는지, `build.gradle` 파일에 오타가 없는지 확인하세요.

#### 4단계: AI 백엔드 및 전체 설치
- 모드 빌드가 성공적으로 완료되었다면, 이제 전체 자동 설치를 진행할 수 있습니다.
```bash
# 프로젝트 루트 디렉토리로 이동
cd ..

# 전체 설치 스크립트 실행
# 이 스크립트는 백엔드 설정, 모드 자동 배포, 서비스 등록을 모두 처리합니다.
chmod +x install_mod.sh
./install_mod.sh
```

#### 5단계: API 키 설정 및 서비스 재시작
- 설치 마지막 단계에서 안내되는 `.env` 파일에 API 키를 설정합니다.
```bash
# AI 백엔드 환경 설정 파일 열기
nano ~/minecraft-ai-backend/.env

# 파일 내용에 API 키 추가
# GOOGLE_API_KEY=your-google-api-key-here

# 설정 후 서비스를 재시작하여 변경사항 적용
sudo systemctl restart mc-ai-backend
```

#### 6단계: 설치 확인
```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 모드가 각 모드팩에 잘 설치되었는지 확인
ls ~/*/mods/modpackai-*.jar

# API 상태 확인
curl http://localhost:5000/health
```
- 모든 명령이 오류 없이 실행되면 설치가 완료된 것입니다. 이제 각 모드팩 서버를 시작하여 게임 내에서 AI를 사용할 수 있습니다.

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