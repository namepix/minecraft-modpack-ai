# 🎯 완전한 RAG 시스템 사용 가이드

수동 모드팩 선택 + RAG 우선 + 실패 알림 시스템 완전 가이드

## 🚀 빠른 시작 (5분 완료)

### 1. GCP 설정 (선택사항 - 더 정확한 검색)
```bash
# GCP RAG 설치
./install_gcp_rag.sh

# .env 파일 설정
GCP_RAG_ENABLED=true
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### 2. 백엔드 시작
```bash
python app.py

# 출력 확인:
# ✅ GCP RAG 활성화됨 - 모드팩별 벡터 검색 가능
# 📦 등록된 모드팩: 0개
```

### 3. 모드팩 분석 (수동 선택)
```bash
# 대화형 모드팩 스캔 & 선택
python modpack_manager.py

# 또는 직접 지정
curl -X POST http://localhost:5000/gcp-rag/build \
  -H "Content-Type: application/json" \
  -d '{"modpack_name": "enigmatica_6", "modpack_version": "1.0.0", "modpack_path": "/home/user/enigmatica_6"}'
```

### 4. 게임 내 테스트
```
/ai 철 블록은 어떻게 만들어?    # RAG + 웹검색
/modpackai rag test iron block  # 검색 결과 직접 확인
```

## 📋 모드팩 관리 시스템

### 🔍 **자동 모드팩 스캔**
```bash
python modpack_manager.py
```

**출력 예시:**
```
📦 발견된 모드팩 목록 (3개):
================================================================================
번호   모드팩 이름               버전      모드수   크기(MB)   분석가능
--------------------------------------------------------------------------------
1     enigmatica_6             1.11.0    285      1250      ✅
2     atm10                    1.0.5     180      890       ✅  
3     beyond_depth             2.1.0     95       520       ✅
--------------------------------------------------------------------------------

분석할 모드팩 번호를 선택하세요 (1-3, 0=취소): 1

🔨 모드팩 분석 시작: enigmatica_6
📂 경로: /home/user/enigmatica_6
📊 모드 수: 285개
💾 크기: 1250MB
⏱️ 예상 소요 시간: 9.5분
💰 예상 비용: ~$0.125
계속 진행하시겠습니까? (y/N): y

✅ 인덱스 구축 성공!
📊 처리된 문서 수: 1450
📈 통계: {"recipes": 650, "mods": 285, "kubejs": 515}
```

### 🎮 **게임 내 관리**
```
/modpackai rag status      # RAG 시스템 상태
/modpackai rag list        # 등록된 모드팩 목록
/modpackai rag build /path # 새 모드팩 분석
/modpackai rag test query  # 검색 결과 확인
```

**출력 예시:**
```
[16:30:15] [RAG 시스템 상태]
- GCP RAG: §a활성화됨
- 로컬 RAG: §a활성화됨  
- GCP 프로젝트: modpack-ai-2024-123456

[16:30:20] [등록된 모드팩 목록 (2개)]
1. enigmatica_6 v1.11.0 (1450개 문서)
2. atm10 v1.0.5 (980개 문서)

[16:30:25] [RAG 검색 결과: 3개]
1. [0.89] (recipe) Shaped recipe for iron_block x1: keys={'I': 'iron_ingot'}
2. [0.76] (kubejs) kubejs script: iron_variants.js => 철 관련 아이템들...
3. [0.72] (mod) Installed mod jar: thermal_expansion-1.21.1-11.0.2.jar
```

## 🤖 향상된 AI 채팅 시스템

### 📊 **RAG 우선 + 실패 알림**
```
질문: "철 블록 만들기"

✅ 성공 시:
[AI] 철 블록을 만들려면 철 주괴 9개를 3x3 제작대에...
(RAG: 3개 문서 검색됨, 384자 사용됨)

⚠️ RAG 실패 시:  
[AI] ⚠️ 모드팩 데이터 없음 - 웹검색으로 답변드립니다.
철 블록은 일반적으로 철 주괴 9개를 3x3로...
(RAG 실패 이유: 'enigmatica_6 v1.11.0' 모드팩 데이터 없음)
```

### 🔍 **실시간 디버그 정보**
```json
{
  "rag": {
    "system_used": "gcp_rag",           // 실제 사용된 시스템
    "success": true,                    // RAG 성공 여부  
    "fallback_reason": null,            // 실패 시 이유
    "hits": 3,                         // 검색된 문서 수
    "used_chars": 384,                 // 사용된 문자수
    "debug_info": {
      "gcp_rag": {
        "used": true,
        "results_count": 3,
        "results": [...]                // 실제 검색 결과
      }
    }
  }
}
```

## 🎛️ 시스템 제어

### 🔧 **RAG 시스템 우선순위**
```
1순위: GCP RAG (모드팩별 전용)
  ↓ 실패 시
2순위: 로컬 RAG (범용)
  ↓ 실패 시  
3순위: 웹검색만 사용 (명확한 알림)
```

### ⚙️ **설정 파일 (.env)**
```env
# RAG 우선순위 제어
GCP_RAG_ENABLED=true              # GCP RAG 사용 여부
RAG_TOP_K=5                       # 검색할 문서 수
RAG_SNIPPET_MAX_CHARS=500         # 문서당 최대 문자수
RAG_TOTAL_MAX_CHARS=1500          # 전체 RAG 텍스트 제한

# AI 모델 설정
GOOGLE_API_KEY=your-key           # Gemini (웹검색)
GEMINI_WEBSEARCH_ENABLED=true     # 웹검색 사용
```

### 📊 **상태 확인**
```bash
# 백엔드 상태
curl http://localhost:5000/gcp-rag/status

# 응답:
{
  "gcp_rag_enabled": true,
  "gcp_rag_available": true, 
  "project_id": "modpack-ai-2024-123456",
  "local_rag_enabled": true
}
```

## 💡 실제 사용 시나리오

### 시나리오 1: 새 서버 시작
```bash
# 1. 백엔드 시작
python app.py

# 2. 모드팩 스캔 & 선택
python modpack_manager.py
# → "enigmatica_6" 선택 → 9분 분석

# 3. 게임에서 테스트  
/ai thermal expansion는 뭐야?
# → ✅ RAG: 3개 문서 + 웹검색으로 정확한 답변

# 4. 추가 모드팩 분석 (나중에)
python modpack_manager.py
# → "atm10" 선택 → 6분 분석
```

### 시나리오 2: RAG 없이 시작 (빠른 테스트)
```bash
# .env에서 비활성화
GCP_RAG_ENABLED=false

# 게임에서 질문
/ai iron block recipe
# → ⚠️ RAG 시스템 비활성화됨 - 웹검색만 사용
# → 여전히 정확한 답변, 단 모드팩 특화 정보 없음
```

### 시나리오 3: 문제 해결
```bash
# RAG 검색 결과가 이상할 때
/modpackai rag test iron block
# → 실제 검색된 문서들 확인

# 모드팩 재분석이 필요할 때
python modpack_manager.py
# → 메뉴 3 선택 → 기존 인덱스 삭제
# → 메뉴 1 선택 → 재분석
```

## 🚨 문제 해결

### ❌ "RAG 시스템 비활성화"
```bash
# 해결책 1: GCP 설정 확인
curl http://localhost:5000/gcp-rag/status
# → gcp_rag_available: false

# 해결책 2: 환경변수 확인  
cat .env | grep GCP
# → GCP_RAG_ENABLED=true
# → GCP_PROJECT_ID=실제_프로젝트_ID
```

### ❌ "모드팩 데이터 없음"
```bash
# 해결책: 모드팩 등록 확인
curl http://localhost:5000/gcp-rag/modpacks
# → 빈 목록이면 분석 필요

python modpack_manager.py
# → 원하는 모드팩 분석
```

### ❌ "검색 결과 없음"
```bash
# 해결책: 검색 테스트
/modpackai rag test your_query
# → 실제 검색되는 문서들 확인
# → 검색어 조정 필요할 수 있음
```

## 📈 성능 최적화

### 💰 **비용 절약**
- **선택적 분석**: 필요한 모드팩 1-2개만
- **토큰 제한**: 1500자로 제한 (변경 가능)
- **검색 품질**: 임계값 0.6-0.8 조정

### ⚡ **응답 속도**
- **GCP RAG**: ~2-3초 (정확성 높음)
- **로컬 RAG**: ~0.5초 (빠름)  
- **웹검색**: ~1-2초 (최신 정보)

### 🎯 **정확성 향상**
- **모드팩별 분리**: 각 모드팩 전용 인덱스
- **다단계 폴백**: GCP → 로컬 → 웹검색
- **실시간 확인**: 검색 결과 직접 확인

## 🔄 롤백 & 제거

### 📂 **간단한 비활성화**
```bash
# .env 파일만 수정
GCP_RAG_ENABLED=false
# → 로컬 RAG + 웹검색으로 자동 폴백
```

### 🗑️ **완전 제거**
```bash
./uninstall_gcp_rag.sh
# → 파일, 패키지, 환경변수 모두 제거
```

---

**🎉 이제 완벽한 RAG 시스템을 사용할 준비가 완료되었습니다!**

- ✅ 수동 모드팩 선택으로 비용/시간 절약
- ✅ RAG 우선 사용으로 정확한 답변  
- ✅ 실패 시 명확한 알림으로 투명성
- ✅ 게임 내 관리 도구로 편의성