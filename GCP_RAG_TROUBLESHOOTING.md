# 🔧 GCP RAG 시스템 문제 해결 가이드

## 🚨 현재 발생한 문제

### 증상
```
403 Caller does not have required permission to use project direct-outlook-463412-s3
Grant the caller the roles/serviceusage.serviceUsageConsumer role
```

### 원인
GCP VM의 서비스 계정에 필요한 IAM 역할이 부족

## ✅ 해결 방법

### 방법 1: GCP 콘솔에서 직접 설정 (권장)

1. **GCP 콘솔 접속**: https://console.cloud.google.com/
2. **프로젝트 선택**: `direct-outlook-463412-s3`
3. **IAM 메뉴**: 탐색 메뉴 → IAM 및 관리자 → IAM
4. **서비스 계정 찾기**: `110094869036-compute@developer.gserviceaccount.com`
5. **편집 버튼 클릭** → **역할 추가**
6. **다음 역할들 추가**:
   - ✅ `Service Usage Consumer` (필수)
   - ✅ `Vertex AI User` (권장)
   - ✅ `Cloud Firestore User` (권장)

### 방법 2: gcloud 명령어 사용 (로컬에서)

```bash
# 현재 인증 상태 확인
gcloud auth list

# 권한 추가 (필수)
gcloud projects add-iam-policy-binding direct-outlook-463412-s3 \
    --member="serviceAccount:110094869036-compute@developer.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageConsumer"

# 추가 권한 (권장)
gcloud projects add-iam-policy-binding direct-outlook-463412-s3 \
    --member="serviceAccount:110094869036-compute@developer.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding direct-outlook-463412-s3 \
    --member="serviceAccount:110094869036-compute@developer.gserviceaccount.com" \
    --role="roles/datastore.user"
```

## 🧪 설정 완료 후 테스트

권한 설정이 완료되면 (보통 1-5분 후) 다음 명령어로 테스트:

```bash
cd /home/namepix080/minecraft-ai-backend
source venv/bin/activate
python3 -c "from gcp_rag_system import GCPRAGSystem; rag = GCPRAGSystem(); print(f'RAG System enabled: {rag.enabled}')"
```

**성공 시 출력**: `RAG System enabled: True`

## 📋 현재 시스템 상태

✅ **완료된 부분**:
- VM에 cloud-platform 스코프 활성화됨
- 백엔드 서비스 정상 실행 중
- Gemini API 활성화됨
- 모드 빌드 완료 (NeoForge/Fabric)

⚠️ **대기 중인 부분**:
- GCP 서비스 계정 IAM 역할 설정

## 🔄 다음 단계

1. **사용자가 GCP 콘솔에서 권한 설정**
2. **RAG 시스템 테스트 실행**
3. **모드팩 인덱스 구축**
4. **최종 검증 완료**

## 📚 추가 정보

- **GCP IAM 문서**: https://cloud.google.com/iam/docs/
- **Vertex AI 권한**: https://cloud.google.com/vertex-ai/docs/general/access-control
- **서비스 계정 관리**: https://cloud.google.com/iam/docs/service-accounts