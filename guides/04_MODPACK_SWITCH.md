# 🔄 관리자를 위한 모드팩 변경 가이드

## 📋 개요

이 가이드는 관리자가 GCP VM Debian에서 마인크래프트 모드팩을 변경하는 방법을 설명합니다.

### **모드팩 변경 방법들**
1. 🖥️ **CLI 스크립트** (가장 편리한 방법)
2. 🎮 **게임 내 명령어** (관리자 전용)
3. 🌐 **백엔드 API 직접 호출** (고급 사용자)

---

## 🖥️ CLI 스크립트 사용법 (권장)

### **기본 사용법**
```bash
# 설정 파일에서 모드팩 정보 읽어서 분석
modpack_switch

# 특정 모드팩 분석 (버전 자동 추출)
modpack_switch CreateModpack

# 특정 모드팩과 버전으로 분석
modpack_switch FTBRevelation 1.0.0

# 사용 가능한 모드팩 목록 확인
modpack_switch --list

# 도움말 보기
modpack_switch --help
```

### **CLI 스크립트 특징**
- ✅ **설정 파일 기반**: `.env` 파일에서 모드팩 정보 자동 읽기
- ✅ **자동 버전 추출**: 파일명에서 버전 정보 자동 추출
- ✅ **단일 모드팩 분석**: 빠르고 효율적인 분석
- ✅ **자동 설정 업데이트**: 분석 후 설정 파일 자동 업데이트
- ✅ **백엔드 상태 확인**: 서비스 실행 상태 자동 체크
- ✅ **상세 결과 표시**: 모드 수, 제작법 수, 아이템 수 등
- ✅ **색상 출력**: 정보, 성공, 경고, 오류 구분

### **CLI 스크립트 출력 예시**
```bash
$ modpack_switch CreateModpack

[INFO] 설정 파일에서 정보 로드:
[INFO]   모드팩 디렉토리: /tmp/modpacks
[INFO] 백엔드 서비스 상태 확인 중...
[SUCCESS] 백엔드 서비스가 정상 실행 중입니다
[INFO] 모드팩 분석 시작: CreateModpack v1.0.0
[INFO] 모드팩 파일 검색 중...
[SUCCESS] 모드팩 파일 발견: /tmp/modpacks/CreateModpack_1.0.0.zip
[INFO] 파일 크기: 256M
[INFO] 백엔드에 모드팩 분석 요청 중...
[SUCCESS] 모드팩 분석이 완료되었습니다!

📊 분석 결과:
  🎮 모드팩: CreateModpack v1.0.0
  📦 모드 수: 150
  🛠️ 제작법 수: 2500
  🎯 아이템 수: 3000
  🌐 언어 매핑: 500개 추가

[INFO] 설정 파일이 업데이트되었습니다
[INFO] 이제 게임 내에서 AI 어시스턴트를 사용할 수 있습니다!
```

---

## ⚠️ 사전 조건 및 준비사항

### **1. 모드팩 파일 업로드**

#### **파일 업로드 위치**
모드팩 파일을 다음 디렉토리에 업로드하세요:
```bash
/tmp/modpacks/
```

#### **업로드 방법**
```bash
# SCP 사용 (로컬에서 서버로)
scp your-modpack.zip username@server-ip:/tmp/modpacks/

# SFTP 사용
sftp username@server-ip
cd /tmp/modpacks/
put your-modpack.zip

# 직접 복사 (서버에서)
cp /path/to/your-modpack.zip /tmp/modpacks/
```

#### **지원하는 파일 형식**
- `.zip` 파일
- `.jar` 파일

#### **파일명 규칙**
스크립트는 다음 패턴의 파일명에서 버전을 자동 추출합니다:
- `modpack_name_version.zip` (예: `CreateModpack_1.0.0.zip`)
- `modpack_name-version.zip` (예: `CreateModpack-1.0.0.zip`)
- `modpack_name version.zip` (예: `CreateModpack 1.0.0.zip`)

### **2. 백엔드 서비스 확인**
```bash
# 백엔드 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 서비스가 실행되지 않은 경우 시작
sudo systemctl start mc-ai-backend
```

### **3. 설정 파일 확인**
```bash
# 설정 파일 확인
cat $HOME/minecraft-ai-backend/.env | grep MODPACK
```

---

## 🔧 상세 사용법

### **방법 1: 설정 파일 기반 분석**
```bash
# .env 파일에 모드팩 정보 설정
nano $HOME/minecraft-ai-backend/.env

# 다음 내용 추가/수정:
CURRENT_MODPACK_NAME=CreateModpack
CURRENT_MODPACK_VERSION=1.0.0

# 설정 파일에서 정보를 읽어서 분석
modpack_switch
```

### **방법 2: 명령행 인수로 분석**
```bash
# 모드팩명만 지정 (버전 자동 추출)
modpack_switch CreateModpack

# 모드팩명과 버전 모두 지정
modpack_switch FTBRevelation 1.0.0
```

### **방법 3: 파일명에서 버전 추출**
파일명에 버전이 포함되어 있으면 자동으로 추출됩니다:
```bash
# 파일: CreateModpack_1.0.0.zip
modpack_switch CreateModpack
# → 자동으로 버전 1.0.0 추출

# 파일: FTBRevelation-2.0.1.zip
modpack_switch FTBRevelation
# → 자동으로 버전 2.0.1 추출
```

---

## 📊 분석 결과 해석

### **분석 결과 예시**
```
📊 분석 결과:
  🎮 모드팩: CreateModpack v1.0.0
  📦 모드 수: 150
  🛠️ 제작법 수: 2500
  🎯 아이템 수: 3000
  🌐 언어 매핑: 500개 추가
```

### **결과 항목 설명**
- **모드팩**: 분석된 모드팩의 이름과 버전
- **모드 수**: 모드팩에 포함된 모드의 개수
- **제작법 수**: 추출된 제작법의 개수
- **아이템 수**: 추출된 아이템의 개수
- **언어 매핑**: 자동 생성된 한국어-영어 매핑 개수

---

## 🔄 모드팩 변경 워크플로우

### **1. 새 모드팩 준비**
```bash
# 1. 모드팩 파일을 /tmp/modpacks/에 업로드
scp new-modpack.zip username@server-ip:/tmp/modpacks/

# 2. 업로드된 파일 확인
ls -la /tmp/modpacks/
```

### **2. 모드팩 분석**
```bash
# 방법 1: 설정 파일 업데이트 후 분석
nano $HOME/minecraft-ai-backend/.env
# CURRENT_MODPACK_NAME=new-modpack 추가
modpack_switch

# 방법 2: 직접 분석
modpack_switch new-modpack 1.0.0
```

### **3. 게임 서버 시작**
```bash
# 해당 모드팩 서버 시작
cd ~/new-modpack
./start.sh
```

### **4. 게임 내 테스트**
```bash
# 게임 내에서 AI 어시스턴트 테스트
/modpackai help
/give @p nether_star 1
```

---

## 🚨 문제 해결

### **모드팩 파일을 찾을 수 없는 경우**
```bash
# 1. 파일 존재 확인
ls -la /tmp/modpacks/

# 2. 파일명 확인
modpack_switch --list

# 3. 파일명 수정 (필요한 경우)
mv /tmp/modpacks/old-name.zip /tmp/modpacks/CreateModpack_1.0.0.zip
```

### **백엔드 서비스 오류**
```bash
# 1. 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 2. 서비스 재시작
sudo systemctl restart mc-ai-backend

# 3. 로그 확인
sudo journalctl -u mc-ai-backend -f
```

### **버전 추출 실패**
```bash
# 1. 파일명에서 버전 추출 시도
modpack_switch CreateModpack
# → "버전을 추출할 수 없어 기본값(1.0)을 사용합니다" 메시지

# 2. 수동으로 버전 지정
modpack_switch CreateModpack 1.0.0
```

### **권한 오류**
```bash
# 1. 파일 권한 확인
ls -la /tmp/modpacks/

# 2. 권한 수정
sudo chmod 644 /tmp/modpacks/*.zip
sudo chmod 644 /tmp/modpacks/*.jar
```

---

## 📝 설정 파일 관리

### **설정 파일 위치**
```bash
$HOME/minecraft-ai-backend/.env
```

### **모드팩 관련 설정**
```bash
# 현재 사용할 모드팩 이름
CURRENT_MODPACK_NAME=CreateModpack

# 현재 사용할 모드팩 버전
CURRENT_MODPACK_VERSION=1.0.0

# 모드팩 업로드 디렉토리
MODPACK_UPLOAD_DIR=/tmp/modpacks
```

### **설정 파일 자동 업데이트**
`modpack_switch` 명령어를 실행하면 다음 정보가 자동으로 업데이트됩니다:
- `CURRENT_MODPACK_NAME`: 분석된 모드팩 이름
- `CURRENT_MODPACK_VERSION`: 분석된 모드팩 버전

---

## 🎮 게임 내 모드팩 변경 (관리자 전용)

### **게임 내 명령어**
```bash
# 모드팩 변경 (관리자만)
/modpackai switch <모드팩명> [버전]

# 예시
/modpackai switch CreateModpack
/modpackai switch FTBRevelation 1.0.0
```

### **권한 설정**
```bash
# 관리자 권한 부여
/op <플레이어명>
# 또는
/lp user <플레이어명> permission set modpackai.admin true
```

---

## 🌐 API 직접 호출 (고급 사용자)

### **모드팩 변경 API**
```bash
curl -X POST http://localhost:5000/api/modpack/switch \
  -H "Content-Type: application/json" \
  -d '{
    "modpack_path": "/tmp/modpacks/CreateModpack_1.0.0.zip",
    "modpack_name": "CreateModpack",
    "modpack_version": "1.0.0"
  }'
```

### **응답 예시**
```json
{
  "message": "모드팩 CreateModpack v1.0.0로 성공적으로 변경되었습니다.",
  "analysis_result": {
    "modpack_name": "CreateModpack",
    "mods_count": 150,
    "recipes_count": 2500,
    "items_count": 3000
  },
  "language_mappings_added": 500,
  "rag_updated": true
}
```

---

## 📋 체크리스트

### **모드팩 변경 전**
- [ ] 모드팩 파일이 `/tmp/modpacks/`에 업로드됨
- [ ] 백엔드 서비스가 정상 실행 중
- [ ] 파일 권한이 올바르게 설정됨

### **모드팩 변경 후**
- [ ] 분석이 성공적으로 완료됨
- [ ] 설정 파일이 자동 업데이트됨
- [ ] 게임 서버에서 AI 어시스턴트 테스트
- [ ] 제작법 조회 기능 테스트

---

**🎮 이제 새로운 모드팩으로 AI 어시스턴트를 사용할 수 있습니다!** 🚀 