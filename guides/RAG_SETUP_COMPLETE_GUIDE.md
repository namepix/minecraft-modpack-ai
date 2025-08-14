# 🚀 RAG 시스템 완전 설치 가이드 (GCP RAG 전용)

## 📋 개요

이 가이드는 GCP VM Debian 환경에서 ModpackAI의 RAG(Retrieval-Augmented Generation) 시스템을 완전히 설치하고 설정하는 방법을 단계별로 설명합니다.

**⚠️ 중요**: 모든 명령어는 **정확한 디렉토리**에서 실행해야 합니다. 각 단계마다 현재 위치를 명시했습니다.

## 🎯 아키텍처 개요

```
┌─ minecraft-modpack-ai/     ← 소스 코드 저장소 (GitHub에서 clone)
│  └─ backend/              ← 개발 및 수정용 파일들
│     ├─ app.py
│     ├─ config_manager.py
│     ├─ gcp_rag_system.py
│     └─ ... (기타 파일들)
│
└─ minecraft-ai-backend/     ← 실제 실행 환경
   ├─ .env                  ← 환경변수 설정 파일
   ├─ app.py               ← 실행용 Flask 앱
   ├─ venv/                ← Python 가상환경
   └─ ... (복사된 실행 파일들)
```

---

## 📁 1단계: 프로젝트 다운로드 및 기본 설정

### 1.1 홈 디렉토리에서 시작

```bash
# 홈 디렉토리로 이동
cd ~

# 현재 위치 확인 (반드시 /home/사용자명 이어야 함)
pwd
```

### 1.2 프로젝트 클론

```bash
# GitHub에서 프로젝트 다운로드
git clone https://github.com/namepix/minecraft-modpack-ai.git

# 다운로드 확인
ls -la minecraft-modpack-ai/
```

### 1.3 install_mod.sh 실행

```bash
# 프로젝트 루트 디렉토리로 이동
cd ~/minecraft-modpack-ai

# 현재 위치 확인 (/home/사용자명/minecraft-modpack-ai)
pwd

# 설치 스크립트 실행 권한 부여
chmod +x install_mod.sh

# 설치 스크립트 실행
./install_mod.sh
```

**결과**: 
- `~/minecraft-ai-backend/` 디렉토리 생성
- Python 가상환경 설치
- 기본 의존성 설치
- Flask 서비스 등록

---

## ⚙️ 2단계: 환경변수 설정

### 2.1 환경변수 파일 편집

```bash
# minecraft-ai-backend 디렉토리의 .env 파일 편집
nano ~/minecraft-ai-backend/.env
```

### 2.2 .env 파일 내용 (완전한 예시)

```bash
# ==========================================
# API Keys (필수 - 실제 키로 교체하세요)
# ==========================================

# Google Gemini API Key (권장 - 웹검색 지원)
GOOGLE_API_KEY=your-actual-google-api-key-here

# OpenAI API Key (백업용, 선택사항)
OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic Claude API Key (백업용, 선택사항)  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# ==========================================
# GCP RAG 시스템 설정 (필수)
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
# 서버 설정
# ==========================================

# Flask 서버 포트
PORT=5000

# 디버그 모드 (프로덕션에서는 false)
DEBUG=false

# Flask 환경
FLASK_ENV=production

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
DEFAULT_AI_MODEL=gemini-2.5-pro
```

### 2.3 파일 저장

```bash
# nano 에디터에서:
# 1. Ctrl + X (나가기)
# 2. Y (저장)
# 3. Enter (파일명 확인)
```

---

## 🔐 3단계: GCP 인증 및 권한 설정

### 3.1 현재 GCP 계정 확인

```bash
# VM의 서비스 계정 확인
curl -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email

# 현재 권한 범위 확인  
curl -H "Metadata-Flavor: Google" \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/scopes
```

**예상 결과**: 
- 서비스 계정: `숫자-compute@developer.gserviceaccount.com`
- 권한 범위: `https://www.googleapis.com/auth/cloud-platform` 포함되어야 함

### 3.2 VM 권한 범위 확장 (필요시)

**만약 `cloud-platform` 권한이 없다면**:

1. **GCP 콘솔**에서 VM 중지
2. **VM 인스턴스** → **편집**
3. **액세스 범위** → **모든 Cloud API에 대한 전체 액세스 허용** 선택
4. **저장** → **VM 시작**

### 3.3 GCP IAM 권한 부여

**GCP 콘솔에서**:
1. **IAM 및 관리** → **IAM**
2. **프로젝트 선택**: `your-gcp-project-id`
3. **보안 주체 추가**
4. **새 보안 주체**: VM의 서비스 계정 (위에서 확인한 이메일)
5. **역할 추가**:
   - `Vertex AI 사용자` (roles/aiplatform.user)
   - `Cloud Datastore 사용자` (roles/datastore.user)
   - `저장소 객체 뷰어` (roles/storage.objectViewer)
   - `Editor` (권장 - 모든 권한)

### 3.4 API 활성화

```bash
# 권한 설정 후 VM에서 실행
gcloud services enable aiplatform.googleapis.com --project=your-gcp-project-id
gcloud services enable firestore.googleapis.com --project=your-gcp-project-id

# 활성화 확인
gcloud services list --enabled --project=your-gcp-project-id | grep -E "(aiplatform|firestore)"
```

**성공 예시**:
```
aiplatform.googleapis.com           Vertex AI API
firestore.googleapis.com            Cloud Firestore API
```

---

## 🔄 4단계: 파일 동기화 시스템 설정

### 4.1 동기화의 중요성

**⚠️ 중요**: 
- **minecraft-modpack-ai/backend/**: 소스 코드 (수정용)
- **minecraft-ai-backend/**: 실행 환경 (실행용)
- 수정 후 반드시 동기화 필요!

### 4.2 자동 동기화 스크립트 생성

```bash
# 홈 디렉토리에서 동기화 스크립트 생성
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
```

### 4.3 첫 동기화 실행

```bash
# 홈 디렉토리에서 실행
cd ~
./sync_backend.sh
```

---

## 🎯 5단계: RAG 설정 도구 사용

### 5.1 config_manager.py 사용법

```bash
# minecraft-ai-backend 디렉토리로 이동
cd ~/minecraft-ai-backend

# Python 가상환경 활성화
source venv/bin/activate

# 현재 RAG 설정 상태 확인
python3 config_manager.py status
```

**성공 예시 출력**:
```
📋 RAG 시스템 설정 상태
==================================================
🔧 RAG 모드: auto
📦 현재 모드팩: Prominence_II_RPG_Hasturian_Era v3.1.51hf
🌐 GCP RAG: ✅ 활성화
✅ GCP 프로젝트 ID: your-gcp-project-id
⚙️  환경 파일: /home/사용자명/minecraft-ai-backend/.env
📄 설정 파일: /home/사용자명/minecraft-ai-backend/rag_config.json
```

### 5.2 GCP 프로젝트 ID 설정

```bash
# GCP 프로젝트 ID 설정 (실제 프로젝트 ID로 교체)
python3 config_manager.py set-gcp-project "your-actual-gcp-project-id"
```

### 5.3 수동 모드팩 설정 (선택사항)

```bash
# 특정 모드팩으로 수동 설정
python3 config_manager.py set-manual "Prominence_II_RPG_Hasturian_Era" "3.1.51hf"

# 자동 모드로 전환
python3 config_manager.py set-auto
```

---

## 🚀 6단계: Flask 서버 실행 및 테스트

### 6.1 서버 실행 준비

```bash
# minecraft-ai-backend 디렉토리에 있는지 확인
cd ~/minecraft-ai-backend
pwd  # /home/사용자명/minecraft-ai-backend 여야 함

# 가상환경 활성화
source venv/bin/activate

# 환경변수 로드
export GOOGLE_CLOUD_PROJECT=your-gcp-project-id
export GCP_PROJECT_ID=your-gcp-project-id
export GCP_RAG_ENABLED=true
```

### 6.2 Flask 서버 실행

```bash
# Flask 앱 실행
python3 app.py
```

**성공 시 출력 예시**:
```
GCP_PROJECT_ID: your-gcp-project-id
GCP_RAG_ENABLED: true
✅ GCP RAG 시스템 초기화 완료 - Project: your-gcp-project-id
✅ Gemini 2.5 Pro 클라이언트 초기화 완료 (웹검색 지원, google-genai SDK)
🚀 마인크래프트 AI 백엔드 시작 중...
📊 현재 활성 모델: gemini
🔑 Google API (Gemini): ✅
🔑 OpenAI API: ❌
🔑 Anthropic API (Claude): ❌
🔗 GCP RAG: ✅
🎯 주 사용 모델: gemini
🌐 Gemini 웹검색 기능 활성화됨
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.xxx.x.x:5000
```

---

## 🧪 7단계: RAG 시스템 테스트

### 7.1 새 터미널에서 기본 상태 확인

```bash
# 새 터미널 열기

# GCP RAG 상태 확인
curl -s http://localhost:5000/gcp-rag/status | python3 -m json.tool

# 서버 건강 상태 확인
curl -s http://localhost:5000/health | python3 -m json.tool
```

**GCP RAG 성공 예시**:
```json
{
  "success": true,
  "gcp_rag_enabled": true,
  "gcp_rag_available": true,
  "project_id": "your-gcp-project-id",
  "location": "us-central1",
  "local_rag_enabled": false
}
```

### 7.2 Firestore 데이터베이스 생성

```bash
# Firestore 데이터베이스 생성 (최초 1회만)
gcloud firestore databases create --region=us-central1 --project=your-gcp-project-id --type=firestore-native
```

### 7.3 RAG 인덱스 구축 테스트

```bash
# 테스트용 모드팩 인덱스 생성
curl -X POST http://localhost:5000/gcp-rag/build \
  -H "Content-Type: application/json" \
  -d '{
    "modpack_name": "test_modpack",
    "modpack_version": "1.0.0",
    "modpack_path": "/tmp"
  }'
```

**성공 예시**:
```json
{
  "success": true,
  "modpack_name": "test_modpack",
  "modpack_version": "1.0.0",
  "collection_name": "modpack_test_modpack_1_0_0",
  "document_count": 0,
  "stats": {}
}
```

### 7.4 RAG 검색 테스트

```bash
# RAG 검색 테스트
curl -X POST http://localhost:5000/gcp-rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iron ingot recipe",
    "modpack_name": "test_modpack",
    "modpack_version": "1.0.0",
    "top_k": 5,
    "min_score": 0.7
  }'
```

### 7.5 채팅 API 테스트

```bash
# 실제 채팅 테스트 (RAG 포함)
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "철 주괴로 뭘 만들 수 있어?",
    "player_uuid": "test-player"
  }'
```

---

## 🛠️ 8단계: 실제 모드팩 RAG 구축

### 8.1 rag_manager.py 사용

```bash
# minecraft-ai-backend 디렉토리에서
cd ~/minecraft-ai-backend
source venv/bin/activate

# 실제 모드팩 RAG 인덱스 구축
python3 rag_manager.py build "Prominence_II_RPG_Hasturian_Era" "3.1.51hf" "/path/to/your/modpack"

# 등록된 모드팩 목록 확인
python3 rag_manager.py list
```

### 8.2 모드팩 경로 찾기

```bash
# 일반적인 모드팩 경로들
ls -la /opt/minecraft/
ls -la ~/minecraft/
ls -la /srv/minecraft/

# 모드팩 구조 예시
# /path/to/modpack/
# ├── mods/           ← .jar 파일들
# ├── config/         ← 설정 파일들  
# ├── kubejs/         ← KubeJS 스크립트
# ├── data/           ← 데이터팩
# └── defaultconfigs/ ← 기본 설정
```

---

## 🔧 9단계: 문제 해결 가이드

### 9.1 일반적인 문제들

#### 문제: `GCP_PROJECT_ID 환경변수 없음`
```bash
# 해결책 1: 환경변수 수동 설정
export GCP_PROJECT_ID=your-gcp-project-id
export GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# 해결책 2: .env 파일 재확인
cat ~/minecraft-ai-backend/.env | grep GCP_PROJECT_ID
```

#### 문제: `403 PERMISSION_DENIED`
```bash
# GCP 권한 확인
gcloud projects get-iam-policy your-gcp-project-id \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:YOUR-SERVICE-ACCOUNT@developer.gserviceaccount.com"
```

#### 문제: `config_manager.py 파일 없음`
```bash
# 동기화 스크립트 재실행
cd ~
./sync_backend.sh

# 파일 존재 확인
ls -la ~/minecraft-ai-backend/config_manager.py
```

### 9.2 로그 확인

```bash
# Flask 앱 에러 로그 확인
cd ~/minecraft-ai-backend
python3 app.py 2>&1 | tee app.log

# 시스템 로그 확인
journalctl -u mc-ai-backend -f
```

### 9.3 완전 초기화 (필요시)

```bash
# 모든 것을 삭제하고 다시 시작
rm -rf ~/minecraft-modpack-ai
rm -rf ~/minecraft-ai-backend
rm -f ~/sync_backend.sh

# 이 가이드의 1단계부터 다시 시작
```

---

## ✅ 10단계: 성공 확인 체크리스트

### 10.1 필수 확인 사항

- [ ] **GCP API 활성화**: Vertex AI, Firestore API 활성화됨
- [ ] **권한 설정**: VM 서비스 계정에 필요한 IAM 역할 부여됨
- [ ] **환경변수**: GCP_PROJECT_ID, API 키들이 올바르게 설정됨
- [ ] **파일 동기화**: 모든 Python 파일이 최신 버전으로 동기화됨
- [ ] **Flask 서버**: 에러 없이 정상 실행됨

### 10.2 기능 테스트

- [ ] **GCP RAG 상태**: `gcp_rag_available: true` 반환
- [ ] **Firestore 연결**: 데이터베이스 생성 및 접근 가능
- [ ] **Vertex AI**: 임베딩 모델 로드 성공
- [ ] **RAG 검색**: 검색 API 정상 작동
- [ ] **채팅 API**: 전체 통합 테스트 통과

---

## 🎯 일상 사용 워크플로우

### 개발/수정 시

```bash
# 1. 소스 코드 수정
nano ~/minecraft-modpack-ai/backend/app.py

# 2. 동기화
cd ~
./sync_backend.sh

# 3. 서버 재시작
cd ~/minecraft-ai-backend
source venv/bin/activate
python3 app.py
```

### 새 모드팩 추가 시

```bash
# 1. 모드팩 RAG 인덱스 구축
cd ~/minecraft-ai-backend
source venv/bin/activate
python3 rag_manager.py build "모드팩이름" "버전" "/모드팩/경로"

# 2. config_manager로 활성 모드팩 설정
python3 config_manager.py set-manual "모드팩이름" "버전"
```

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **현재 디렉토리**: 각 명령어를 올바른 디렉토리에서 실행했는지
2. **파일 동기화**: `sync_backend.sh` 실행 후 최신 파일인지
3. **환경변수**: `.env` 파일의 내용과 실제 로드된 환경변수 일치하는지
4. **GCP 설정**: API 활성화 및 권한 설정이 완료되었는지
5. **로그 확인**: Flask 앱 실행 시 나오는 에러 메시지 확인

**이 가이드를 순서대로 따라하면 RAG 시스템이 완전히 작동할 것입니다!** 🚀