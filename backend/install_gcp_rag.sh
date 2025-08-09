#!/bin/bash
# GCP RAG 시스템 설치 스크립트

echo "🚀 GCP RAG 시스템 설치 중..."

# 1. 필요한 패키지 설치
echo "📦 GCP 라이브러리 설치 중..."
pip install -r requirements-gcp-rag.txt

# 2. 환경변수 파일에 GCP 설정 추가
if [ ! -f .env ]; then
    echo "📝 .env 파일 생성..."
    touch .env
fi

# GCP RAG 활성화
if ! grep -q "GCP_RAG_ENABLED" .env; then
    echo "" >> .env
    echo "# === GCP RAG 설정 ===" >> .env
    echo "GCP_RAG_ENABLED=true" >> .env
    echo "GCP_PROJECT_ID=your-gcp-project-id" >> .env
fi

echo "✅ GCP RAG 시스템 설치 완료!"
echo ""
echo "🔧 추가 설정 필요:"
echo "1. .env 파일에서 GCP_PROJECT_ID를 실제 프로젝트 ID로 변경"
echo "2. GCP 인증 설정 (서비스 계정 키 파일 또는 gcloud auth)"
echo "3. Firestore와 Vertex AI API 활성화"
echo ""
echo "📚 사용법:"
echo "- POST /gcp-rag/build : 모드팩 인덱스 구축"
echo "- POST /gcp-rag/search : 검색 결과 확인 (개발용)"
echo "- GET /gcp-rag/modpacks : 등록된 모드팩 목록"
echo "- GET /gcp-rag/status : 시스템 상태"
echo ""