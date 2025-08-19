# 🎮 마인크래프트 모드팩 AI 시스템 (NeoForge 모드)

**NeoForge 모드**로 구현된 마인크래프트 모드팩 전문 AI 어시스턴트입니다. 게임 내에서 모드팩 관련 질문에 답변하고 제작법을 제공합니다.

## ✨ 주요 기능

- 🤖 **Gemini 2.5 Pro 중심**: 웹검색 지원으로 최신 모드 정보 실시간 제공
- 🌐 **실시간 웹검색**: Google 검색을 통한 최신 모드 업데이트 및 정보 확인
- 🎯 **모드팩 전문 지식**: 특정 모드팩에 대한 정확한 정보 제공
- 🛠️ **NeoForge 네이티브**: 순수 NeoForge 모드로 구현되어 안정성 극대화
- 💬 **Screen 기반 GUI**: 더 유연하고 강력한 AI 채팅 인터페이스
- 🌐 **한글/영어 호환**: 아이템명과 질문 모두 한글/영어 사용 가능
- 🔄 **간편한 배포**: 자동화된 GCP VM 배포 및 업데이트 시스템
- 🛡️ **보안 및 모니터링**: 내장된 보안 미들웨어와 성능 모니터링

## 🏗️ 시스템 아키텍처 (모드 기반)

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Minecraft     │ ◄────────────► │   AI Backend    │
│   NeoForge Mod  │                │   (Flask)       │
│                 │                │                 │
│  - Screen GUI    │                │  - Gemini 2.5   │
│  - Commands      │                │    Pro (메인)    │
│  - Event Handler │                │  - 보안 미들웨어  │
│  - Config (JSON) │                │  - 모니터링      │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   NeoForge      │                │  Google Search  │
│   Modpack Server│                │   (웹검색)        │
│                 │                │                 │
│  - Modpack      │                │  - 실시간 정보   │
│  - Players      │                │  - 모드 업데이트 │
│  - Mod JAR      │                │  - 최신 데이터   │
└─────────────────┘                └─────────────────┘
```

## 🚀 빠른 시작

### 1. 설치 (NeoForge 모드 방식)
```bash
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
chmod +x install_mod.sh
./install_mod.sh
```

### 2. API 키 설정 (Gemini Pro 우선)
```bash
nano $HOME/minecraft-ai-backend/.env
# 🌟 GOOGLE_API_KEY=your-key (필수, 웹검색 지원)
# 📖 OPENAI_API_KEY=your-key (선택, 백업용)
# 📖 ANTHROPIC_API_KEY=your-key (선택, 백업용)
```

### 3. 서비스 시작
```bash
sudo systemctl start mc-ai-backend
sudo systemctl enable mc-ai-backend
```

### 4. 모드 설치 확인
```bash
# 각 모드팩의 mods 폴더에 모드 파일 확인
ls ~/*/mods/modpackai-*.jar
```

### 5. 게임 내 사용
```
/ai 철 블록은 어떻게 만들어?    # AI에게 바로 질문
/ai                           # AI GUI 열기 (클라이언트)
/modpackai give               # AI 아이템 받기
/modpackai recipe 다이아몬드   # 제작법 조회
/modpackai help               # 도움말 보기
```

### 6. API 엔드포인트
```
GET  /health                    # 서버 상태 확인
POST /chat                      # AI 채팅
GET  /models                    # 사용 가능한 AI 모델 목록
POST /models/switch             # AI 모델 전환
GET  /recipe/<item_name>        # 아이템 제작법 조회
```

**💡 팁**: AI 어시스턴트 아이템(네더 스타)을 우클릭하면 바로 채팅창이 열립니다!

## 📚 상세 가이드

- [관리자 설정 가이드](guides/01_ADMIN_SETUP.md)
- [시스템 개요](guides/02_SYSTEM_OVERVIEW.md)
- [게임 내 명령어](guides/03_GAME_COMMANDS.md)
- [모드팩 전환](guides/04_MODPACK_SWITCH.md)
- [개발자 가이드](guides/05_DEVELOPMENT.md)
- [다중 Java 버전 지원 가이드](MULTI_JAVA_GUIDE.md)
- [Fabric 빌드 문제 해결](FABRIC_BUILD_TROUBLESHOOTING.md)

## 🔄 다중 Java 버전 지원

### 🎯 지원하는 구성
| 모드팩 예시 | 플랫폼 | Java 버전 | 사용법 |
|-------------|--------|-----------|--------|
| **enigmatica_10** | NeoForge | 21 | `./modpack_selector.sh enigmatica_10` |
| **prominence_2** | Fabric | 17 | `./modpack_selector.sh prominence_2` |
| **all_the_mods_9** | NeoForge | 21 | `./modpack_selector.sh all_the_mods_9` |
| **vault_hunters** | Fabric | 17 | `./modpack_selector.sh vault_hunters` |

### 🚀 자동 모드팩 감지
- ✅ **Java 버전 자동 선택** (17/21 지원)
- ✅ **플랫폼 자동 매칭** (NeoForge/Fabric)
- ✅ **모드팩 폴더 자동 감지**
- ✅ **기존 JAR 충돌 방지**

**📖 상세 가이드**: [다중 Java 버전 지원 가이드](MULTI_JAVA_GUIDE.md)

## 🛠️ 개발 환경

### 요구사항
- **Java**: OpenJDK 17+
- **Python**: 3.9+
- **Minecraft**: 1.21.1 (NeoForge)
- **Gradle**: 8.0+

### 빌드
```bash
# 🚀 모든 Java 버전 모드 빌드 (권장)
./build_all_mods_multi_java.sh

# 🎯 특정 모드팩용 설치
./modpack_selector.sh prominence_2  # Java 17 Fabric
./modpack_selector.sh enigmatica_10 # Java 21 NeoForge

# 백엔드 테스트
cd backend
python -m pytest
```

## 📊 성능 지표

- **AI 응답 시간**: 1-3초 (Gemini 2.5 Pro)
- **웹검색 지원**: 실시간 Google 검색
- **메모리 사용량**: 최적화된 단일 앱 구조
- **서버 호환성**: 모든 NeoForge 서버 지원

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🔗 링크

- [GitHub 저장소](https://github.com/namepix/minecraft-modpack-ai)
- [플러그인 버전](https://github.com/namepix/minecraft-modpack-ai/tree/plugin-version)
- [이슈 리포트](https://github.com/namepix/minecraft-modpack-ai/issues)
- [릴리스](https://github.com/namepix/minecraft-modpack-ai/releases)

---

**⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!**