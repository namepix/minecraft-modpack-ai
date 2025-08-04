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
# 모드팩 변경
modpack_switch CreateModpack
modpack_switch FTBRevelation 1.0.0
modpack_switch AllTheMods 1.19.2

# 사용 가능한 모드팩 목록 확인
modpack_switch --list

# 도움말 보기
modpack_switch --help
```

### **CLI 스크립트 특징**
- ✅ **자동 파일 탐지**: 여러 파일명 패턴 자동 매칭
- ✅ **백엔드 상태 확인**: 서비스 실행 상태 자동 체크
- ✅ **상세 결과 표시**: 모드 수, 제작법 수, 아이템 수 등
- ✅ **색상 출력**: 정보, 성공, 경고, 오류 구분

### **CLI 스크립트 출력 예시**
```bash
$ modpack_switch CreateModpack 1.0.0

[INFO] 설정 파일에서 모드팩 디렉토리 로드: /tmp/modpacks
[INFO] 백엔드 서비스 상태 확인 중...
[SUCCESS] 백엔드 서비스가 정상 실행 중입니다
[INFO] 모드팩 변경 시작: CreateModpack v1.0.0
[INFO] 모드팩 파일 검색 중...
[SUCCESS] 모드팩 파일 발견: /tmp/modpacks/CreateModpack_1.0.0.zip
[INFO] 파일 크기: 256M
[INFO] 백엔드에 모드팩 변경 요청 중...
[SUCCESS] 모드팩 변경이 완료되었습니다!

📊 변경 결과:
  🎮 모드팩: CreateModpack v1.0.0
  📦 모드 수: 150
  🛠️ 제작법 수: 2500
  🎯 아이템 수: 3000
  🌐 언어 매핑: 500개 추가

[INFO] 이제 게임 내에서 AI 어시스턴트를 사용할 수 있습니다!
```

---

## ⚠️ 사전 조건 및 준비사항

### **1. 모드팩 파일 업로드**

#### **파일 업로드 위치**
```bash
# 권장 위치 1: 임시 디렉토리
/tmp/modpacks/

# 권장 위치 2: 백엔드 업로드 디렉토리
/opt/mc_ai_backend/uploads/

# 권장 위치 3: 사용자 홈 디렉토리
~/modpacks/
```

#### **디렉토리 생성 및 설정**
```bash
# 디렉토리 생성
sudo mkdir -p /tmp/modpacks
sudo mkdir -p /opt/mc_ai_backend/uploads
sudo mkdir -p ~/modpacks

# 권한 설정
sudo chown -R $USER:$USER /tmp/modpacks
sudo chown -R $USER:$USER /opt/mc_ai_backend/uploads
sudo chmod 755 /tmp/modpacks
sudo chmod 755 /opt/mc_ai_backend/uploads
```

#### **파일 업로드 방법**
```bash
# 로컬에서 서버로 업로드
scp your-modpack.zip username@your-server-ip:/tmp/modpacks/

# 또는 GCP 콘솔을 통한 업로드
# 1. GCP Console → Compute Engine → VM 인스턴스
# 2. SSH 연결 → 파일 업로드 기능 사용
```

### **2. 파일명 규칙**

#### **권장 파일명 형식**
```
모드팩명_버전.zip
```

**예시**:
- `CreateModpack_1.0.0.zip`
- `FTBRevelation_1.0.0.zip`
- `AllTheMods_1.19.2.zip`

#### **CLI 스크립트 자동 매칭 패턴**
```bash
# CLI 스크립트가 자동으로 확인하는 패턴들
CreateModpack_1.0.0.zip
CreateModpack_1.0.0.jar
CreateModpack.zip
CreateModpack.jar
createmodpack_1.0.0.zip  # 소문자도 지원
createmodpack_1.0.0.jar
createmodpack.zip
createmodpack.jar
```

### **3. 시스템 요구사항**
- ✅ 백엔드 서비스 실행 중
- ✅ 충분한 디스크 공간 (모드팩 크기의 3배)
- ✅ 모드팩 파일이 지원 형식 (.zip, .jar)

---

## 🚀 모드팩 변경 과정

### **CLI 스크립트 사용 시**
```
1. 모드팩 파일 업로드
   ↓
2. CLI 명령어 실행
   modpack_switch <모드팩명> [버전]
   ↓
3. 자동 처리
   ├── 백엔드 서비스 상태 확인
   ├── 파일 경로 자동 탐지
   ├── 파일 크기 및 권한 확인
   ├── 백엔드 API 호출
   └── 결과 표시
   ↓
4. 완료 알림
```

### **게임 내 명령어 사용 시**
```
1. 모드팩 파일 업로드
   ↓
2. 게임 내 명령어 실행
   /modpackai switch <모드팩명> [버전]
   ↓
3. 백엔드 자동 처리
   ├── 파일 경로 자동 탐지
   ├── 모드팩 분석
   ├── 데이터베이스 업데이트
   ├── 언어 매핑 생성
   └── RAG 데이터 업데이트
   ↓
4. 완료 알림
```

---

## 🎮 게임 내 명령어 사용법

### **관리자 명령어**
```bash
# 모드팩 변경
/modpackai switch CreateModpack
/modpackai switch FTBRevelation 1.0.0
/modpackai switch AllTheMods 1.19.2

# 현재 모드팩 정보 확인
/modpackai current
```

### **권한 설정**
```bash
# 관리자 권한 부여
/op <플레이어명>

# 권한 확인
/lp user <플레이어명> permission set modpackai.admin true
```

---

## 🌐 백엔드 API 직접 호출

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

### **모드팩 분석 API (분석만)**
```bash
curl -X POST http://localhost:5000/api/modpack/analyze \
  -H "Content-Type: application/json" \
  -d '{"modpack_path": "/tmp/modpacks/CreateModpack_1.0.0.zip"}'
```

### **응답 예시**
```json
{
  "message": "모드팩 CreateModpack v1.0.0로 성공적으로 변경되었습니다.",
  "analysis_result": {
    "analysis_status": "completed",
    "mods_count": 150,
    "recipes_count": 2500,
    "items_count": 3000
  },
  "language_mappings_added": 500,
  "rag_updated": true
}
```

---

## 🔧 고급 설정

### **1. 환경 변수 설정**
```bash
# .env 파일에 추가
MODPACK_UPLOAD_DIR=/tmp/modpacks
MODPACK_BACKUP_DIR=/opt/mc_ai_backend/backups
```

### **2. 자동 파일 정리**
```bash
# 7일 이상 된 임시 파일 자동 삭제
find /tmp/modpacks -name "*.zip" -mtime +7 -delete
```

### **3. 백업 설정**
```bash
# 모드팩 변경 전 자동 백업
cp /opt/mc_ai_backend/recipes.db /opt/mc_ai_backend/backups/recipes_$(date +%Y%m%d_%H%M%S).db
```

### **4. 모니터링 스크립트**
```bash
#!/bin/bash
# modpack_monitor.sh
MODPACK_DIR="/tmp/modpacks"
BACKEND_URL="http://localhost:5000"

# 새 모드팩 파일 감지
inotifywait -m -e create "$MODPACK_DIR" | while read path action file; do
    if [[ $file == *.zip ]]; then
        echo "새 모드팩 파일 감지: $file"
        # 자동 분석 요청
        curl -X POST "$BACKEND_URL/api/modpack/analyze" \
          -H "Content-Type: application/json" \
          -d "{\"modpack_path\": \"$MODPACK_DIR/$file\"}"
    fi
done
```

---

## 🚨 문제 해결

### **파일을 찾을 수 없을 때**
```bash
# 1. 파일 존재 확인
ls -la /tmp/modpacks/
ls -la /opt/mc_ai_backend/uploads/

# 2. 파일명 확인
find /tmp -name "*modpack*" -type f
find /opt -name "*modpack*" -type f

# 3. 권한 확인
ls -la /tmp/modpacks/your-modpack.zip
```

### **권한 오류**
```bash
# 파일 권한 수정
sudo chmod 644 /tmp/modpacks/your-modpack.zip
sudo chown $USER:$USER /tmp/modpacks/your-modpack.zip
```

### **디스크 공간 부족**
```bash
# 디스크 사용량 확인
df -h
du -sh /tmp/modpacks/
du -sh /opt/mc_ai_backend/

# 불필요한 파일 정리
sudo apt autoremove -y
sudo journalctl --vacuum-time=7d
```

### **백엔드 서비스 오류**
```bash
# 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 로그 확인
sudo journalctl -u mc-ai-backend -f

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

### **CLI 스크립트 오류**
```bash
# 스크립트 권한 확인
ls -la /usr/local/bin/modpack_switch

# 권한 수정
sudo chmod +x /usr/local/bin/modpack_switch

# 스크립트 재설치
sudo cp modpack_switch.sh /usr/local/bin/modpack_switch
sudo chmod +x /usr/local/bin/modpack_switch
```

---

## 💡 사용 팁

### **1. 효율적인 파일 관리**
- 📁 모드팩별로 폴더 분리
- 🏷️ 파일명에 버전 정보 포함
- 🗑️ 사용 후 임시 파일 정리

### **2. CLI 스크립트 사용 최적화**
```bash
# 파일명과 명령어 일치시키기
# 파일: CreateModpack_1.0.0.zip
# 명령어: modpack_switch CreateModpack 1.0.0

# 사용 가능한 모드팩 확인
modpack_switch --list

# 도움말 확인
modpack_switch --help
```

### **3. 자동화 스크립트**
```bash
#!/bin/bash
# auto_modpack_switch.sh
MODPACK_NAME=$1
VERSION=$2

# 파일 업로드 확인
if [ -f "/tmp/modpacks/${MODPACK_NAME}_${VERSION}.zip" ]; then
    echo "모드팩 파일 확인됨"
    # CLI 스크립트 실행
    modpack_switch $MODPACK_NAME $VERSION
else
    echo "모드팩 파일을 찾을 수 없습니다: /tmp/modpacks/${MODPACK_NAME}_${VERSION}.zip"
fi
```

### **4. 모드팩 변경 워크플로우**
```bash
# 1. 새 모드팩 파일 업로드
scp CreateModpack_1.0.0.zip username@server-ip:/tmp/modpacks/

# 2. 사용 가능한 모드팩 확인
modpack_switch --list

# 3. 모드팩 변경
modpack_switch CreateModpack 1.0.0

# 4. 변경 결과 확인
echo "모드팩 변경 완료!"

# 5. 게임 서버 재시작 (필요시)
cd ~/CreateModpack
./start.sh
```

---

## 📊 모드팩 변경 체크리스트

### **사전 준비**
- [ ] 새 모드팩 파일 준비
- [ ] 파일명 규칙 확인 (모드팩명_버전.zip)
- [ ] 충분한 디스크 공간 확인
- [ ] 백엔드 서비스 상태 확인

### **파일 업로드**
- [ ] 업로드 디렉토리 생성 및 권한 설정
- [ ] 모드팩 파일 업로드
- [ ] 파일 권한 확인
- [ ] 파일 크기 확인

### **모드팩 변경**
- [ ] CLI 스크립트 또는 게임 내 명령어 실행
- [ ] 백엔드 응답 확인
- [ ] 변경 결과 확인 (모드 수, 제작법 수 등)
- [ ] 오류 발생 시 로그 확인

### **사후 확인**
- [ ] 게임 내 AI 어시스턴트 테스트
- [ ] 제작법 조회 테스트
- [ ] 채팅 기능 테스트
- [ ] 플레이어들에게 변경 공지

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 파일이 올바른 위치에 업로드되었는지
2. 파일명과 명령어 인수가 일치하는지
3. 백엔드 서비스가 정상 실행 중인지
4. 충분한 디스크 공간이 있는지
5. CLI 스크립트가 올바르게 설치되었는지

### **로그 확인**
```bash
# 백엔드 로그
sudo journalctl -u mc-ai-backend -f

# 시스템 로그
tail -f /var/log/syslog

# 디스크 사용량
df -h
```

**🎮 모드팩 변경이 성공적으로 완료되었습니다!** 🚀 