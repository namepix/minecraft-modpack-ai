# 🚀 빠른 시작 가이드

## ⚡ 5분 만에 시작하기

### 1단계: 프로젝트 다운로드
```bash
git clone https://github.com/your-username/minecraft-modpack-ai.git
cd minecraft-modpack-ai
```

### 2단계: 설치

**Windows:**
```cmd
# PowerShell에서 실행
.\install.ps1
```

**Linux:**
```bash
chmod +x install.sh
./install.sh
```

### 3단계: API 키 설정

**Windows:**
```cmd
setup_env.bat
```

**Linux:**
```bash
cp env.example .env
nano .env
```

Google AI Studio에서 API 키 발급: https://aistudio.google.com/app/apikey

### 4단계: 백엔드 시작

**Windows:**
```cmd
start_backend.bat
```

**Linux:**
```bash
cd backend
python app.py
```

### 5단계: 플러그인 설치

**Windows:**
```cmd
build_plugin.bat
```

**Linux:**
```bash
cd minecraft_plugin
mvn clean package
```

빌드된 `ModpackAI-1.0.jar`를 마인크래프트 서버의 `plugins/` 폴더에 복사

### 6단계: 테스트

**API 테스트 (Windows):**
```cmd
test_api.bat
```

**API 테스트 (Linux):**
```bash
curl http://localhost:5000/health
```

**게임 내 테스트:**
```
/modpackai help
/give @p book 1
# 책을 들고 우클릭
```

## 🎯 주요 기능

- **🤖 Gemini 2.5 Pro**: 웹검색 지원 AI 모델
- **🎮 게임 내 GUI**: 직관적인 채팅 인터페이스
- **🛠️ 제작법 조회**: 시각적 3x3 그리드 표시
- **🌐 다중 언어**: 한글/영어 혼용 가능
- **🔒 보안**: 내장 보안 및 모니터링

## 📝 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `/ai <질문>` | AI에게 바로 질문 |
| `/modpackai chat` | AI 채팅 GUI 열기 |
| `/modpackai recipe <아이템>` | 제작법 조회 |
| `/modpackai help` | 도움말 |

## 🏗️ 프로젝트 구조

```
minecraft-modpack-ai/
├── backend/                    # Python Flask 백엔드
├── minecraft_plugin/           # Java Minecraft 플러그인
├── config/                     # 설정 파일들
├── guides/                     # 상세 가이드 문서들
├── .env                       # 환경 변수 (생성됨)
├── install.ps1               # Windows 설치 스크립트
├── install.sh                # Linux 설치 스크립트
└── start_backend.bat         # Windows 백엔드 시작
```

## 🚨 문제 해결

### 백엔드가 시작되지 않을 때
1. Python 3.8+ 설치 확인
2. 가상환경 활성화 확인
3. `.env` 파일의 API 키 설정 확인

### 플러그인이 로드되지 않을 때
1. Java 11+ 설치 확인
2. JAR 파일이 `plugins/` 폴더에 있는지 확인
3. 서버 로그에서 오류 메시지 확인

### AI가 응답하지 않을 때
1. 백엔드 서비스 실행 확인: http://localhost:5000/health
2. API 키 유효성 확인
3. 네트워크 연결 상태 확인

## 📚 더 자세한 정보

- [관리자 설정 가이드](guides/01_ADMIN_SETUP.md)
- [시스템 구조 설명](guides/02_SYSTEM_OVERVIEW.md)
- [게임 내 사용법](guides/03_GAME_COMMANDS.md)
- [모드팩 변경 방법](guides/04_MODPACK_SWITCH.md)
- [개발자 가이드](guides/05_DEVELOPMENT.md)

## 💡 팁

- **무료 사용**: Google AI Studio API 키로 무료 크레딧 활용
- **최신 정보**: Gemini 웹검색으로 실시간 모드 정보 확인
- **멀티플랫폼**: Windows/Linux 모두 지원
- **확장 가능**: 새로운 AI 모델 쉽게 추가 가능

---

**🎮 즐거운 모드팩 플레이 되세요!** 🚀