#!/bin/bash

echo "🔍 환경 파일 경로 문제 진단 스크립트"
echo "=================================="

# 1. 현재 config_manager.py의 경로 로직 확인
echo "1️⃣ config_manager.py 내용 확인"
echo "경로 설정 부분:"
grep -n "env_file\|\.env\|Path" ~/minecraft-modpack-ai/backend/config_manager.py

echo ""
echo "2️⃣ 환경 파일 위치 확인"
echo "minecraft-ai-backend/.env 파일:"
ls -la ~/minecraft-ai-backend/.env 2>/dev/null && echo "✅ 존재" || echo "❌ 없음"

echo "minecraft-modpack-ai/.env 파일:"
ls -la ~/minecraft-modpack-ai/.env 2>/dev/null && echo "✅ 존재" || echo "❌ 없음"

echo ""
echo "3️⃣ 환경 파일 내용 비교"
echo "minecraft-ai-backend/.env의 GCP_PROJECT_ID:"
grep "GCP_PROJECT_ID" ~/minecraft-ai-backend/.env 2>/dev/null || echo "없음"

echo "minecraft-modpack-ai/.env의 GCP_PROJECT_ID (만약 있다면):"
grep "GCP_PROJECT_ID" ~/minecraft-modpack-ai/.env 2>/dev/null || echo "없음"

echo ""
echo "4️⃣ Python에서 실제 로드되는 경로 확인"
cd ~/minecraft-modpack-ai/backend
python3 -c "
import os
from pathlib import Path
from dotenv import load_dotenv

# 현재 config_manager.py와 동일한 로직
project_root = Path(__file__).parent.parent if '__file__' in globals() else Path.cwd().parent
env_file = project_root / '.env'

print(f'계산된 .env 파일 경로: {env_file}')
print(f'파일 존재 여부: {env_file.exists()}')

if env_file.exists():
    load_dotenv(env_file)
    print(f'로드된 GCP_PROJECT_ID: {os.getenv(\"GCP_PROJECT_ID\", \"없음\")}')
else:
    print('환경 파일이 존재하지 않음')
"

echo ""
echo "5️⃣ 해결책 제안"
echo "문제: 환경 파일이 잘못된 위치에서 읽혀지고 있음"
echo "해결책 1: 올바른 .env 파일을 올바른 위치로 복사"
echo "해결책 2: config_manager.py를 수정해서 올바른 경로 지정"