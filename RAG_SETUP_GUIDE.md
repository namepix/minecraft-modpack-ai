# 🔧 RAG 시스템 설정 가이드 (최종 통합본)

## 🎯 표준화 완료

**표준 환경 파일 경로**: `~/minecraft-ai-backend/.env`
- ✅ 모든 시스템 컴포넌트가 단일 경로 사용
- ✅ 기존 사용자 설정과 완전 호환
- ✅ 자동 초기화 및 설정 관리

## 📁 표준 환경 파일 설정

### 1. 환경 파일 위치 확인 (표준)
```bash
ls -la ~/minecraft-ai-backend/.env  # 표준 위치
```

### 2. 설정 관리 (자동화됨)
```bash
cd ~/minecraft-modpack-ai/backend

# 자동으로 ~/minecraft-ai-backend/.env 관리됨
python config_manager.py status
```

### 3. .env 파일에 추가할 내용
```env
# === 기존 설정 유지 ===
DEFAULT_AI_MODEL=gemini-2.5-pro
GOOGLE_API_KEY=your-google-api-key-here

# === GCP RAG 설정 (필수) ===
GCP_PROJECT_ID=your-actual-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name
GCP_RAG_ENABLED=true

# === 모드팩 설정 ===
CURRENT_MODPACK_NAME=Prominence_II_RPG_Hasturian_Era
CURRENT_MODPACK_VERSION=3.1.51hf
```

## 🛠️ 수정된 사용법

### A. 수동 모드팩 설정 (권장)
```bash
cd ~/minecraft-modpack-ai/backend

# 1. 수동 모드팩 설정
python config_manager.py set-manual "Prominence_II_RPG_Hasturian_Era" "3.1.51hf"

# 2. GCP 프로젝트 ID 설정
python config_manager.py set-gcp-project "your-actual-project-id"

# 3. 상태 확인 
python config_manager.py status
```

### B. 환경변수 직접 설정 (간단)
```bash
# 프로젝트 루트의 .env 파일에 추가
cd ~/minecraft-modpack-ai
echo "GCP_PROJECT_ID=your-actual-project-id" >> .env
echo "GCS_BUCKET_NAME=your-bucket-name" >> .env
```

### C. 원클릭 스크립트 (수정됨)
```bash
cd ~/minecraft-modpack-ai

# RAG 인덱스 구축 (GCP 설정 포함)
./rag_quick_setup.sh build "Prominence_II_RPG_Hasturian_Era" "3.1.51hf" "/path/to/modpack"

# 설정 상태 확인
./rag_quick_setup.sh status
```

## ✅ 문제 해결 체크리스트

### 1. 환경 파일 경로 확인
```bash
cd ~/minecraft-modpack-ai/backend
python -c "
from config_manager import RAGConfigManager
manager = RAGConfigManager()
print(f'환경 파일 경로: {manager.env_file}')
print(f'파일 존재: {manager.env_file.exists()}')
"
```

### 2. GCP 설정 확인
```bash
cd ~/minecraft-modpack-ai
grep -E "(GCP_PROJECT_ID|GCS_BUCKET_NAME)" .env
```

### 3. 설정 상태 확인
```bash
cd ~/minecraft-modpack-ai/backend
python config_manager.py status
```

## 🎮 실제 사용 시나리오 (수정됨)

### 시나리오 1: 새 프로젝트 설정
```bash
cd ~/minecraft-modpack-ai

# 1. .env 파일 복사 및 수정
cp env.example .env
nano .env  # GCP_PROJECT_ID, GCS_BUCKET_NAME 설정

# 2. 모드팩 설정
cd backend
python config_manager.py set-manual "my_modpack" "1.0.0"

# 3. 상태 확인
python config_manager.py status
```

### 시나리오 2: 기존 프로젝트 수정
```bash
cd ~/minecraft-modpack-ai/backend

# 1. 현재 상태 확인
python config_manager.py status

# 2. GCP 프로젝트 ID 설정
python config_manager.py set-gcp-project "actual-project-id"

# 3. 다시 확인
python config_manager.py status
```

## 📊 예상 결과 (수정됨)

설정 완료 후 `python config_manager.py status` 실행 결과:
```
📋 RAG 시스템 설정 상태
==================================================
🔧 RAG 모드: manual
📦 현재 모드팩: Prominence_II_RPG_Hasturian_Era v3.1.51hf
🌐 GCP RAG: ✅ 활성화
✅ GCP 프로젝트 ID: your-actual-project-id
⚙️ 환경 파일: /home/namepix080/minecraft-modpack-ai/.env
📄 설정 파일: /home/namepix080/minecraft-modpack-ai/backend/rag_config.json

💡 수동 모드 활성화됨
   - RAG 검색이 지정된 모드팩에만 제한됩니다
   - 새 모드팩을 인덱싱하려면 rag_manager.py를 사용하세요
```

## 🚨 중요 변경사항

1. **환경 파일 경로**: `~/.minecraft-ai-backend/.env` → `~/minecraft-modpack-ai/.env`
2. **자동 탐지**: config_manager.py가 프로젝트 구조에 맞게 경로 탐지
3. **GCP 설정**: 필수 변수 누락 시 명확한 오류 메시지
4. **호환성**: 이전 경로도 지원하되 새 경로 우선 사용