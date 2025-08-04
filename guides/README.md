# 📚 마인크래프트 모드팩 AI 시스템 가이드

이 폴더에는 마인크래프트 모드팩 AI 시스템의 사용을 위한 상세한 가이드들이 포함되어 있습니다.

---

## 📖 가이드 목록

### 1. 🛠️ [관리자를 위한 AI 모드 추가 가이드](01_ADMIN_SETUP.md)
**대상**: 서버 관리자  
**내용**: 기존 마인크래프트 모드팩 서버에 AI 모드를 추가하는 방법

**주요 내용**:
- AI 백엔드 설치 및 설정
- 기존 모드팩에 AI 플러그인 추가
- 모드팩별 AI 데이터 설정
- 서버 시작 스크립트 수정
- 테스트 및 확인 방법

### 2. 🏗️ [시스템 전체 구조 가이드](02_SYSTEM_OVERVIEW.md)
**대상**: 개발자, 시스템 관리자  
**내용**: 프로젝트의 전체적인 아키텍처와 데이터 흐름

**주요 내용**:
- 시스템 아키텍처 및 구성 요소
- 데이터 처리 파이프라인
- AI 모델 통합 방식
- API 엔드포인트 설명
- 성능 및 보안 정보

### 3. 🎮 [게임 내 AI 모드 명령어 사용법](03_GAME_COMMANDS.md)
**대상**: 일반 플레이어  
**내용**: 게임 내에서 AI 어시스턴트를 사용하는 방법

**주요 내용**:
- 모든 게임 내 명령어 설명
- AI 채팅 및 제작법 조회 방법
- AI 모델 선택 및 관리
- 아이템 기반 GUI 사용법
- 문제 해결 가이드

### 4. 🔄 [관리자를 위한 모드팩 변경 가이드](04_MODPACK_SWITCH.md)
**대상**: 서버 관리자  
**내용**: 모드팩을 변경하고 AI 시스템에 적용하는 방법

**주요 내용**:
- CLI 스크립트 사용법 (권장)
- 게임 내 명령어 사용법
- 백엔드 API 직접 호출 방법
- 파일 업로드 및 관리
- 문제 해결 및 체크리스트

---

## 🎯 사용자별 권장 가이드

### **일반 플레이어**
- [03_GAME_COMMANDS.md](03_GAME_COMMANDS.md) - 게임 내 명령어 사용법

### **서버 관리자**
- [01_ADMIN_SETUP.md](01_ADMIN_SETUP.md) - AI 모드 추가 가이드
- [04_MODPACK_SWITCH.md](04_MODPACK_SWITCH.md) - 모드팩 변경 가이드

### **개발자/시스템 관리자**
- [02_SYSTEM_OVERVIEW.md](02_SYSTEM_OVERVIEW.md) - 시스템 전체 구조

---

## 🚀 빠른 시작

### **1단계: AI 모드 추가 (관리자)**
```bash
# 1. AI 백엔드 설치
./install.sh

# 2. API 키 설정
nano /opt/mc_ai_backend/.env

# 3. 백엔드 서비스 시작
sudo systemctl start mc-ai-backend
```

### **2단계: 기존 모드팩에 플러그인 추가**
```bash
# 모든 모드팩에 AI 플러그인 추가
for dir in ~/modpack*; do
    mkdir -p "$dir/plugins"
    cp /opt/minecraft/plugins/ModpackAI-1.0.jar "$dir/plugins/"
done
```

### **3단계: 모드팩 데이터 등록**
```bash
# 모드팩 변경
modpack_switch CreateModpack 1.0.0
```

### **4단계: 게임 내 사용 (플레이어)**
```
# AI 채팅 시작
/modpackai chat

# 제작법 조회
/modpackai recipe 다이아몬드 검

# AI 모델 선택
/modpackai models
```

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. **시스템 상태 확인**
   ```bash
   sudo systemctl status mc-ai-backend
   curl http://localhost:5000/health
   ```

2. **로그 확인**
   ```bash
   sudo journalctl -u mc-ai-backend -f
   ```

3. **가이드 참조**
   - 문제 유형에 따라 해당 가이드 파일 확인
   - 각 가이드의 "문제 해결" 섹션 참조

---

## 🔗 관련 파일

- `modpack_switch.sh` - CLI 모드팩 변경 스크립트
- `install.sh` - 자동 설치 스크립트
- `monitor.sh` - 시스템 모니터링 스크립트
- `env.example` - 환경 변수 설정 예시

---

**🎮 즐거운 모드팩 플레이 되세요!** 🚀 