# 🎮 마인크래프트 모드팩 AI 시스템

마인크래프트 모드팩 전문 AI 어시스턴트로, 게임 내에서 모드팩 관련 질문에 답변하고 제작법을 제공합니다.

## ✨ 주요 기능

- 🤖 **다중 AI 모델 지원**: Gemini Pro (메인, 웹검색), GPT, Claude (백업)
- 🎯 **모드팩 전문 지식**: 특정 모드팩에 대한 정확한 정보 제공
- 🛠️ **3x3 제작법 GUI**: 시각적으로 명확한 제작법 표시
- 💬 **채팅 기록**: 플레이어별 대화 기록 저장
- 🌐 **한글/영어 호환**: 아이템명과 질문 모두 한글/영어 사용 가능
- 🔄 **모드팩 자동 변경**: 관리자가 쉽게 모드팩 전환 가능
- 🔍 **RAG 시스템**: 벡터 검색을 통한 정확한 정보 제공

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Minecraft     │ ◄────────────► │   AI Backend    │
│   Plugin        │                │   (Flask)       │
│                 │                │                 │
│  - GUI System   │                │  - AI Models    │
│  - Commands     │                │  - Database     │
│  - Item Events  │                │  - RAG System   │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   Minecraft     │                │   GCP Services  │
│   Server        │                │                 │
│                 │                │  - Cloud Storage│
│  - Modpack      │                │  - Vector DB    │
│  - Players      │                │  - Embeddings   │
└─────────────────┘                └─────────────────┘
```

## 🚀 빠른 시작

### 1. 설치
```bash
git clone https://github.com/your-username/minecraft-modpack-ai.git
cd minecraft-modpack-ai
chmod +x install.sh
./install.sh
```

### 2. API 키 설정 (Gemini Pro 우선)
```bash
nano $HOME/minecraft-ai-backend/.env
# 🌟 GOOGLE_API_KEY=your-key (필수, GCP 크레딧 사용)
# 📖 OPENAI_API_KEY=your-key (선택, 백업용)
# 📖 ANTHROPIC_API_KEY=your-key (선택, 백업용)
```

### 3. 서비스 시작
```bash
sudo systemctl start mc-ai-backend
sudo systemctl enable mc-ai-backend
```

### 4. 게임 내 사용
```
/ai 철 블록은 어떻게 만들어?    # AI에게 바로 질문
/modpackai chat                 # AI GUI 열기
/modpackai recipe 다이아몬드     # 제작법 조회
/modpackai models               # AI 모델 선택
```

**💡 팁**: AI 아이템을 우클릭하면 바로 채팅창이 열립니다!

## 📚 상세 가이드

### 📖 [가이드 모음](guides/)
- [관리자를 위한 AI 모드 추가 가이드](guides/01_ADMIN_SETUP.md)
- [시스템 전체 구조 가이드](guides/02_SYSTEM_OVERVIEW.md)
- [게임 내 AI 모드 명령어 사용법](guides/03_GAME_COMMANDS.md)
- [관리자를 위한 모드팩 변경 가이드](guides/04_MODPACK_SWITCH.md)

## 🎮 게임 내 명령어

| 명령어 | 설명 | 권한 | 예시 |
|--------|------|------|------|
| `/ai <질문>` | AI에게 바로 질문 | 일반 | `/ai 철 블록 만드는 법` |
| `/modpackai chat` | AI 채팅 GUI 열기 | 일반 | `/modpackai chat` |
| `/modpackai recipe <아이템>` | 제작법 조회 | 일반 | `/modpackai recipe 다이아몬드` |
| `/modpackai models` | AI 모델 선택 | 일반 | `/modpackai models` |
| `/modpackai current` | 현재 AI 모델 정보 | 일반 | `/modpackai current` |
| `/modpackai switch <모드팩>` | 모드팩 변경 | 관리자 | `/modpackai switch FTB` |
| `/modpackai help` | 도움말 보기 | 일반 | `/modpackai help` |

## 🤖 지원하는 AI 모델

| 모델 | 제공업체 | 특징 | 비용 |
|------|----------|------|------|
| GPT-3.5 Turbo | OpenAI | 빠르고 저렴 | 유료 |
| GPT-4 | OpenAI | 정확도 높음 | 유료 |
| Claude 3 Haiku | Anthropic | 빠르고 효율적 | 유료 |
| Claude 3 Sonnet | Anthropic | 균형잡힌 성능 | 유료 |
| Gemini Pro | Google | 무료 크레딧 제공 | 무료 |

## 🔧 관리자 도구

### CLI 모드팩 변경 스크립트
```bash
# 설정 파일에서 모드팩 정보 읽어서 분석
modpack_switch

# 특정 모드팩 분석 (버전 자동 추출)
modpack_switch CreateModpack

# 특정 모드팩과 버전으로 분석
modpack_switch FTBRevelation 1.0.0

# 사용 가능한 모드팩 목록
modpack_switch --list

# 도움말
modpack_switch --help
```

### 시스템 모니터링
```bash
# 시스템 상태 확인
mc-ai-monitor

# 상세 로그 확인
mc-ai-monitor --log
```

## 📊 시스템 요구사항

- **OS**: Debian 11+ 또는 Ubuntu 20.04+
- **CPU**: 2 vCPU 이상 (권장: 4 vCPU)
- **RAM**: 4GB 이상 (권장: 8GB)
- **Storage**: 20GB 이상 (SSD 권장)
- **Python**: 3.8+
- **Java**: 11+

## 🔒 보안 기능

- **Rate Limiting**: API 요청 제한
- **Input Validation**: 입력 데이터 검증
- **XSS Prevention**: 크로스 사이트 스크립팅 방지
- **UUID 기반 인증**: 플레이어 식별

## 🚨 문제 해결

### 백엔드 서비스 오류
```bash
# 서비스 상태 확인
sudo systemctl status mc-ai-backend

# 로그 확인
sudo journalctl -u mc-ai-backend -f

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

### 플러그인 로드 오류
```bash
# 플러그인 파일 확인
ls -la ~/enigmatica_10/plugins/ModpackAI-1.0.jar
ls -la ~/integrated_MC/plugins/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### API 키 오류
```bash
# 환경 변수 확인
grep API_KEY $HOME/minecraft-ai-backend/.env
```

## 📈 성능 지표

- **응답 시간**: 1-6초 (모델에 따라)
- **정확도**: 80-95% (모델에 따라)
- **동시 사용자**: 권장 5-8명, 최대 10-15명
- **제작법 정보**: 95%+ 정확도

## 🔮 향후 개발 계획

- [ ] 더 많은 AI 모델 지원
- [ ] 음성 인식 기능 추가
- [ ] 모바일 앱 개발
- [ ] 실시간 번역 기능
- [ ] 클라우드 네이티브 아키텍처

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. [가이드 모음](guides/) 참조
2. 시스템 로그 확인
3. API 키 설정 확인
4. 네트워크 연결 상태 확인

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**🎮 즐거운 모드팩 플레이 되세요!** 🚀 