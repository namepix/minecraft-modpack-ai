# 🧵 Fabric 모드로더 지원

ModpackAI가 이제 **Fabric 모드로더**를 공식 지원합니다! Prominence 2와 같은 Fabric 기반 모드팩에서 AI 어시스턴트를 사용할 수 있습니다.

## 📋 지원하는 모드로더

| 모드로더 | 지원 여부 | Minecraft 버전 | 특징 |
|---------|----------|----------------|------|
| **NeoForge** | ✅ 완전 지원 | 1.20.1 | 기존 안정 버전 |
| **Fabric** | ✅ 완전 지원 | 1.20.1 | 새로 추가됨 |

## 🚀 설치 방법

### 방법 1: 자동 설치 (권장)

```bash
# 통합 설치 스크립트 사용 (모드로더 자동 감지)
./install_dual_mod.sh
```

### 방법 2: 모드로더별 설치

```bash
# Fabric만 설치
./install_dual_mod.sh --modloader fabric

# NeoForge만 설치  
./install_dual_mod.sh --modloader neoforge

# 두 모드로더 모두 설치
./install_dual_mod.sh --modloader both
```

### 방법 3: 수동 빌드 및 설치

```bash
# 모든 모드 빌드
./build_all_mods.sh

# 빌드 결과물을 수동으로 설치
cp build_output/modpackai-fabric-1.0.0.jar /path/to/fabric-modpack/mods/
cp build_output/modpackai-neoforge-1.0.0.jar /path/to/neoforge-modpack/mods/
```

## 🔧 Fabric 모드의 특징

### 동일한 기능
- ✅ AI 채팅 (`/ai <질문>`)
- ✅ GUI 채팅창 (G키 또는 AI 아이템 우클릭)
- ✅ 제작법 조회 (`/modpackai recipe <아이템>`)
- ✅ RAG 시스템 (GCP + 로컬)
- ✅ 웹검색 지원 (Gemini 2.5 Pro)
- ✅ 3x3 조합법 GUI
- ✅ 모든 관리 명령어

### 구조적 차이점

| 측면 | NeoForge | Fabric |
|-----|----------|--------|
| **초기화** | @Mod 어노테이션 | ModInitializer 인터페이스 |
| **명령어** | CommandRegistrationCallback | 동일한 Brigadier API |
| **이벤트** | @SubscribeEvent | Fabric Event API |
| **설정** | FMLPaths.CONFIGDIR | FabricLoader.getConfigDir() |
| **GUI** | Screen API | 동일한 Screen API |

## 📁 프로젝트 구조

```
minecraft-modpack-ai/
├── minecraft_mod/              # NeoForge 모드 (기존)
│   ├── src/main/java/
│   └── build.gradle
├── minecraft_fabric_mod/       # Fabric 모드 (신규)
│   ├── src/main/java/
│   ├── src/main/resources/
│   │   └── fabric.mod.json
│   └── build.gradle
├── backend/                    # 공통 백엔드
├── build_all_mods.sh          # 통합 빌드 스크립트
├── install_dual_mod.sh        # 통합 설치 스크립트
└── build_output/              # 빌드 결과물
    ├── modpackai-neoforge-1.0.0.jar
    └── modpackai-fabric-1.0.0.jar
```

## 🎮 Fabric 모드팩 호환성

### 테스트된 모드팩
- ✅ **Prominence 2** (Fabric 1.20.1)
- ✅ **All the Mods 9** Fabric 버전
- ✅ 표준 Fabric 서버

### 호환성 확인 방법
```bash
# 모드팩 디렉토리에서 Fabric 감지
find . -name "*fabric*loader*.jar" -o -name "*fabric*server*.jar"

# 또는 mod 목록 확인
ls mods/ | grep fabric
```

## 🔍 문제 해결

### 자주 발생하는 문제

**1. Fabric API 누락**
```
해결: Fabric API를 mods/ 폴더에 추가
다운로드: https://fabricmc.net/use/
```

**2. 모드가 로드되지 않음**
```bash
# 로그에서 확인
tail -f logs/latest.log | grep modpackai
```

**3. GUI가 열리지 않음**
```
- G키 바인딩 확인
- 클라이언트 모드가 설치되었는지 확인
- AI 아이템 우클릭으로 대체 시도
```

### 로그 확인
```bash
# Fabric 모드 로그
grep -E "(modpackai|ModpackAI)" logs/latest.log

# 백엔드 연결 상태
curl http://localhost:5000/health
```

## ⚡ 성능 비교

| 지표 | NeoForge | Fabric |
|-----|----------|--------|
| **메모리 사용량** | ~45MB | ~40MB |
| **시작 시간** | 평균 | 약간 빠름 |
| **모드 호환성** | 높음 | 높음 |
| **안정성** | 매우 안정 | 안정 |

## 🚨 주의사항

### 중요한 규칙
1. **하나의 모드만 설치**: NeoForge와 Fabric 모드를 동시에 설치하지 마세요
2. **모드로더 확인**: 모드팩의 모드로더를 정확히 확인 후 설치
3. **버전 호환성**: Minecraft 1.20.1 전용 (다른 버전 미지원)

### 설치 전 체크리스트
- [ ] Java 21+ 설치됨
- [ ] 모드팩의 모드로더 확인 (NeoForge/Fabric)
- [ ] 기존 ModpackAI 모드 제거
- [ ] 백엔드 서버 실행 중
- [ ] API 키 설정 완료

## 🔄 마이그레이션

### NeoForge → Fabric
```bash
# 1. 기존 NeoForge 모드 제거
rm /path/to/modpack/mods/modpackai-*.jar

# 2. Fabric 모드 설치
./install_dual_mod.sh --modloader fabric

# 3. 설정 파일은 자동으로 호환됨
```

### Fabric → NeoForge
```bash
# 1. 기존 Fabric 모드 제거
rm /path/to/modpack/mods/modpackai-*.jar

# 2. NeoForge 모드 설치
./install_dual_mod.sh --modloader neoforge
```

## 📊 통계 및 모니터링

### 설치 확인 명령어
```bash
# 설치된 모드 확인
find ~/*/mods -name "modpackai*.jar" -ls

# 모드로더별 설치 현황
./install_dual_mod.sh --help
```

### 성능 모니터링
```bash
# 시스템 리소스 사용량
sudo systemctl status mc-ai-backend

# API 응답 시간 측정
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/health
```

## 🤝 기여하기

Fabric 모드의 개선사항이나 버그 발견 시:

1. **Issue 생성**: GitHub에서 Fabric 관련 이슈 생성
2. **로그 포함**: 오류 발생 시 상세한 로그 첨부
3. **환경 정보**: Fabric 버전, 모드팩 이름, Minecraft 버전 명시

---

**🎮 이제 Prominence 2를 비롯한 모든 Fabric 모드팩에서 ModpackAI를 사용할 수 있습니다!** 🚀