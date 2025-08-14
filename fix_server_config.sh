#!/bin/bash

# 🔧 서버측 config_manager.py 경로 문제 해결 스크립트

echo "🔍 현재 상황 점검..."

# 1. Python 캐시 제거
echo "1️⃣ Python 캐시 제거"
find ~/minecraft-modpack-ai -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find ~/minecraft-ai-backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find ~/minecraft-modpack-ai -name "*.pyc" -delete 2>/dev/null || true
find ~/minecraft-ai-backend -name "*.pyc" -delete 2>/dev/null || true

# 2. 현재 config_manager.py 파일 위치 확인
echo "2️⃣ config_manager.py 파일 검색"
echo "프로젝트 파일: $(ls ~/minecraft-modpack-ai/backend/config_manager.py 2>/dev/null && echo "✅ 존재" || echo "❌ 없음")"
echo "백엔드 파일: $(ls ~/minecraft-ai-backend/config_manager.py 2>/dev/null && echo "✅ 존재" || echo "❌ 없음")"

# 3. 잘못된 config_manager.py 제거 (minecraft-ai-backend 디렉토리에서)
if [ -f ~/minecraft-ai-backend/config_manager.py ]; then
    echo "3️⃣ 잘못된 위치의 config_manager.py 제거"
    rm ~/minecraft-ai-backend/config_manager.py
    echo "✅ ~/minecraft-ai-backend/config_manager.py 제거됨"
fi

# 4. 올바른 config_manager.py 경로 확인
echo "4️⃣ 현재 작업 디렉토리에서 실행 권장"
echo "cd ~/minecraft-modpack-ai/backend"
echo "python config_manager.py status"

# 5. 환경 파일 설정 확인
echo "5️⃣ 환경 파일 위치 확인"
echo "현재 .env 파일 위치:"
find ~ -name ".env" -path "*/minecraft*" 2>/dev/null

echo ""
echo "🎯 해결책:"
echo "1. cd ~/minecraft-modpack-ai/backend"
echo "2. python config_manager.py status"
echo "3. 만약 여전히 문제가 있다면 config_manager.py 내용을 다시 확인"
