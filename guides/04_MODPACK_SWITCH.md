# 🔄 모드팩 변경 가이드

## 📋 개요

이 가이드는 마인크래프트 AI 시스템에서 모드팩을 변경하고 관리하는 방법을 설명합니다.
현재 시스템은 간소화된 구조로 되어 있어 설정 파일 수정을 통해 쉽게 모드팩을 변경할 수 있습니다.

## 🎯 모드팩 변경 방법

### 1. 설정 파일 기반 변경 (권장)

**Windows:**
```cmd
# .env 파일 편집
notepad .env
```

**Linux:**
```bash
# .env 파일 편집
nano .env
```

**설정 내용 수정:**
```env
# 현재 모드팩 정보
CURRENT_MODPACK_NAME=enigmatica_10
CURRENT_MODPACK_VERSION=1.0.0

# 백엔드 서버 설정
PORT=5000
DEBUG=false
```

### 2. 스크립트를 통한 변경

**modpack_switch.sh 스크립트 사용:**

**기본 사용법:**
```bash
# Linux
./modpack_switch.sh

# Windows (Git Bash 또는 WSL)
./modpack_switch.sh
```

**특정 모드팩 지정:**
```bash
./modpack_switch.sh FTB_Revelations 3.5.0
./modpack_switch.sh Create_Above_and_Beyond 1.3.1
./modpack_switch.sh All_The_Mods_10 1.0.0
```

## 🛠️ Minecraft 플러그인 설정

### 1. 플러그인 설정 파일

**위치**: `minecraft_plugin/src/main/resources/config.yml`

```yaml
# AI 서버 설정
ai:
  server_url: "http://localhost:5000"
  modpack_name: "enigmatica_10"      # 현재 모드팩명
  modpack_version: "1.0"             # 현재 버전

# AI 어시스턴트 아이템 설정
ai_item:
  material: "BOOK"
  name: "§6§l모드팩 AI 어시스턴트"
```

### 2. 서버별 설정

각 마인크래프트 서버의 `plugins/ModpackAI/config.yml`에서 개별 설정 가능:

```yaml
ai:
  server_url: "http://localhost:5000"
  modpack_name: "create_above_and_beyond"  # 서버별 모드팩
  modpack_version: "1.3.1"
```

## 📊 지원하는 모드팩 목록

### 1. 인기 모드팩들

| 모드팩명 | 설정값 | 최신 버전 | 특징 |
|----------|--------|-----------|------|
| Enigmatica 10 | `enigmatica_10` | 1.0.0 | 종합 모드팩 |
| All The Mods 10 | `atm10` | 1.0.0 | 대용량 모드팩 |
| Create: Above and Beyond | `create_above_and_beyond` | 1.3.1 | Create 중심 |
| FTB Revelation | `ftb_revelation` | 3.5.0 | 안정적인 종합팩 |
| Prominence II | `prominence_2` | 2.6.0 | RPG 요소 |
| Medieval Minecraft | `medieval_mc` | 1.5.1 | 중세 테마 |

### 2. 설정 예시

**Enigmatica 10:**
```env
CURRENT_MODPACK_NAME=enigmatica_10
CURRENT_MODPACK_VERSION=1.0.0
```

**Create: Above and Beyond:**
```env
CURRENT_MODPACK_NAME=create_above_and_beyond  
CURRENT_MODPACK_VERSION=1.3.1
```

**All The Mods 10:**
```env
CURRENT_MODPACK_NAME=atm10
CURRENT_MODPACK_VERSION=1.0.0
```

## 🔧 모드팩별 AI 최적화

### 1. 시스템 프롬프트 맞춤화

`config/config.yaml`에서 모드팩별 프롬프트 설정:

```yaml
ai:
  system_prompt_template: |
    당신은 {modpack_name} v{modpack_version} 전문 AI 어시스턴트입니다.
    
    현재 모드팩의 주요 특징:
    - Create 모드 중심의 기계화 및 자동화
    - 건축 및 장식 요소 강화
    - 탐험과 모험 컨텐츠 풍부
    
    답변 시 이 모드팩의 특성을 고려하여 조언해주세요.
```

### 2. 모드팩별 특화 정보

**Create 중심 모드팩 (Create: Above and Beyond):**
```yaml
ai:
  specialized_knowledge:
    - "Create 모드 기계류 제작 및 사용법"
    - "동력 전달 시스템 (Kinetic Energy)"
    - "자동화 시스템 구축"
    - "장식용 블록과 건축 기법"
```

**Magic 중심 모드팩 (Enigmatica):**
```yaml
ai:
  specialized_knowledge:
    - "마법 모드 (Botania, Blood Magic, Astral Sorcery)"
    - "기술 모드와 마법 모드 연계"
    - "복합 자동화 시스템"
    - "차원 간 이동 및 탐험"
```

## 🎮 게임 내 모드팩 정보 확인

### 1. 명령어로 확인

```
/modpackai current        # 현재 설정된 모드팩 정보
/modpackai version        # AI 시스템 버전 및 모드팩 정보
```

### 2. GUI에서 확인

AI 채팅 창을 열면 상단에 현재 모드팩 정보가 표시됩니다:
```
🤖 모드팩 AI 어시스턴트 - Enigmatica 10 v1.0.0
```

## 📝 모드팩 변경 체크리스트

### 1. 변경 전 준비

- [ ] 현재 모드팩 백업 (선택사항)
- [ ] 새 모드팩의 버전 정보 확인
- [ ] AI 시스템 서비스 중지

### 2. 설정 변경

- [ ] `.env` 파일에서 모드팩 정보 업데이트
- [ ] `config/config.yaml`에서 특화 설정 적용
- [ ] 플러그인 `config.yml` 업데이트

### 3. 변경 후 확인

- [ ] 백엔드 서비스 재시작
- [ ] 마인크래프트 서버 플러그인 리로드
- [ ] `/modpackai current`로 변경 확인
- [ ] AI 응답 테스트

## 🚨 문제 해결

### 1. 모드팩 변경이 반영되지 않을 때

**확인사항:**
1. `.env` 파일의 변경사항 저장 여부
2. 백엔드 서비스 재시작 여부
3. 플러그인 설정 파일 업데이트 여부

**해결 방법:**
```bash
# Windows
cd backend
python app.py  # 수동 재시작

# Linux
sudo systemctl restart mc-ai-backend
sudo systemctl status mc-ai-backend
```

### 2. AI가 이전 모드팩 정보로 답변할 때

**원인**: 설정이 제대로 반영되지 않음

**해결 방법:**
1. 백엔드 완전 재시작
2. 플러그인 리로드: `/reload confirm`
3. 브라우저에서 `http://localhost:5000/health` 확인

### 3. 새 모드팩 정보를 AI가 모를 때

**해결 방법:**
- Gemini 2.5 Pro의 웹검색 기능이 자동으로 최신 정보 검색
- 직접 질문: `/ai 이 모드팩의 주요 모드와 특징을 알려줘`

## 📊 성능 최적화

### 1. 모드팩별 응답 최적화

**대용량 모드팩 (ATM, Enigmatica):**
```yaml
ai:
  max_tokens: 1500  # 더 자세한 답변
  temperature: 0.6  # 정확성 중시
```

**특화 모드팩 (Create, Botania):**
```yaml
ai:
  max_tokens: 1000  # 간결한 답변
  temperature: 0.8  # 창의적 답변
```

### 2. 캐싱 최적화

```yaml
cost_optimization:
  # 모드팩별 캐시 설정
  cache_duration_hours: 
    general_questions: 24
    recipe_queries: 12
    modpack_specific: 6
```

## 🔮 고급 설정

### 1. 다중 모드팩 지원

하나의 AI 시스템으로 여러 모드팩 서버 지원:

```yaml
# 서버별 설정
servers:
  server1:
    modpack_name: "enigmatica_10"
    port: 25565
  server2:  
    modpack_name: "create_above_and_beyond"
    port: 25566
```

### 2. 자동 모드팩 감지

마인크래프트 서버의 모드 목록을 읽어서 자동으로 모드팩 식별:

```python
# 향후 구현 예정 기능
def detect_modpack_from_mods():
    """설치된 모드 목록으로 모드팩 자동 식별"""
    pass
```

## 📚 참고 자료

### 1. 모드팩 공식 사이트

- **CurseForge**: https://www.curseforge.com/minecraft/modpacks
- **FTB App**: https://www.feed-the-beast.com/
- **Modrinth**: https://modrinth.com/modpacks

### 2. 모드팩 버전 확인

```bash
# 모드팩 매니페스트 파일에서 버전 정보 추출
# manifest.json 또는 modpack.json 파일 확인
```

### 3. 커뮤니티 가이드

- **Reddit**: r/feedthebeast
- **Discord**: 각 모드팩별 공식 디스코드
- **Wiki**: 모드팩별 위키 페이지

---

**🎮 모드팩 변경을 통해 더 다양한 AI 어시스턴트 경험을 즐기세요!** 🚀