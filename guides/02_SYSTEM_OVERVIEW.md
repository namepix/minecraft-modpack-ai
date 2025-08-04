# 🏗️ 마인크래프트 모드팩 AI 시스템 전체 구조

## 📋 시스템 개요

마인크래프트 모드팩 AI 시스템은 게임 내에서 모드팩 관련 질문에 답변하고 제작법을 제공하는 AI 어시스턴트입니다.

### **핵심 구성 요소**
- 🎮 **Minecraft 플러그인**: 게임 내 GUI 및 명령어 처리
- 🤖 **AI 백엔드**: 다중 AI 모델 통합 및 응답 생성
- 📊 **데이터베이스**: 채팅 기록, 제작법, 언어 매핑 저장
- 🔍 **모드팩 분석기**: 모드팩 파일에서 정보 추출
- 🌐 **RAG 시스템**: 벡터 검색을 통한 정확한 정보 제공

---

## 🏛️ 시스템 아키텍처

### **전체 구조도**
```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Minecraft     │ ◄────────────► │   AI Backend    │
│   Plugin        │                │   (Flask)       │
│                 │                │                 │
│  - GUI System   │                │  - AI Models    │
│  - Commands     │                │  - Database     │
│  - Item Events  │                │  - RAG System   │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   Minecraft     │                │   GCP Services  │
│   Server        │                │                 │
│                 │                │  - Cloud Storage│
│  - Modpack      │                │  - Vector DB    │
│  - Players      │                │  - Embeddings   │
└─────────────────┘                └─────────────────┘
```

### **데이터 흐름**
```
사용자 질문 (한글)
    ↓
한글-영어 변환 (하이브리드 매핑)
    ↓
컨텍스트 검색
    ├── 로컬 데이터베이스
    ├── GCP RAG 벡터 검색
    └── AI 웹검색 (필요시)
    ↓
AI 모델 선택 및 응답 생성
    ↓
응답 후처리 (한글(영어) 형식)
    ↓
게임 내 GUI 표시
```

---

## 🔧 핵심 컴포넌트 상세

### **1. Minecraft 플러그인 (Java)**
**위치**: `minecraft_plugin/`

**주요 기능**:
- 🎯 **AIChatGUI**: 통합 채팅 및 제작법 GUI
- 📋 **ModpackAICommand**: 게임 내 명령어 처리
- 🎮 **PlayerInteractListener**: 아이템 우클릭 이벤트
- 🤖 **ModelSelectionGUI**: AI 모델 선택 인터페이스

**핵심 클래스**:
```java
ModpackAIPlugin.java          // 메인 플러그인 클래스
AIChatGUI.java               // 통합 GUI 시스템
ModpackAICommand.java        // 명령어 처리
AIManager.java              // 백엔드 통신 관리
RecipeManager.java          // 제작법 데이터 관리
```

### **2. AI 백엔드 (Python Flask)**
**위치**: `backend/`

**주요 기능**:
- 🤖 **HybridAIModel**: 다중 AI 모델 통합
- 📊 **데이터베이스 관리**: SQLite 기반
- 🔍 **모드팩 분석**: ZIP/JAR 파일 파싱
- 🌐 **RAG 시스템**: 벡터 검색 및 임베딩

**핵심 모듈**:
```python
app.py                      # Flask 메인 애플리케이션
hybrid_ai_model.py         # AI 모델 통합 관리
recipe_manager.py          # 제작법 데이터베이스
chat_manager.py            # 채팅 기록 관리
language_mapper.py         # 한글-영어 매핑
rag_manager.py             # RAG 시스템 관리
modpack_analyzer.py        # 모드팩 파일 분석
```

### **3. 데이터베이스 구조**
**SQLite 데이터베이스**:
- `chat_history.db`: 플레이어별 채팅 기록
- `recipes.db`: 모드팩별 제작법 및 아이템 정보
- `language_mappings.db`: 한글-영어 아이템명 매핑

**주요 테이블**:
```sql
-- 채팅 기록
chat_history (id, player_uuid, user_message, ai_response, timestamp)

-- 제작법 정보
recipes (id, modpack_name, item_name, recipe_type, ingredients, result)

-- 언어 매핑
language_mappings (id, korean_name, english_name, modpack_name, confidence)
```

### **4. RAG (Retrieval Augmented Generation) 시스템**
**구성 요소**:
- **Google Cloud Storage**: 문서 저장
- **SentenceTransformer**: 텍스트 임베딩
- **FAISS**: 벡터 인덱싱 및 검색

**작동 과정**:
```
모드팩 파일 → 텍스트 추출 → 임베딩 생성 → 벡터 저장
    ↓
사용자 질문 → 임베딩 생성 → 벡터 검색 → 관련 문서 검색
    ↓
AI 모델에 컨텍스트 제공 → 정확한 응답 생성
```

---

## 🔄 데이터 처리 파이프라인

### **1. 모드팩 분석 파이프라인**
```
모드팩 파일 (ZIP/JAR)
    ↓
파일 압축 해제
    ├── mods/ 폴더 스캔
    ├── data/ 폴더 스캔
    └── assets/ 폴더 스캔
    ↓
JSON 파일 파싱
    ├── recipes/ 폴더
    ├── items/ 폴더
    └── blocks/ 폴더
    ↓
데이터베이스 저장
    ├── 제작법 정보
    ├── 아이템 정보
    └── 모드 정보
    ↓
RAG 시스템 업데이트
    ├── 텍스트 임베딩
    ├── 벡터 인덱스
    └── GCS 저장
```

### **2. 질문 처리 파이프라인**
```
사용자 질문 (한글)
    ↓
한글-영어 변환
    ├── 사용자 정의 매핑
    ├── 일반 매핑
    ├── 부분 매칭
    └── AI 기반 변환
    ↓
컨텍스트 검색
    ├── 로컬 DB 검색
    ├── RAG 벡터 검색
    └── 웹 검색 (필요시)
    ↓
AI 모델 선택
    ├── 기본 모델
    ├── 사용자 선택
    └── 무료 크레딧 확인
    ↓
응답 생성
    ├── 컨텍스트 + 질문 조합
    ├── AI 모델 처리
    └── 응답 후처리
    ↓
한글(영어) 형식 변환
    ↓
게임 내 표시
```

### **3. 제작법 처리 파이프라인**
```
제작법 질문
    ↓
아이템명 추출 및 변환
    ↓
데이터베이스 검색
    ├── recipes 테이블
    ├── items 테이블
    └── version_mappings 테이블
    ↓
제작법 데이터 수집
    ├── 재료 목록
    ├── 결과 아이템
    ├── 제작법 타입
    └── 모드 정보
    ↓
GUI 형식 변환
    ├── 3x3 그리드 매핑
    ├── 아이템 아이콘 생성
    └── 정보 텍스트 생성
    ↓
게임 내 표시
```

---

## 🤖 AI 모델 통합

### **지원하는 AI 모델**
1. **OpenAI**
   - GPT-3.5 Turbo (빠르고 저렴)
   - GPT-4 (정확도 높음)

2. **Anthropic**
   - Claude 3 Haiku (빠르고 효율적)
   - Claude 3 Sonnet (균형잡힌 성능)

3. **Google**
   - Gemini Pro (무료 크레딧 제공)

### **모델 선택 전략**
- **기본**: GPT-3.5 Turbo
- **정확도 우선**: GPT-4, Claude 3 Sonnet
- **속도 우선**: Claude 3 Haiku
- **비용 절약**: Gemini Pro

### **무료 크레딧 관리**
- 각 모델별 사용량 모니터링
- 크레딧 소진 시 자동 알림
- 사용자에게 모델 변경 안내

---

## 🌐 API 엔드포인트

### **주요 API**
```
POST /api/chat                    # AI 채팅
GET  /api/recipe/<item_name>      # 제작법 조회
POST /api/modpack/switch          # 모드팩 변경
GET  /api/chat/history/<uuid>     # 채팅 기록
POST /api/language/mapping        # 언어 매핑 추가
GET  /api/models                  # AI 모델 목록
POST /api/models/switch           # AI 모델 변경
GET  /health                      # 상태 확인
```

### **API 응답 형식**
```json
{
  "success": true,
  "message": "응답 메시지",
  "data": {
    "ai_response": "AI 응답 내용",
    "recipe_data": "제작법 정보",
    "context": "사용된 컨텍스트"
  }
}
```

---

## 🔒 보안 및 성능

### **보안 기능**
- **Rate Limiting**: API 요청 제한
- **Input Validation**: 입력 데이터 검증
- **XSS Prevention**: 크로스 사이트 스크립팅 방지
- **UUID 기반 인증**: 플레이어 식별

### **성능 최적화**
- **응답 캐싱**: 중복 질문 캐싱
- **데이터베이스 인덱싱**: 빠른 검색
- **비동기 처리**: 백그라운드 작업
- **메모리 관리**: 효율적인 리소스 사용

### **모니터링**
- **시스템 상태**: CPU, 메모리, 디스크 사용량
- **API 응답 시간**: 성능 모니터링
- **오류 로깅**: 문제 추적 및 디버깅
- **사용량 통계**: AI 모델별 사용량

---

## 📊 시스템 요구사항

### **서버 사양**
- **CPU**: 2 vCPU 이상 (권장: 4 vCPU)
- **RAM**: 4GB 이상 (권장: 8GB)
- **Storage**: 20GB 이상 (SSD 권장)
- **Network**: 외부 IP 주소

### **소프트웨어 요구사항**
- **OS**: Debian 11+ 또는 Ubuntu 20.04+
- **Python**: 3.8+
- **Java**: 11+
- **Maven**: 플러그인 빌드용

### **외부 서비스**
- **OpenAI API**: GPT 모델 사용
- **Anthropic API**: Claude 모델 사용
- **Google Cloud**: RAG 시스템 (선택사항)

---

## 🚀 확장성 및 유지보수

### **확장 가능한 구조**
- **모듈화**: 각 컴포넌트 독립적 개발
- **플러그인 아키텍처**: 새로운 기능 쉽게 추가
- **API 기반**: 다양한 클라이언트 지원
- **데이터베이스 마이그레이션**: 스키마 업데이트

### **유지보수 기능**
- **자동 백업**: 데이터베이스 백업
- **로그 관리**: 체계적인 로깅
- **모니터링**: 시스템 상태 실시간 확인
- **업데이트**: 자동 업데이트 스크립트

---

## 🎯 사용 시나리오

### **일반 사용자**
1. 게임 내에서 AI 어시스턴트 아이템 획득
2. 우클릭하여 GUI 열기
3. 모드팩 관련 질문 입력
4. AI 응답 및 제작법 확인

### **관리자**
1. CLI에서 모드팩 변경: `modpack_switch <모드팩명>`
2. 게임 내에서 관리자 명령어 사용
3. 시스템 모니터링 및 관리
4. AI 모델 선택 및 설정

### **개발자**
1. 플러그인 코드 수정 및 빌드
2. 백엔드 API 확장
3. 새로운 AI 모델 추가
4. 데이터베이스 스키마 업데이트

---

## 📈 성능 지표

### **응답 시간**
- **로컬 DB 검색**: < 100ms
- **RAG 벡터 검색**: < 500ms
- **AI 모델 응답**: 1-5초
- **전체 응답**: 1-6초

### **정확도**
- **제작법 정보**: 95%+
- **아이템 정보**: 90%+
- **한글-영어 변환**: 85%+
- **AI 응답 품질**: 모델에 따라 80-95%

### **동시 사용자**
- **권장**: 5-8명
- **최대**: 10-15명
- **확장 가능**: 로드 밸런싱으로 증가 가능

---

## 🔮 향후 개발 계획

### **단기 계획**
- [ ] 더 많은 AI 모델 지원
- [ ] 음성 인식 기능 추가
- [ ] 모바일 앱 개발
- [ ] 실시간 번역 기능

### **장기 계획**
- [ ] 클라우드 네이티브 아키텍처
- [ ] 마이크로서비스 분리
- [ ] 머신러닝 모델 자체 개발
- [ ] 다국어 지원 확대

---

**🎮 이 시스템은 마인크래프트 모드팩 플레이어들에게 더 나은 게임 경험을 제공합니다!** 🚀 