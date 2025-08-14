#!/bin/bash

echo "🔍 서버측 config_manager.py 실제 내용 검증"
echo "============================================"

echo "1️⃣ 현재 config_manager.py 파일 크기와 수정 시간"
ls -la ~/minecraft-modpack-ai/backend/config_manager.py

echo ""
echo "2️⃣ config_manager.py에서 경로 관련 코드 추출"
echo "환경 파일 경로 설정 부분:"
grep -n -A5 -B5 "runtime_dir\|self.env_file" ~/minecraft-modpack-ai/backend/config_manager.py

echo ""
echo "3️⃣ 실제 __init__ 메서드 전체 내용"
sed -n '/def __init__(self):/,/def [a-zA-Z]/p' ~/minecraft-modpack-ai/backend/config_manager.py | head -n -1

echo ""
echo "4️⃣ Python에서 실제 실행되는 경로 디버깅"
cd ~/minecraft-modpack-ai/backend
python3 -c "
import os
import sys
from pathlib import Path

print('=== 디버깅 정보 ===')
print(f'현재 작업 디렉토리: {os.getcwd()}')
print(f'__file__ 경로 (가상): {Path.cwd() / 'config_manager.py'}')

# config_manager.py와 동일한 로직 재현
runtime_dir = Path.home() / 'minecraft-ai-backend'
env_file = runtime_dir / '.env'
project_root = Path.cwd().parent  # __file__.parent.parent 대신
env_example = project_root / 'env.example'

print(f'계산된 runtime_dir: {runtime_dir}')
print(f'계산된 env_file: {env_file}')
print(f'env_file 존재 여부: {env_file.exists()}')
print(f'계산된 project_root: {project_root}')
print(f'계산된 env_example: {env_example}')
print(f'env_example 존재 여부: {env_example.exists()}')

# 실제 환경변수 로드 테스트
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    print(f'로드된 GCP_PROJECT_ID: {os.getenv(\"GCP_PROJECT_ID\", \"없음\")}')
    print(f'로드된 CURRENT_MODPACK_NAME: {os.getenv(\"CURRENT_MODPACK_NAME\", \"없음\")}')
"

echo ""
echo "5️⃣ 가능한 문제점들"
echo "- config_manager.py가 실제로는 다른 내용일 가능성"
echo "- Python import 캐시 문제"
echo "- 파일 동기화 문제"
echo "- 실행 환경 차이"