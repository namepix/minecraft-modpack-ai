# 테스트 가이드

이 디렉토리는 마인크래프트 모드팩 AI 프로젝트의 테스트 코드를 포함합니다.

## 📁 테스트 파일 구조

```
tests/
├── conftest.py              # 공통 fixture 및 설정
├── test_app_integration.py  # Flask 앱 통합 테스트
├── test_chat_manager.py     # 채팅 관리 테스트
├── test_cli_scripts.py      # CLI 스크립트 테스트
├── test_hybrid_ai_model.py  # AI 모델 테스트
├── test_language_mapper.py  # 언어 매핑 테스트
├── test_modpack_analyzer.py # 모드팩 분석 테스트
├── test_recipe_manager.py   # 레시피 관리 테스트
├── test_rag_manager.py      # RAG 관리 테스트
├── test_utils.py           # 유틸리티 함수 테스트
├── test_web_search.py      # 웹검색 매니저 테스트
└── README.md               # 이 파일
```

## 🚀 테스트 실행

### 기본 실행
```bash
cd backend
python run_tests.py
```

### 특정 테스트 타입 실행
```bash
# 단위 테스트만
python run_tests.py unit

# 통합 테스트만
python run_tests.py integration

# 빠른 테스트 (slow 제외)
python run_tests.py fast

# 웹 관련 테스트만
python run_tests.py web
```

### pytest 직접 실행
```bash
# 모든 테스트
pytest tests/

# 특정 파일
pytest tests/test_utils.py

# 특정 테스트 함수
pytest tests/test_utils.py::TestConfig::test_initialization

# 마커로 필터링
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### 커버리지와 함께 실행
```bash
# 커버리지 보고서 생성
pytest --cov=backend --cov-report=html:htmlcov tests/

# 터미널에서 커버리지 확인
pytest --cov=backend --cov-report=term-missing tests/
```

## 🏷️ 테스트 마커

- `@pytest.mark.unit` - 단위 테스트
- `@pytest.mark.integration` - 통합 테스트
- `@pytest.mark.slow` - 느린 테스트
- `@pytest.mark.web` - 웹 관련 테스트

## 📊 테스트 커버리지

현재 테스트 커버리지는 다음과 같습니다:

- **유틸리티 함수**: 95%+
- **채팅 관리**: 90%+
- **레시피 관리**: 85%+
- **AI 모델**: 80%+
- **모드팩 분석**: 85%+
- **웹검색**: 90%+
- **통합 테스트**: 75%+

## 🔧 테스트 설정

### pytest.ini 설정
- 테스트 경로: `tests/`
- 파일 패턴: `test_*.py`
- 클래스 패턴: `Test*`
- 함수 패턴: `test_*`
- 커버리지 자동 생성
- 경고 필터링

### conftest.py 공통 fixture
- `temp_db`: 임시 데이터베이스
- `mock_env_vars`: 환경 변수 모킹
- `mock_rag_manager`: RAG 매니저 모킹
- `mock_ai_clients`: AI 클라이언트 모킹
- `sample_modpack_data`: 샘플 모드팩 데이터
- `sample_chat_history`: 샘플 채팅 기록

## 📝 테스트 작성 가이드

### 1. 테스트 클래스 구조
```python
class TestClassName:
    """클래스 설명"""
    
    @pytest.fixture
    def fixture_name(self):
        """fixture 설명"""
        return fixture_value
    
    def test_function_name(self, fixture_name):
        """테스트 설명"""
        # Given (준비)
        input_data = "test"
        
        # When (실행)
        result = function_to_test(input_data)
        
        # Then (검증)
        assert result == expected_value
```

### 2. Mock 사용
```python
@patch('module.function')
def test_with_mock(self, mock_function):
    mock_function.return_value = "mocked_result"
    # 테스트 로직
```

### 3. 예외 테스트
```python
def test_exception_handling(self):
    with pytest.raises(ValueError, match="error message"):
        function_that_raises_exception()
```

### 4. 파라미터화된 테스트
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_parameterized(self, input, expected):
    assert function(input) == expected
```

## 🐛 문제 해결

### Import 오류
```bash
# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 의존성 문제
```bash
# 테스트 의존성 설치
pip install -r requirements.txt
```

### 데이터베이스 오류
- 테스트는 임시 데이터베이스를 사용합니다
- 실제 데이터베이스에 영향을 주지 않습니다

### 네트워크 오류
- 웹 관련 테스트는 mock을 사용합니다
- 실제 네트워크 호출이 필요하면 `@pytest.mark.web` 마커를 사용하세요

## 📈 성능 최적화

### 병렬 실행
```bash
pytest -n auto tests/
```

### 캐시 사용
```bash
pytest --cache-clear  # 캐시 초기화
```

### 특정 테스트만 실행
```bash
pytest -k "test_name" tests/
```

## 🔍 코드 품질

### 린팅
```bash
flake8 backend/
```

### 타입 체크
```bash
mypy backend/
```

### 포맷팅
```bash
black backend/
```

## 📚 추가 리소스

- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest-cov 문서](https://pytest-cov.readthedocs.io/)
- [unittest.mock 문서](https://docs.python.org/3/library/unittest.mock.html) 