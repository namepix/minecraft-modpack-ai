#!/bin/bash
# GCP RAG 시스템 제거 스크립트 (롤백용)

echo "🗑️ GCP RAG 시스템 제거 중..."

# 1. .env 파일에서 GCP RAG 비활성화
if [ -f .env ]; then
    echo "📝 .env 파일에서 GCP RAG 비활성화..."
    if grep -q "GCP_RAG_ENABLED=true" .env; then
        sed -i 's/GCP_RAG_ENABLED=true/GCP_RAG_ENABLED=false/g' .env
    fi
fi

# 2. GCP 라이브러리 제거 (선택사항)
read -p "GCP 라이브러리를 완전히 제거하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 GCP 라이브러리 제거 중..."
    pip uninstall -y google-cloud-firestore google-cloud-aiplatform vertexai
fi

# 3. GCP RAG 관련 파일들 제거 (선택사항)
read -p "GCP RAG 관련 파일들을 제거하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗂️ GCP RAG 파일 제거 중..."
    rm -f gcp_rag_system.py
    rm -f requirements-gcp-rag.txt
    rm -f install_gcp_rag.sh
    echo "⚠️ 이 스크립트 파일도 제거됩니다 (다음 실행 시 삭제됨)"
fi

echo "✅ GCP RAG 시스템 제거 완료!"
echo ""
echo "🔄 이제 다음과 같은 상태입니다:"
echo "- GCP RAG 기능 비활성화됨"
echo "- 기존 로컬 RAG 시스템은 계속 사용 가능"
echo "- Flask 백엔드는 정상적으로 작동"
echo ""
echo "💡 다시 활성화하려면: ./install_gcp_rag.sh 실행"