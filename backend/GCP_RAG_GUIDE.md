# 🚀 GCP RAG 시스템 사용 가이드

GCP를 활용한 고급 RAG(Retrieval-Augmented Generation) 시스템 구축 및 사용법

## 📋 개요

### 🎯 목표
- **모드팩별 전용 지식 베이스** 구축
- **실시간 벡터 검색**으로 관련 정보 추출
- **개발자용 디버그 도구**로 검색 결과 실시간 확인
- **토큰 사용량 최적화**로 AI API 비용 절약
- **간편한 롤백 시스템**으로 안전한 테스트

### 🏗️ 아키텍처
```
모드팩 파일들 → 벡터화 → GCP Firestore → 검색 → AI(웹검색) → 답변
      ↓                    ↓              ↓
   recipes.json        임베딩 생성      유사도 검색
   mods/*.jar         Vertex AI       상위 K개 선택
   kubejs/*.js       텍스트 청킹      토큰 제한 적용
```

## 🛠️ 설치 및 설정

### 1. 기본 요구사항
```bash
# Python 3.9+
python --version

# 기본 백엔드 의존성 설치
pip install -r requirements.txt
```

### 2. GCP RAG 시스템 설치
```bash
# GCP RAG 시스템 설치
./install_gcp_rag.sh

# 또는 수동 설치
pip install -r requirements-gcp-rag.txt
```

### 3. GCP 프로젝트 설정 (웹 브라우저 사용) 🌐

#### 3.1 Google 계정으로 GCP 콘솔 접속
1. **Chrome 브라우저**에서 https://console.cloud.google.com 접속
2. **Google 계정으로 로그인** (Gmail 계정 사용 가능)

**🆕 신규 사용자인 경우:**
- **약관 동의** 및 **결제 정보 등록** 필요 ⚠️
- **무료 크레딧 $300** 제공
- **신용카드** 등록 필요하지만 무료 한도 내에서는 과금되지 않음

**🔄 기존 GCP 사용자인 경우:** 
- 이미 설정된 **결제 계정** 및 **프로젝트**가 있을 수 있음
- **무료 크레딧을 이미 사용** 중이어도 문제 없음
- **Always Free 티어** 제품들은 계속 무료로 사용 가능:
  - Firestore: 매일 **20,000회 읽기**, **20,000회 쓰기** 무료
  - Vertex AI: 매월 **일정 임베딩 호출** 무료 제공
- **기존 프로젝트 사용** 또는 **새 프로젝트 생성** 모두 가능

#### 3.2 프로젝트 선택 또는 생성

**📋 옵션 1: 새 프로젝트 생성 (권장)**
1. **상단 프로젝트 선택 드롭다운** 클릭
2. **"새 프로젝트"** 버튼 클릭
3. 프로젝트 정보 입력:
   ```
   프로젝트 이름: ModpackAI RAG System
   프로젝트 ID: modpack-ai-rag-2024 (자동 생성되는 고유 ID 사용)
   ```
4. **결제 계정 선택**: 기존 결제 계정이 있다면 선택
5. **"만들기"** 클릭하고 1-2분 대기

**🔄 옵션 2: 기존 프로젝트 사용**
1. **상단 프로젝트 선택 드롭다운** 클릭
2. **기존 프로젝트** 목록에서 사용할 프로젝트 선택
3. ⚠️ **주의사항**: 
   - 기존 Firestore 데이터베이스가 있다면 **데이터 충돌** 가능성 있음
   - **새 컬렉션**을 사용하므로 기존 데이터에는 영향 없음
   - **API 사용량**이 기존 프로젝트와 **합산**됨

#### 3.3 필수 API 활성화
1. **왼쪽 메뉴** → **"API 및 서비스"** → **"라이브러리"** 클릭
2. 다음 3개 API를 하나씩 검색하고 활성화:

   **📊 Firestore API 활성화**
   - 검색창에 **"Cloud Firestore API"** 입력
   - **"Cloud Firestore API"** 클릭 → **"사용"** 버튼 클릭
   
   **🤖 Vertex AI API 활성화**  
   - 검색창에 **"Vertex AI API"** 입력
   - **"Vertex AI API"** 클릭 → **"사용"** 버튼 클릭
   
   **📝 Cloud Translation API 활성화** (선택사항)
   - 검색창에 **"Cloud Translation API"** 입력
   - **"Cloud Translation API"** 클릭 → **"사용"** 버튼 클릭

#### 3.4 Firestore 데이터베이스 생성
1. **왼쪽 메뉴** → **"Firestore"** → **"데이터베이스 만들기"** 클릭
2. **모드 선택**: **"Native 모드"** 선택 (권장)
3. **위치 선택**: **"us-central1 (아이오와)"** 선택 (한국에서 가장 가까운 리전)
4. **"완료"** 클릭하고 2-3분 대기

#### 3.5 서비스 계정 생성 및 키 다운로드 ⭐
1. **왼쪽 메뉴** → **"IAM 및 관리"** → **"서비스 계정"** 클릭
2. **"서비스 계정 만들기"** 클릭
3. 서비스 계정 정보 입력:
   ```
   서비스 계정 이름: modpack-ai-rag
   서비스 계정 ID: modpack-ai-rag (자동 생성)
   설명: ModpackAI RAG System Service Account
   ```
4. **"만들고 계속하기"** 클릭

5. **권한 부여** (중요!):
   - **"역할 선택"** 드롭다운 클릭
   - **"Cloud Datastore 사용자"** 검색하고 선택
   - **"다른 역할 추가"** 클릭
   - **"Vertex AI 사용자"** 검색하고 선택
   - **"계속"** 클릭

6. **"완료"** 클릭

7. **키 파일 다운로드**:
   - 생성된 서비스 계정을 **클릭**
   - **"키"** 탭 클릭
   - **"키 추가"** → **"새 키 만들기"** 클릭
   - **"JSON"** 선택 → **"만들기"** 클릭
   - 💾 **키 파일 자동 다운로드됨** (예: `modpack-ai-rag-1234567890.json`)

#### 3.6 다운로드한 키 파일 이동
```bash
# 다운로드 폴더에서 프로젝트 폴더로 이동 (Windows 예시)
move C:\Users\%USERNAME%\Downloads\modpack-ai-rag-*.json C:\Users\Administrator\minecraft-modpack-ai\backend\gcp-key.json

# Linux/Mac 예시
mv ~/Downloads/modpack-ai-rag-*.json ~/minecraft-modpack-ai/backend/gcp-key.json
```

### 4. 환경변수 설정

#### 4.1 프로젝트 ID 확인
- **GCP 콘솔 상단**에서 프로젝트 이름 옆에 표시되는 **프로젝트 ID** 복사
- 예: `modpack-ai-rag-2024-123456`

#### 4.2 .env 파일 수정
```bash
# .env 파일 편집
nano .env
```

```env
# === GCP RAG 설정 ===
GCP_RAG_ENABLED=true
GCP_PROJECT_ID=modpack-ai-rag-2024-123456
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Administrator\minecraft-modpack-ai\backend\gcp-key.json

# === 기존 설정 ===
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_WEBSEARCH_ENABLED=true
```

#### 4.3 설정 확인
```bash
# 백엔드 시작해서 GCP RAG 상태 확인
python app.py

# 다른 터미널에서 상태 확인
curl -X GET http://localhost:5000/gcp-rag/status
```

#### ✅ 성공 시 출력 예시:
```json
{
  "success": true,
  "gcp_rag_enabled": true,
  "gcp_rag_available": true,
  "project_id": "modpack-ai-rag-2024-123456",
  "location": "us-central1",
  "local_rag_enabled": true
}
```

### 🚨 자주 발생하는 문제 해결

#### ❌ 문제 1: "GCP RAG 시스템 비활성화"
```bash
# 해결책: API 활성화 확인
# GCP 콘솔 → API 및 서비스 → 사용 설정된 API에서 확인
# - Cloud Firestore API ✅
# - Vertex AI API ✅
```

#### ❌ 문제 2: "인증 실패"  
```bash
# 해결책: 키 파일 경로 확인
ls -la /path/to/gcp-key.json  # 파일 존재하는지 확인
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS  # 환경변수 확인
```

#### ❌ 문제 3: "권한 부족"
```bash
# 해결책: 서비스 계정 권한 재확인
# GCP 콘솔 → IAM 및 관리 → IAM
# 서비스 계정에 다음 권한이 있는지 확인:
# - Cloud Datastore 사용자
# - Vertex AI 사용자  
```

### 💡 추가 팁

#### 💸 **비용 관리 (기존 사용자 특히 중요!)**
- **Always Free 한도**: 
  - Firestore: 매일 20,000회 읽기/쓰기 **영구 무료**
  - Vertex AI: 월간 임베딩 API 호출 일정량 **무료**
- **무료 한도 초과 시**: 매우 저렴한 단가 (Firestore 읽기: $0.0006/1000회)
- **비용 알림 설정**: GCP 콘솔 → 결제 → 예산 및 알림에서 **$5 알림** 설정 권장
- **실제 예상 비용**: 
  - 모드팩 1개 인덱싱: **~$0.50-1.00** (1회성)
  - 월간 검색 1000회: **~$0.10-0.30**

#### 🔄 **기존 계정 활용 시 장점**
- **결제 정보 재입력 불필요**
- **기존 프로젝트와 분리 관리 가능**
- **통합 결제서**로 한 번에 관리
- **무료 크레딧 소진되어도 Always Free 제품은 계속 무료**

#### 🔒 **보안 관리**
- **키 파일**: 절대 Git에 커밋하지 마세요!
- **서비스 계정**: 최소 권한 원칙 (Datastore + Vertex AI만)
- **키 로테이션**: 3-6개월마다 새 키 생성 권장

#### 🌍 **성능 최적화**
- **리전**: `us-central1` 추천 (한국에서 가장 빠름)
- **데이터 지역성**: Firestore와 Vertex AI 동일 리전 사용
- **캐싱**: 자주 검색하는 쿼리는 로컬 캐시 활용

#### 📊 **모니터링**
- **실시간 사용량**: GCP 콘솔에서 API 호출량 확인
- **비용 대시보드**: 월간/일간 비용 트렌드 모니터링
- **할당량 관리**: API 호출 한도 설정으로 비용 제어

## 🎮 사용법

### 1. 시스템 상태 확인
```bash
# 백엔드 시작
python app.py

# 상태 확인
curl -X GET http://localhost:5000/gcp-rag/status
```

### 2. 모드팩 인덱스 구축
```bash
# POST /gcp-rag/build
curl -X POST http://localhost:5000/gcp-rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "modpack_name": "enigmatica_6",
    "modpack_version": "1.0.0",
    "modpack_path": "/home/user/enigmatica_6"
  }'
```

#### 응답 예시
```json
{
  "success": true,
  "modpack_name": "enigmatica_6",
  "modpack_version": "1.0.0",
  "collection_name": "modpack_enigmatica_6_1_0_0",
  "document_count": 1250,
  "stats": {
    "recipes": 450,
    "mods": 150,
    "kubejs": 650
  }
}
```

### 3. 검색 결과 확인 (개발자용)
```bash
# POST /gcp-rag/search - 실제 검색 결과를 눈으로 확인
curl -X POST http://localhost:5000/gcp-rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iron block recipe",
    "modpack_name": "enigmatica_6",
    "modpack_version": "1.0.0",
    "top_k": 5,
    "min_score": 0.7
  }'
```

#### 응답 예시 - 검색된 정보가 실제로 유용한지 확인 가능!
```json
{
  "success": true,
  "query": "iron block recipe",
  "modpack": "enigmatica_6 v1.0.0",
  "results_count": 3,
  "results": [
    {
      "doc_id": "abc123",
      "text": "Shaped recipe for iron_block x1: keys={'I': 'iron_ingot'}",
      "doc_type": "recipe",
      "doc_source": "/data/minecraft/recipes/iron_block.json",
      "similarity": 0.89,
      "text_length": 58
    },
    {
      "doc_id": "def456", 
      "text": "kubejs script: startup_scripts/iron_variants.js => // 철 관련 아이템들의 대체 레시피 추가...",
      "doc_type": "kubejs",
      "doc_source": "/kubejs/startup_scripts/iron_variants.js",
      "similarity": 0.76,
      "text_length": 245
    }
  ],
  "search_params": {
    "top_k": 5,
    "min_score": 0.7
  }
}
```

### 4. 통합 채팅 테스트
```bash
# POST /chat - RAG가 적용된 실제 채팅
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "철 블록을 어떻게 만들어?",
    "player_uuid": "test-player",
    "modpack_name": "enigmatica_6",
    "modpack_version": "1.0.0"
  }'
```

#### 응답 예시 - 디버그 정보 포함
```json
{
  "success": true,
  "response": "철 블록을 만들려면 철 주괴 9개를 3x3 제작대에 배치하세요...",
  "model": "gemini",
  "rag": {
    "enabled": true,
    "gcp_enabled": true,
    "hits": 3,
    "used": true,
    "used_chars": 384,
    "debug_info": {
      "gcp_rag": {
        "used": true,
        "results_count": 3,
        "results": [
          {
            "similarity": 0.89,
            "doc_type": "recipe",
            "text": "Shaped recipe for iron_block..."
          }
        ]
      }
    }
  }
}
```

### 5. 등록된 모드팩 확인
```bash
# GET /gcp-rag/modpacks
curl -X GET http://localhost:5000/gcp-rag/modpacks
```

### 6. 자동화 테스트 스크립트 사용
```bash
# 대화형 테스트 도구
python test_gcp_rag.py
```

## 🔧 고급 설정

### 토큰 사용량 최적화
```env
# .env 파일에서 조정 가능
RAG_TOP_K=5                    # 검색할 문서 수 (기본: 5)
RAG_SNIPPET_MAX_CHARS=500      # 문서당 최대 문자수 (기본: 500)
RAG_TOTAL_MAX_CHARS=1500       # 전체 RAG 텍스트 최대 문자수 (기본: 1500)
```

### 검색 품질 조정
```python
# 검색 API 호출 시 파라미터 조정
{
  "top_k": 10,        # 더 많은 결과 (최대 20)
  "min_score": 0.6    # 더 낮은 임계값 (더 많은 결과)
}
```

### 텍스트 청킹 조정
```python
# gcp_rag_system.py에서 수정 가능
def _chunk_text(self, text: str, max_chars: int = 1000):
    # 청크 크기 조정 (기본: 1000자)
```

## 🚨 문제 해결

### 1. GCP RAG 시스템 비활성화
```bash
# 상태 확인
curl -X GET http://localhost:5000/gcp-rag/status

# 일반적인 문제들
# - GCP_PROJECT_ID 미설정
# - 서비스 계정 키 파일 경로 오류  
# - API 권한 부족
```

### 2. 임베딩 생성 실패
```bash
# Vertex AI API 활성화 확인
gcloud services list --enabled --filter="name:aiplatform.googleapis.com"

# 권한 확인
gcloud auth application-default print-access-token
```

### 3. Firestore 연결 실패
```bash
# Firestore API 활성화 확인
gcloud services list --enabled --filter="name:firestore.googleapis.com"

# 데이터베이스 생성 (필요 시)
gcloud firestore databases create --region=us-central1
```

### 4. 검색 결과 없음
```python
# 검색 임계값 낮추기
{
  "min_score": 0.5  # 기본 0.7에서 낮춤
}

# 또는 로그 확인
tail -f logs/gcp_rag.log
```

## 🔄 롤백 및 제거

### 1. GCP RAG 비활성화 (데이터 보존)
```bash
# .env 파일에서 비활성화
GCP_RAG_ENABLED=false

# 백엔드 재시작 후 로컬 RAG로 자동 폴백
```

### 2. 완전 제거
```bash
# 롤백 스크립트 실행
./uninstall_gcp_rag.sh

# 또는 수동 제거
rm -f gcp_rag_system.py
rm -f requirements-gcp-rag.txt
pip uninstall -y google-cloud-firestore google-cloud-aiplatform vertexai
```

### 3. GCP 리소스 정리
```bash
# Firestore 컬렉션 삭제 (필요 시)
# 주의: 데이터가 영구적으로 삭제됩니다
gcloud firestore delete --all-collections

# 프로젝트 완전 삭제 (필요 시)  
gcloud projects delete your-modpack-ai-project
```

## 📊 성능 모니터링

### 비용 추적
```bash
# GCP 콘솔에서 확인:
# - Firestore 읽기/쓰기 작업 수
# - Vertex AI 임베딩 API 호출 수
# - 스토리지 사용량
```

### 응답 시간 최적화
- **로컬 RAG**: ~100-500ms
- **GCP RAG**: ~1-3초 (첫 검색 후 캐시됨)
- **Gemini 웹검색**: ~2-5초

### 권장 사항
- 모드팩당 **10,000개 이하 문서** 권장
- 청크 크기 **800-1200자** 권장  
- 검색 **top_k=5-10** 권장
- 임계값 **min_score=0.6-0.8** 권장

## 🎯 베스트 프랙티스

### 1. 개발 단계
```bash
# 1단계: 로컬에서 기본 RAG 테스트
GCP_RAG_ENABLED=false

# 2단계: GCP RAG로 업그레이드
./install_gcp_rag.sh

# 3단계: 소규모 모드팩으로 테스트
python test_gcp_rag.py
```

### 2. 프로덕션 배포
```bash
# 환경 분리
# - 개발: 로컬 SQLite + 로컬 RAG
# - 스테이징: GCP + 테스트 데이터
# - 프로덕션: GCP + 전체 모드팩
```

### 3. 모니터링
```python
# 응답에 포함된 디버그 정보 활용
{
  "rag": {
    "debug_info": {
      "gcp_rag": {
        "used": true,
        "results_count": 5,
        "results": [...]  # 실제 검색 결과 확인
      }
    }
  }
}
```

## 🤝 기여하기

개선사항이나 버그 리포트는 GitHub Issues에서 환영합니다!

- **검색 품질 개선** 아이디어
- **새로운 문서 타입** 지원
- **성능 최적화** 제안
- **사용자 경험** 개선

---

**⭐ 이 가이드가 도움이 되었다면 스타를 눌러주세요!**