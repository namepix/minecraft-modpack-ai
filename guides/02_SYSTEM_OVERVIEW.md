# 🏗️ 시스템 전체 구조 가이드

## 📋 개요

마인크래프트 모드팩 AI 시스템은 Gemini 2.5 Pro 웹검색 기반의 간소화된 아키텍처로 설계되었습니다.
**NeoForge 모드 방식**으로 구현되어 안정성과 호환성이 크게 향상되었습니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                  마인크래프트 모드팩 AI 시스템 (모드 방식)              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Minecraft     │ ◄────────────► │   AI Backend    │
│   NeoForge Mod  │                │   (Flask)       │
│                 │                │                 │
│  - AI 명령어     │                │  - Gemini 2.5   │
│  - Screen GUI    │                │    Pro (메인)    │
│  - 이벤트 핸들러  │                │  - 웹검색 지원   │
│  - 채팅 관리     │                │  - 미들웨어      │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   NeoForge      │                │  Google Search  │
│   Modpack Server│                │   & AI APIs     │
│                 │                │                 │
│  - 모드팩 운영   │                │  - 실시간 검색   │
│  - 플레이어 관리 │                │  - OpenAI 백업   │
│  - 게임 로직     │                │  - Anthropic    │
└─────────────────┘                └─────────────────┘
```

## 🎯 주요 컴포넌트

### 1. 📦 NeoForge 모드 (Java)

**위치**: `minecraft_mod/src/main/java/com/modpackai/`

**주요 클래스**:
```
com.modpackai/
├── ModpackAIMod.java                    # 메인 모드 클래스
├── commands/
│   └── ModpackAICommands.java          # /ai, /modpackai 명령어 처리
├── events/
│   └── PlayerInteractionHandler.java    # 플레이어 상호작용 이벤트
├── gui/
│   └── AIChatScreen.java               # AI 채팅 Screen GUI
└── managers/
    ├── ModpackAIConfig.java            # 설정 관리 (JSON)
    └── ModpackAIManager.java           # AI API 통신 관리
```

**주요 기능**:
- ✅ AI 어시스턴트 명령어 처리 (Brigadier 기반)
- ✅ Screen API 기반 채팅 시스템
- ✅ 플레이어 상호작용 감지 (@SubscribeEvent)
- ✅ HTTP API 통신 (Java 11+ HttpClient)

**플러그인과의 차이점**:
- **명령어 시스템**: CommandExecutor → Brigadier Commands
- **GUI 시스템**: Inventory GUI → Screen API
- **이벤트 처리**: @EventHandler → @SubscribeEvent
- **설정 관리**: YML → JSON
- **초기화**: onEnable() → @Mod + FMLCommonSetupEvent

### 2. 🚀 AI 백엔드 (Python Flask)

**위치**: `backend/`

**파일 구조**:
```
backend/
├── app.py                      # 메인 Flask 애플리케이션
├── middleware/
│   ├── security.py            # 보안 미들웨어
│   └── monitoring.py          # 모니터링 미들웨어
├── tests/                     # 테스트 코드
├── requirements.txt           # Python 의존성
└── run_tests.py              # 테스트 실행 스크립트
```

**주요 기능**:
- ✅ Gemini 2.5 Pro 웹검색 API 통합
- ✅ 다중 AI 모델 지원 (OpenAI, Anthropic 백업)
- ✅ 보안 미들웨어 (Rate Limiting, Input Validation)
- ✅ 성능 모니터링
- ✅ RESTful API 제공

### 3. ⚙️ 설정 시스템

**모드 설정**: `config/modpackai-config.json`
```json
{
  "backend": {
    "url": "http://localhost:5000",
    "timeout": 10000
  },
  "ai_item": {
    "material": "NETHER_STAR",
    "name": "§6§l모드팩 AI 어시스턴트",
    "lore": "§7우클릭으로 AI 채팅창을 열 수 있습니다"
  },
  "ai": {
    "primary_model": "gemini",
    "web_search_enabled": true
  }
}
```

**환경 변수**: `.env`
```env
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
PORT=5000
DEBUG=false
```

## 🔄 데이터 플로우

### 1. 플레이어 질문 플로우
```
1. 플레이어가 `/ai 질문` 또는 GUI에서 메시지 입력
2. NeoForge 모드가 질문을 받음
3. HTTP POST /chat로 백엔드에 요청
4. 백엔드가 Gemini 2.5 Pro에 웹검색과 함께 질의
5. AI 응답을 모드로 반환
6. 모드가 플레이어에게 응답 표시
```

### 2. 제작법 조회 플로우
```
1. 플레이어가 `/modpackai recipe <아이템>` 입력
2. HTTP GET /recipe/<item_name>로 요청
3. 백엔드가 웹검색을 통해 최신 제작법 정보 검색
4. 구조화된 제작법 데이터 반환
5. 채팅 또는 GUI에 제작법 표시
```

### 3. AI 아이템 상호작용 플로우
```
1. 플레이어가 AI 아이템(네더 스타) 우클릭
2. PlayerInteractionHandler에서 이벤트 감지
3. 클라이언트 측: AIChatScreen 열기
4. 서버 측: 안내 메시지 전송
```

## 🛡️ 보안 아키텍처

### 1. 미들웨어 시스템
```python
# security.py
- Rate Limiting (요청 제한)
- Input Validation (입력 검증)
- XSS Prevention (크로스사이트 스크립팅 방지)
- Request Size Limiting (요청 크기 제한)

# monitoring.py  
- Performance Tracking (성능 추적)
- Error Logging (에러 로깅)
- Usage Statistics (사용 통계)
```

### 2. API 키 관리
- 환경 변수를 통한 안전한 저장
- 여러 AI 모델의 폴백 시스템
- 자동 유효성 검증

## 🔧 관리 도구

### 1. 스크립트 파일들
```bash
install_mod.sh          # 모드 자동 설치 스크립트
monitor.sh              # 시스템 모니터링
update.sh               # 업데이트 스크립트
deploy.sh               # 배포 스크립트
emergency.sh            # 응급 복구 스크립트
modpack_switch.sh       # 모드팩 변경 스크립트
```

### 2. 테스트 시스템
```bash
test_local.sh           # 로컬 테스트
test_remote.sh          # 원격 테스트
test_runner.py          # Python 테스트 실행기
```

## 📊 API 엔드포인트

### 1. 기본 엔드포인트
```http
GET  /health                    # 서버 상태 확인
POST /chat                      # AI 채팅
GET  /models                    # 사용 가능한 AI 모델 목록
POST /models/switch             # AI 모델 전환
```

### 2. 제작법 엔드포인트
```http
GET /recipe/<item_name>         # 아이템 제작법 조회
```

### 3. 요청/응답 예시
**채팅 요청**:
```json
POST /chat
{
  "message": "철 블록 만드는 법",
  "player_uuid": "12345678-1234-5678-9012-123456789abc",
  "modpack_name": "Enigmatica 10",
  "modpack_version": "1.0.0"
}
```

**채팅 응답**:
```json
{
  "success": true,
  "response": "철 블록은 철 주괴 9개로 만들 수 있습니다...",
  "model": "gemini",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## 🎯 성능 최적화

### 1. 캐싱 전략
- 웹검색 결과 캐싱 (6시간)
- 자주 조회되는 제작법 캐싱
- API 응답 캐싱

### 2. 비용 최적화
- Gemini 2.5 Pro 우선 사용 (GCP 크레딧 활용)
- 폴백 시스템으로 비용 제어
- 요청 빈도 제한

### 3. 모니터링 메트릭
- 응답 시간 추적
- API 사용량 모니터링
- 에러율 추적
- 사용자 활동 분석

## 🔄 플러그인 vs 모드 비교

| 측면 | 플러그인 (기존) | 모드 (현재) |
|------|------|------|
| **서버 요구사항** | 하이브리드 서버 필요 | 순수 NeoForge 서버 |
| **안정성** | ❌ 오류 많음 | ✅ 안정적 |
| **설치 복잡도** | 복잡 (하이브리드 서버) | 간단 (모드만 설치) |
| **명령어 시스템** | CommandExecutor | Brigadier (더 강력) |
| **GUI 시스템** | Inventory 기반 | Screen 기반 (더 유연) |
| **설정 관리** | YML | JSON (더 구조화) |
| **이벤트 처리** | @EventHandler | @SubscribeEvent |
| **빌드 시스템** | Maven | Gradle |
| **사용자 경험** | 동일 | 동일 (향상됨) |

## 🔮 확장 가능성

### 1. 추가 AI 모델 지원
- 새로운 AI 모델 쉽게 추가 가능
- 동적 모델 선택 시스템
- 모델별 성능 최적화

### 2. 기능 확장
- 음성 인식/합성
- 이미지 생성
- 실시간 번역
- 게임 내 자동화

### 3. 스케일링
- 다중 서버 지원
- 로드 밸런싱
- 데이터베이스 연동
- 클라우드 네이티브 배포

---

**🎮 이 모드 기반 아키텍처는 하이브리드 서버의 문제점을 해결하고 더 안정적인 AI 경험을 제공합니다!** 🚀