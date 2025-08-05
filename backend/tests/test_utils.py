"""
유틸리티 함수 테스트
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from backend.utils.config import Config
from backend.utils.logger import setup_logger
from backend.utils.validators import validate_uuid, validate_message_length, sanitize_input
from backend.utils.helpers import extract_version_from_filename, format_recipe_display


class TestConfig:
    """설정 관리 테스트 클래스"""
    
    @pytest.fixture
    def config(self):
        """설정 인스턴스 생성"""
        return Config()
    
    def test_config_initialization(self, config):
        """설정 초기화 테스트"""
        assert config is not None
        assert hasattr(config, 'get')
        assert hasattr(config, 'set')
        assert hasattr(config, 'load_from_env')
    
    def test_config_get_default_values(self, config):
        """설정 기본값 조회 테스트"""
        # 기본값이 설정되어 있는지 확인
        assert config.get('FLASK_PORT', 5000) == 5000
        assert config.get('DEBUG', False) == False
        assert config.get('SECRET_KEY', 'default') == 'default'
    
    def test_config_set_and_get(self, config):
        """설정 설정 및 조회 테스트"""
        config.set('TEST_KEY', 'test_value')
        
        assert config.get('TEST_KEY') == 'test_value'
    
    def test_config_load_from_env(self, config):
        """환경 변수에서 설정 로드 테스트"""
        with patch.dict(os.environ, {
            'TEST_ENV_VAR': 'test_value',
            'FLASK_PORT': '8080',
            'DEBUG': 'true'
        }):
            config.load_from_env()
            
            assert config.get('TEST_ENV_VAR') == 'test_value'
            assert config.get('FLASK_PORT') == '8080'
            assert config.get('DEBUG') == 'true'
    
    def test_config_get_with_type_conversion(self, config):
        """타입 변환이 있는 설정 조회 테스트"""
        config.set('INT_VALUE', '123')
        config.set('BOOL_VALUE', 'true')
        config.set('FLOAT_VALUE', '3.14')
        
        assert config.get('INT_VALUE', type=int) == 123
        assert config.get('BOOL_VALUE', type=bool) == True
        assert config.get('FLOAT_VALUE', type=float) == 3.14
    
    def test_config_get_nonexistent_key(self, config):
        """존재하지 않는 키 조회 테스트"""
        assert config.get('NONEXISTENT_KEY') is None
        assert config.get('NONEXISTENT_KEY', default='default') == 'default'


class TestLogger:
    """로거 테스트 클래스"""
    
    def test_setup_logger(self):
        """로거 설정 테스트"""
        with patch('logging.basicConfig') as mock_basic_config, \
             patch('logging.getLogger') as mock_get_logger:
            
            logger = setup_logger('test_logger')
            
            assert logger is not None
            mock_basic_config.assert_called_once()
            mock_get_logger.assert_called_once_with('test_logger')
    
    def test_setup_logger_with_file(self):
        """파일 로거 설정 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as f:
            log_file = f.name
        
        try:
            with patch('logging.FileHandler') as mock_file_handler, \
                 patch('logging.Formatter') as mock_formatter:
                
                logger = setup_logger('test_logger', log_file=log_file)
                
                assert logger is not None
                mock_file_handler.assert_called_once_with(log_file)
                mock_formatter.assert_called()
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
    
    def test_setup_logger_with_level(self):
        """레벨이 있는 로거 설정 테스트"""
        with patch('logging.basicConfig') as mock_basic_config:
            logger = setup_logger('test_logger', level='DEBUG')
            
            assert logger is not None
            # DEBUG 레벨이 설정되었는지 확인
            call_args = mock_basic_config.call_args
            assert call_args[1]['level'] == 'DEBUG'


class TestValidators:
    """검증 함수 테스트 클래스"""
    
    def test_validate_uuid_valid(self):
        """유효한 UUID 검증 테스트"""
        valid_uuids = [
            '12345678-1234-1234-1234-123456789012',
            '00000000-0000-0000-0000-000000000000',
            'ffffffff-ffff-ffff-ffff-ffffffffffff'
        ]
        
        for uuid_str in valid_uuids:
            assert validate_uuid(uuid_str) is True
    
    def test_validate_uuid_invalid(self):
        """잘못된 UUID 검증 테스트"""
        invalid_uuids = [
            'invalid-uuid',
            '12345678-1234-1234-1234-12345678901',  # 너무 짧음
            '12345678-1234-1234-1234-1234567890123',  # 너무 김
            '12345678-1234-1234-1234-12345678901g',  # 잘못된 문자
            '',
            None
        ]
        
        for uuid_str in invalid_uuids:
            assert validate_uuid(uuid_str) is False
    
    def test_validate_message_length_valid(self):
        """유효한 메시지 길이 검증 테스트"""
        valid_messages = [
            '안녕하세요',
            'a' * 1000,  # 정확히 1000자
            '테스트 메시지입니다.',
            ''
        ]
        
        for message in valid_messages:
            assert validate_message_length(message, max_length=1000) is True
    
    def test_validate_message_length_invalid(self):
        """잘못된 메시지 길이 검증 테스트"""
        invalid_messages = [
            'a' * 1001,  # 1000자 초과
            'b' * 2000,  # 1000자 초과
            'c' * 5000   # 1000자 초과
        ]
        
        for message in invalid_messages:
            assert validate_message_length(message, max_length=1000) is False
    
    def test_sanitize_input_success(self):
        """입력 정리 성공 테스트"""
        test_inputs = [
            '안녕하세요',
            'Hello World',
            'Test message with numbers 123',
            'Special chars: !@#$%^&*()',
            '한글과 English mixed'
        ]
        
        for input_str in test_inputs:
            sanitized = sanitize_input(input_str)
            assert sanitized == input_str  # 정상적인 입력은 변경되지 않아야 함
    
    def test_sanitize_input_xss_prevention(self):
        """XSS 방지 테스트"""
        malicious_inputs = [
            '<script>alert("XSS")</script>',
            'Hello <img src="x" onerror="alert(1)">',
            'Test <iframe src="javascript:alert(1)"></iframe>',
            'Normal text <script>malicious</script> more text'
        ]
        
        for input_str in malicious_inputs:
            sanitized = sanitize_input(input_str)
            assert '<script>' not in sanitized
            assert 'javascript:' not in sanitized
            assert 'onerror=' not in sanitized
    
    def test_sanitize_input_sql_injection_prevention(self):
        """SQL 인젝션 방지 테스트"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker'); --",
            "Normal text'; DROP TABLE users; --"
        ]
        
        for input_str in malicious_inputs:
            sanitized = sanitize_input(input_str)
            assert "';" not in sanitized
            assert "DROP TABLE" not in sanitized
            assert "INSERT INTO" not in sanitized
    
    def test_sanitize_input_empty_and_none(self):
        """빈 값 및 None 처리 테스트"""
        assert sanitize_input('') == ''
        assert sanitize_input(None) == ''
        assert sanitize_input('   ') == '   '  # 공백은 유지


class TestHelpers:
    """헬퍼 함수 테스트 클래스"""
    
    def test_extract_version_from_filename_success(self):
        """파일명에서 버전 추출 성공 테스트"""
        test_cases = [
            ('TestModpack-1.0.0.zip', '1.0.0'),
            ('MyModpack_v2.1.3.zip', '2.1.3'),
            ('Modpack-3.0.0-beta.zip', '3.0.0'),
            ('Complex-Name-4.2.1-release.zip', '4.2.1'),
            ('Simple_5.0.0.zip', '5.0.0')
        ]
        
        for filename, expected_version in test_cases:
            version = extract_version_from_filename(filename)
            assert version == expected_version
    
    def test_extract_version_from_filename_no_version(self):
        """버전이 없는 파일명 테스트"""
        test_cases = [
            'NoVersion.zip',
            'Modpack.zip',
            'Test-Modpack.zip',
            'simple.zip'
        ]
        
        for filename in test_cases:
            version = extract_version_from_filename(filename)
            assert version == '1.0.0'  # 기본값
    
    def test_extract_version_from_filename_invalid_format(self):
        """잘못된 형식의 파일명 테스트"""
        test_cases = [
            'Test-1.2.3.4.zip',  # 너무 많은 버전 숫자
            'Test-v1.2.zip',     # v 접두사
            'Test-1.2.3-beta.zip',  # 하이픈이 포함된 버전
            'Test_1_2_3.zip'     # 언더스코어로 구분
        ]
        
        for filename in test_cases:
            version = extract_version_from_filename(filename)
            # 일부는 추출 가능, 일부는 기본값
            assert version in ['1.2.3', '1.0.0']
    
    def test_format_recipe_display_success(self):
        """레시피 표시 형식 성공 테스트"""
        test_recipe = {
            'type': 'minecraft:crafting',
            'ingredients': [
                {'item': 'minecraft:dirt', 'count': 1},
                {'item': 'minecraft:stone', 'count': 2}
            ],
            'result': {'item': 'minecraft:test_item', 'count': 1}
        }
        
        formatted = format_recipe_display(test_recipe)
        
        assert 'type' in formatted
        assert 'ingredients' in formatted
        assert 'result' in formatted
        assert formatted['type'] == 'minecraft:crafting'
        assert len(formatted['ingredients']) == 2
        assert formatted['result']['item'] == 'minecraft:test_item'
    
    def test_format_recipe_display_with_missing_fields(self):
        """누락된 필드가 있는 레시피 표시 테스트"""
        incomplete_recipe = {
            'type': 'minecraft:crafting',
            'ingredients': [{'item': 'minecraft:dirt'}]  # count 누락
        }
        
        formatted = format_recipe_display(incomplete_recipe)
        
        assert 'type' in formatted
        assert 'ingredients' in formatted
        assert formatted['ingredients'][0]['count'] == 1  # 기본값 설정
    
    def test_format_recipe_display_empty_recipe(self):
        """빈 레시피 표시 테스트"""
        empty_recipe = {}
        
        formatted = format_recipe_display(empty_recipe)
        
        assert formatted == {}
    
    def test_format_recipe_display_none_recipe(self):
        """None 레시피 표시 테스트"""
        formatted = format_recipe_display(None)
        
        assert formatted == {}


class TestFileUtils:
    """파일 유틸리티 테스트 클래스"""
    
    @pytest.fixture
    def temp_file(self):
        """임시 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"test": "data"}')
            yield f.name
            os.unlink(f.name)
    
    def test_read_json_file_success(self, temp_file):
        """JSON 파일 읽기 성공 테스트"""
        from backend.utils.helpers import read_json_file
        
        data = read_json_file(temp_file)
        
        assert data == {"test": "data"}
    
    def test_read_json_file_not_found(self):
        """존재하지 않는 JSON 파일 읽기 테스트"""
        from backend.utils.helpers import read_json_file
        
        data = read_json_file('nonexistent.json')
        
        assert data == {}
    
    def test_read_json_file_invalid_json(self):
        """잘못된 JSON 파일 읽기 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('invalid json content')
            invalid_file = f.name
        
        try:
            from backend.utils.helpers import read_json_file
            
            data = read_json_file(invalid_file)
            
            assert data == {}
        finally:
            os.unlink(invalid_file)
    
    def test_write_json_file_success(self):
        """JSON 파일 쓰기 성공 테스트"""
        from backend.utils.helpers import write_json_file
        
        test_data = {"key": "value", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            result = write_json_file(temp_file, test_data)
            
            assert result is True
            
            # 파일이 올바르게 쓰여졌는지 확인
            with open(temp_file, 'r') as f:
                written_data = json.load(f)
            
            assert written_data == test_data
        finally:
            os.unlink(temp_file)
    
    def test_write_json_file_permission_error(self):
        """권한 오류가 있는 JSON 파일 쓰기 테스트"""
        from backend.utils.helpers import write_json_file
        
        # 읽기 전용 디렉토리에 쓰기 시도
        result = write_json_file('/root/test.json', {"test": "data"})
        
        assert result is False


class TestNetworkUtils:
    """네트워크 유틸리티 테스트 클래스"""
    
    def test_is_port_available(self):
        """포트 사용 가능 여부 테스트"""
        from backend.utils.helpers import is_port_available
        
        # 일반적으로 사용되지 않는 포트
        assert is_port_available(9999) is True
        
        # 시스템에서 사용 중인 포트 (SSH 등)
        assert is_port_available(22) is False
    
    def test_check_internet_connection(self):
        """인터넷 연결 확인 테스트"""
        from backend.utils.helpers import check_internet_connection
        
        # 인터넷 연결이 있는 환경에서는 True
        result = check_internet_connection()
        assert isinstance(result, bool)
    
    def test_get_local_ip(self):
        """로컬 IP 주소 조회 테스트"""
        from backend.utils.helpers import get_local_ip
        
        ip = get_local_ip()
        
        # IP 주소 형식 확인
        assert isinstance(ip, str)
        assert '.' in ip
        parts = ip.split('.')
        assert len(parts) == 4
        assert all(0 <= int(part) <= 255 for part in parts)


class TestTimeUtils:
    """시간 유틸리티 테스트 클래스"""
    
    def test_format_timestamp(self):
        """타임스탬프 형식 테스트"""
        from backend.utils.helpers import format_timestamp
        
        from datetime import datetime
        
        # 현재 시간으로 테스트
        now = datetime.now()
        formatted = format_timestamp(now)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_parse_timestamp(self):
        """타임스탬프 파싱 테스트"""
        from backend.utils.helpers import parse_timestamp
        
        # ISO 형식 문자열
        iso_string = "2024-01-01T12:00:00"
        parsed = parse_timestamp(iso_string)
        
        assert parsed is not None
        assert parsed.year == 2024
        assert parsed.month == 1
        assert parsed.day == 1
    
    def test_get_time_difference(self):
        """시간 차이 계산 테스트"""
        from backend.utils.helpers import get_time_difference
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        
        diff = get_time_difference(one_hour_ago, now)
        
        assert diff['hours'] == 1
        assert diff['minutes'] == 0
        assert diff['seconds'] == 0


class TestStringUtils:
    """문자열 유틸리티 테스트 클래스"""
    
    def test_normalize_string(self):
        """문자열 정규화 테스트"""
        from backend.utils.helpers import normalize_string
        
        test_cases = [
            ('  Hello World  ', 'Hello World'),
            ('\n\tTest\n\t', 'Test'),
            ('   ', ''),
            ('', ''),
            ('Normal String', 'Normal String')
        ]
        
        for input_str, expected in test_cases:
            result = normalize_string(input_str)
            assert result == expected
    
    def test_truncate_string(self):
        """문자열 자르기 테스트"""
        from backend.utils.helpers import truncate_string
        
        test_cases = [
            ('Hello World', 5, 'Hello...'),
            ('Short', 10, 'Short'),
            ('Very Long String', 8, 'Very Lon...'),
            ('', 5, ''),
            ('Test', 0, '...')
        ]
        
        for input_str, max_length, expected in test_cases:
            result = truncate_string(input_str, max_length)
            assert result == expected
    
    def test_extract_keywords(self):
        """키워드 추출 테스트"""
        from backend.utils.helpers import extract_keywords
        
        text = "철광석과 다이아몬드를 찾고 있어요. 제작법도 알려주세요."
        keywords = extract_keywords(text)
        
        assert '철광석' in keywords
        assert '다이아몬드' in keywords
        assert '제작법' in keywords
        assert len(keywords) >= 3 