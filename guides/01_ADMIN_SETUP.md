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
- ✅ Gradle 설치 (모드 빌드용)

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
**터미널에서 다음 명령어를 입력하세요:**

```bash
chmod +x install_mod.sh
./install_mod.sh
```

**설명**: 
- `chmod +x install_mod.sh` : 모드 설치 스크립트에 실행 권한을 부여
- `./install_mod.sh` : 모드 설치 스크립트를 실행

**이 스크립트가 자동으로 수행하는 작업:**
- ✅ AI 백엔드 설치 및 설정
- ✅ **NeoForge 모드 빌드** (Gradle 사용)
- ✅ 모든 NeoForge 모드팩에 **ModpackAI 모드** 설치
- ✅ API 키 설정 확인
- ✅ 백엔드 서비스 시작
- ✅ 모든 모드팩 AI 분석

### **3단계: API 키 설정 (필수)**
스크립트 실행 중 API 키 설정 안내가 나타납니다. 

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

### **4단계: 설치 완료 확인**
**터미널에서 다음 명령어로 상태를 확인하세요:**

```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 모드 설치 확인
ls ~/*/mods/modpackai-*.jar

# API 테스트
curl http://localhost:5000/health
```

**성공적인 설치 확인 방법:**
- ✅ `mc-ai-backend` 서비스가 `active (running)` 상태
- ✅ 각 모드팩의 `mods/` 폴더에 `modpackai-1.0.0.jar` 파일 존재
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
```bash
cd ~/minecraft-modpack-ai/minecraft_mod
./gradlew build
```

### **3단계: 모드 설치**
```bash
# 빌드된 모드를 각 모드팩에 복사
for modpack in ~/*/; do
    if [ -d "$modpack/mods" ]; then
        cp build/libs/modpackai-1.0.0.jar "$modpack/mods/"
        echo "ModpackAI 모드 설치 완료: $modpack"
    fi
done
```

### **4단계: 백엔드 서비스 설정**
```bash
# 서비스 등록
sudo cp ~/minecraft-modpack-ai/mc-ai-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mc-ai-backend
sudo systemctl start mc-ai-backend
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
```

### **백엔드 연결 실패**
```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 포트 사용 확인
netstat -tlnp | grep :5000

# API 키 확인
grep API_KEY $HOME/minecraft-ai-backend/.env
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

### **성능 최적화**
```bash
# Java 메모리 설정
export JAVA_OPTS="-Xms2G -Xmx4G"

# 백엔드 워커 수 증가
export WORKERS=4
```

---

**🎮 설치 완료! 이제 NeoForge 모드팩에서 AI 어시스턴트를 사용할 수 있습니다!** 🚀