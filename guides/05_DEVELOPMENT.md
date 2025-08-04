# 🛠️ 개발자 가이드

## 📋 개요

이 가이드는 프로젝트 개발, 디버깅, 수정을 위한 상세한 정보를 제공합니다.

## 🏗️ 프로젝트 구조

```
📁 프로젝트 구조
├── 📁 backend/                    # Python Flask 백엔드
│   ├── 📁 models/                 # AI 모델 관련
│   │   ├── hybrid_ai_model.py    # 하이브리드 AI 모델
│   │   └── ai_model.py           # 기본 AI 모델 (레거시)
│   ├── 📁 database/              # 데이터베이스 관리
│   │   ├── chat_manager.py       # 채팅 기록 관리
│   │   └── recipe_manager.py     # 제작법 데이터 관리
│   ├── 📁 utils/                 # 유틸리티 함수들
│   │   ├── logger.py             # 중앙화된 로깅 시스템
│   │   ├── config.py             # 설정 관리 시스템
│   │   ├── language_mapper.py    # 언어 매핑
│   │   ├── rag_manager.py        # RAG 시스템
│   │   └── web_search.py         # 웹 검색 (레거시)
│   ├── 📁 modpack_parser/        # 모드팩 파싱
│   │   └── modpack_analyzer.py   # 모드팩 분석기
│   ├── app.py                    # Flask 메인 애플리케이션
│   └── requirements.txt          # Python 의존성
├── 📁 minecraft_plugin/          # Java Spigot 플러그인
│   ├── 📁 src/main/java/com/modpackai/
│   │   ├── 📁 managers/          # 매니저 클래스들
│   │   ├── 📁 gui/              # GUI 관련
│   │   ├── 📁 commands/         # 명령어 처리
│   │   ├── 📁 listeners/        # 이벤트 리스너
│   │   └── ModpackAIPlugin.java # 메인 플러그인 클래스
│   └── pom.xml                   # Maven 빌드 설정
├── 📁 tests/                     # 테스트 코드
├── 📁 guides/                    # 문서
├── dev_tools.py                  # 개발 도구 스크립트
└── 📄 스크립트 파일들            # 설치/관리 스크립트
```

## 🚀 개발 환경 설정

### **1. Python 환경 설정**
```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r backend/requirements.txt

# 개발 도구 설치 (선택사항)
pip install pytest flake8 black mypy
```

### **2. Java 환경 설정**
```bash
# Java 17 이상 설치 확인
java -version

# Maven 설치 확인
mvn -version

# 플러그인 빌드
cd minecraft_plugin
mvn clean package
```

### **3. IDE 설정**
- **VS Code**: Python, Java 확장 설치
- **IntelliJ IDEA**: Python, Java 플러그인 활성화
- **PyCharm**: Java 플러그인 설치

## 🧪 테스트 실행

### **단위 테스트**
```bash
# 전체 테스트 실행
python dev_tools.py test

# 특정 테스트 파일 실행
python -m pytest tests/test_ai_model.py -v

# 커버리지와 함께 실행
python -m pytest tests/ --cov=backend --cov-report=html
```

### **통합 테스트**
```bash
# 백엔드 서버 시작
cd backend
python app.py

# API 테스트
curl http://localhost:5000/health
curl http://localhost:5000/api/models
```

## 🔍 디버깅 도구

### **1. 개발 도구 스크립트**
```bash
# 전체 검사
python dev_tools.py all

# 개별 검사
python dev_tools.py test      # 테스트 실행
python dev_tools.py quality   # 코드 품질 검사
python dev_tools.py docs      # 문서 생성
python dev_tools.py deps      # 의존성 검사
python dev_tools.py config    # 설정 유효성 검사
python dev_tools.py lint      # 린터 실행
python dev_tools.py report    # 디버그 리포트 생성
```

### **2. 로깅 시스템**
```python
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# 로그 레벨별 사용
logger.debug("디버그 정보")
logger.info("일반 정보")
logger.warning("경고")
logger.error("오류")
logger.critical("심각한 오류")
```

### **3. 설정 관리**
```python
from backend.utils.config import config

# 설정 값 가져오기
api_key = config.get('openai_api_key')
debug_mode = config.get('debug', False)

# 설정 값 설정하기
config.set('custom_setting', 'value')

# 설정 유효성 검사
errors = config.validate()
if errors:
    print("설정 오류:", errors)
```

## 🔧 코드 품질 관리

### **1. 코드 스타일 검사**
```bash
# flake8으로 코드 스타일 검사
flake8 backend/

# black으로 코드 포맷팅
black backend/

# mypy로 타입 검사
mypy backend/
```

### **2. 코드 리뷰 체크리스트**
- [ ] 함수와 클래스에 docstring 작성
- [ ] 변수명이 명확하고 의미있게 작성
- [ ] 예외 처리 적절히 구현
- [ ] 로깅 적절히 추가
- [ ] 테스트 코드 작성
- [ ] 타입 힌트 사용

## 🐛 일반적인 디버깅 시나리오

### **1. AI 모델 응답 오류**
```python
# 디버깅 단계
1. API 키 확인
2. 네트워크 연결 확인
3. 요청/응답 로그 확인
4. 모델 설정 확인

# 로그 확인
tail -f ~/minecraft-ai-backend/logs/app.log
```

### **2. 데이터베이스 오류**
```python
# 디버깅 단계
1. 데이터베이스 파일 존재 확인
2. 권한 확인
3. SQL 쿼리 로그 확인
4. 스키마 변경 확인

# 데이터베이스 직접 확인
sqlite3 ~/minecraft-ai-backend/minecraft_ai.db
.tables
.schema recipes
```

### **3. 플러그인 로드 오류**
```bash
# 디버깅 단계
1. Java 버전 확인
2. 플러그인 파일 존재 확인
3. 서버 로그 확인
4. 의존성 확인

# 서버 로그 확인
tail -f ~/enigmatica_10/logs/latest.log
```

## 📊 성능 모니터링

### **1. 시스템 리소스 모니터링**
```bash
# CPU, 메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 연결
netstat -tlnp | grep 5000
```

### **2. 애플리케이션 성능 모니터링**
```python
import time
import logging

# 함수 실행 시간 측정
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} 실행 시간: {end_time - start_time:.2f}초")
        return result
    return wrapper
```

## 🔄 코드 수정 워크플로우

### **1. 기능 추가**
```bash
# 1. 브랜치 생성
git checkout -b feature/new-feature

# 2. 코드 작성
# 3. 테스트 작성
python dev_tools.py test

# 4. 코드 품질 검사
python dev_tools.py quality

# 5. 커밋 및 푸시
git add .
git commit -m "feat: 새로운 기능 추가"
git push origin feature/new-feature
```

### **2. 버그 수정**
```bash
# 1. 버그 재현
# 2. 로그 분석
python dev_tools.py report

# 3. 수정 및 테스트
python dev_tools.py test

# 4. 커밋
git commit -m "fix: 버그 수정"
```

## 📚 API 문서

### **API 엔드포인트 목록**
```bash
# API 문서 생성
python dev_tools.py docs

# 생성된 문서 확인
cat api_documentation.json
```

### **주요 API 엔드포인트**
- `GET /health`: 서버 상태 확인
- `POST /api/chat`: AI 채팅
- `GET /api/recipe/<item_name>`: 제작법 조회
- `POST /api/modpack/switch`: 모드팩 변경
- `GET /api/models`: 사용 가능한 AI 모델
- `POST /api/models/switch`: AI 모델 전환

## 🚨 문제 해결

### **1. 일반적인 오류**
```bash
# ImportError: No module named 'xxx'
pip install -r backend/requirements.txt

# Permission denied
sudo chmod +x *.sh

# Port already in use
sudo lsof -i :5000
sudo kill -9 <PID>
```

### **2. 성능 문제**
```bash
# 메모리 사용량 확인
free -h

# CPU 사용량 확인
top

# 디스크 I/O 확인
iotop
```

### **3. 네트워크 문제**
```bash
# 포트 확인
netstat -tlnp | grep 5000

# 방화벽 확인
sudo ufw status

# 연결 테스트
curl http://localhost:5000/health
```

## 📝 개발 팁

### **1. 효율적인 개발**
- **로깅 활용**: 문제 발생 시 로그를 먼저 확인
- **단위 테스트**: 새로운 기능 추가 시 테스트 코드 작성
- **설정 관리**: 환경별 설정 분리
- **문서화**: 코드 변경 시 문서 업데이트

### **2. 코드 품질**
- **함수 분리**: 하나의 함수는 하나의 역할만
- **예외 처리**: 적절한 예외 처리로 안정성 확보
- **타입 힌트**: 코드 가독성과 IDE 지원 향상
- **상수 분리**: 매직 넘버 제거

### **3. 디버깅 전략**
- **단계별 확인**: 문제를 작은 단위로 분해
- **로그 분석**: 시스템 로그와 애플리케이션 로그 확인
- **재현 가능**: 버그를 재현할 수 있는 환경 구성
- **문서화**: 해결한 문제는 문서로 기록

---

**🛠️ 이제 효율적으로 개발하고 디버깅할 수 있습니다!** 🚀 