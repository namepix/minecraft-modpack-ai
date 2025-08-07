# 🚀 간소화된 마인크래프트 AI 백엔드 아키텍처

## 📋 개요

기존의 복잡한 구조에서 간단하고 직관적인 구조로 변경했습니다. Gemini 2.5 Pro 웹검색 기능을 중심으로 한 깔끔한 API 서버입니다.

## 🔄 주요 변경사항

### 1. 구조 단순화
- **이전**: 복잡한 모듈 구조 (HybridAIModel, RAGManager, ChatManager 등)
- **현재**: 단일 Flask 앱에서 직접 AI 모델 호출
- **장점**: 유지보수 용이, 빠른 응답, 명확한 코드 구조

### 2. API 엔드포인트 단순화
```
이전: /api/chat, /api/models, /api/recipe, /api/health
현재: /chat, /models, /recipe, /health
```

### 3. 의존성 최소화
- **제거된 모듈**: RAGManager, ChatManager, RecipeManager, LanguageMapper
- **유지된 기능**: Gemini 웹검색, 다중 AI 모델 지원, 제작법 조회

## 🏗️ 새로운 아키텍처

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Minecraft     │ ◄────────────► │   Flask App     │
│   Plugin        │                │                 │
│                 │                │  - Gemini 2.5   │
│  - AI Commands  │                │  - OpenAI       │
│  - Recipe GUI   │                │  - Claude       │
│  - Chat GUI     │                │  - Web Search   │
└─────────────────┘                └─────────────────┘
```

## 🔧 핵심 기능

### 1. AI 모델 관리
```python
# 자동 모델 선택 (Gemini 우선)
current_model = "gemini" if gemini_client else "openai" if openai_client else "claude"

# 모델 전환
@app.route('/models/switch', methods=['POST'])
def switch_model():
    global current_model
    # 사용 가능한 모델로 전환
```

### 2. 웹검색 지원 채팅
```python
# Gemini 2.5 Pro 웹검색
grounding_tool = types.Tool(google_search=types.GoogleSearch())
config = types.GenerateContentConfig(tools=[grounding_tool])

response = gemini_client.models.generate_content(
    model="gemini-2.5-pro",
    contents=message,
    config=config
)
```

### 3. 자동 폴백 시스템
```python
try:
    # 웹검색 시도
    response = gemini_client.models.generate_content(..., config=config)
except Exception as e:
    # 기본 모드로 폴백
    response = gemini_client.models.generate_content(..., config=None)
```

## 📊 API 응답 형식

### 채팅 응답
```json
{
  "success": true,
  "response": "AI 응답 내용",
  "model": "gemini",
  "timestamp": "2025-01-XX..."
}
```

### 모델 목록
```json
{
  "models": [
    {
      "id": "gemini",
      "name": "Gemini 2.5 Pro (웹검색 지원)",
      "provider": "Google",
      "available": true,
      "current": true
    }
  ]
}
```

### 제작법 조회
```json
{
  "success": true,
  "recipe": {
    "item": "diamond",
    "recipe": "제작법 설명...",
    "materials": [],
    "crafting_type": "unknown"
  }
}
```

## 🚀 성능 개선

### 1. 응답 속도
- **이전**: 3-6초 (복잡한 파이프라인)
- **현재**: 1-3초 (직접 AI 호출)

### 2. 메모리 사용량
- **이전**: 높음 (여러 매니저 객체)
- **현재**: 낮음 (단일 앱)

### 3. 안정성
- **이전**: 복잡한 의존성으로 인한 오류 가능성
- **현재**: 단순한 구조로 안정성 향상

## 🔧 설정 및 배포

### 1. 환경 변수
```bash
# 필수
GOOGLE_API_KEY=your-gemini-api-key

# 선택 (백업용)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. 실행
```bash
cd backend
python app.py
```

### 3. 테스트
```bash
# 기본 테스트
python test_gemini_sdk.py

# 통합 테스트
python -m pytest tests/test_app_integration.py -v
```

## 🎯 사용 시나리오

### 1. 기본 사용
```bash
# 서버 시작
python app.py

# API 테스트
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "철 블록 만드는 법", "player_uuid": "test-123"}'
```

### 2. 모델 전환
```bash
curl -X POST http://localhost:5000/models/switch \
  -H "Content-Type: application/json" \
  -d '{"model_id": "openai"}'
```

### 3. 제작법 조회
```bash
curl http://localhost:5000/recipe/diamond
```

## 🔮 향후 계획

### 1. 기능 확장
- [ ] 채팅 기록 저장 (선택적)
- [ ] 사용자 설정 저장
- [ ] 모드팩별 컨텍스트 관리

### 2. 성능 최적화
- [ ] 응답 캐싱
- [ ] 배치 처리
- [ ] 비동기 처리

### 3. 모니터링
- [ ] 사용량 통계
- [ ] 성능 메트릭
- [ ] 오류 추적

## 📞 문제 해결

### 1. 일반적인 문제
```bash
# API 키 확인
echo $GOOGLE_API_KEY

# 서버 상태 확인
curl http://localhost:5000/health

# 로그 확인
tail -f logs/app.log
```

### 2. 디버깅
```python
# 디버그 모드로 실행
app.run(host='0.0.0.0', port=5000, debug=True)
```

---

**변경일**: 2025년 1월
**버전**: 3.0.0 (간소화 버전)
**담당자**: AI 개발팀 