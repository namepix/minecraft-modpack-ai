# 🔧 통합된 환경 설정 가이드

## 📋 **최종 결정: `~/minecraft-ai-backend/.env` 표준화**

**표준 환경 파일 경로**: `~/minecraft-ai-backend/.env`

### 🎯 **결정 근거**

1. **기존 호환성**: 사용자가 이미 `~/minecraft-ai-backend/.env`에 설정 완료
2. **설치 스크립트 호환**: 기존 install.sh, deploy.sh 등이 이 경로 사용
3. **보안성**: 프로젝트 디렉토리와 분리된 환경 설정 (Git 추적 방지)
4. **일관성**: 모든 시스템 컴포넌트가 단일 경로 사용

## 🛠️ **수정된 시스템 구조**

```
~/minecraft-modpack-ai/              # Git 프로젝트 (소스 코드)
├── backend/app.py                   # → ~/minecraft-ai-backend/.env 참조
├── backend/config_manager.py        # → ~/minecraft-ai-backend/.env 관리
├── env.example                      # 환경 설정 템플릿
└── README.md

~/minecraft-ai-backend/              # 런타임 환경 (데이터 + 설정)
├── .env                            # ✅ 표준 환경 파일 (모든 시스템 사용)
├── logs/                           # 로그 파일
└── backups/                        # 백업 파일
```

## ✅ **자동 환경 설정**

config_manager.py가 자동으로:
1. `~/minecraft-ai-backend/` 디렉토리 생성
2. `env.example`에서 `.env` 파일 초기화  
3. 기존 설정 보존

## 📝 **사용법 (통합본)**

### A. 즉시 해결 (현재 상황)
```bash
# 이미 ~/minecraft-ai-backend/.env에 설정되어 있으므로
cd ~/minecraft-modpack-ai/backend

# GCP 프로젝트 ID만 추가 설정
python config_manager.py set-gcp-project "your-actual-gcp-project-id"

# 상태 확인
python config_manager.py status
```

### B. 새 설치시
```bash
cd ~/minecraft-modpack-ai/backend

# 자동으로 ~/minecraft-ai-backend/.env 생성되고 초기화됨
python config_manager.py status

# 필요한 설정만 추가
python config_manager.py set-gcp-project "your-project-id"
python config_manager.py set-manual "modpack_name" "1.0.0"
```

### C. 수동 설정
```bash
# 환경 파일 직접 편집
nano ~/minecraft-ai-backend/.env

# 또는 변수 추가
echo "GCP_PROJECT_ID=your-project-id" >> ~/minecraft-ai-backend/.env
echo "GCS_BUCKET_NAME=your-bucket-name" >> ~/minecraft-ai-backend/.env
```

## 🔄 **마이그레이션 (필요시)**

기존에 다른 위치에 .env가 있는 경우:
```bash
# 기존 설정 복사
cp ~/minecraft-modpack-ai/.env ~/minecraft-ai-backend/.env

# 또는 수동으로 이동
mv ~/other-location/.env ~/minecraft-ai-backend/.env
```

## 📊 **예상 결과**

설정 완료 후:
```
📋 RAG 시스템 설정 상태
==================================================
🔧 RAG 모드: manual
📦 현재 모드팩: Prominence_II_RPG_Hasturian_Era v3.1.51hf
🌐 GCP RAG: ✅ 활성화
✅ GCP 프로젝트 ID: your-actual-project-id
⚙️ 환경 파일: /home/namepix080/minecraft-ai-backend/.env
📄 설정 파일: /home/namepix080/minecraft-modpack-ai/backend/rag_config.json
```

## 🛡️ **보안 고려사항**

- ✅ Git 추적 방지 (프로젝트 외부 위치)
- ✅ 사용자별 개별 설정
- ✅ 프로덕션 환경과 개발 환경 분리 가능

## 🔧 **문제 해결**

### 환경 파일이 없는 경우
```bash
cd ~/minecraft-modpack-ai/backend
python config_manager.py status  # 자동으로 생성됨
```

### 권한 문제
```bash
chmod 600 ~/minecraft-ai-backend/.env  # 읽기/쓰기 권한만
```

### 설정 확인
```bash
cat ~/minecraft-ai-backend/.env | grep -E "(GCP_PROJECT_ID|GOOGLE_API_KEY)"
```

## 🚨 **중요 사항**

1. **단일 진실 원천**: `~/minecraft-ai-backend/.env`만 사용
2. **자동 초기화**: config_manager.py 실행 시 자동 설정
3. **기존 설정 보존**: 이미 있는 환경 파일은 그대로 유지
4. **일관된 경로**: 모든 코드가 동일한 경로 참조

이제 모든 시스템 컴포넌트가 `~/minecraft-ai-backend/.env`를 표준으로 사용합니다.