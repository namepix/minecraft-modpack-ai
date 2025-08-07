"""
Flask 앱 통합 테스트 - 간단한 버전
"""
import pytest
import json
from unittest.mock import Mock, patch
from backend.app import app


class TestAppIntegration:
    """Flask 앱 통합 테스트 클래스"""
    
    @pytest.fixture
    def client(self):
        """테스트 클라이언트 생성"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.mark.integration
    def test_health_check(self, client):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'current_model' in data
        assert 'available_models' in data
    
    @patch('backend.app.gemini_client')
    def test_chat_endpoint_with_gemini(self, mock_gemini_client, client):
        """Gemini 웹검색 기능이 활성화된 채팅 엔드포인트 테스트"""
        # Gemini 클라이언트 모킹
        mock_response = Mock()
        mock_response.text = "Gemini 웹검색 응답"
        mock_gemini_client.models.generate_content.return_value = mock_response
        
        request_data = {
            'message': '최신 마인크래프트 모드 정보 알려줘',
            'player_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'response' in data
        assert data['response'] == 'Gemini 웹검색 응답'
        assert data['model'] == 'gemini'
        
        # Gemini 클라이언트가 호출되었는지 확인
        mock_gemini_client.models.generate_content.assert_called_once()
    
    @patch('backend.app.gemini_client')
    def test_chat_endpoint_gemini_fallback(self, mock_gemini_client, client):
        """Gemini 웹검색 실패시 기본 모드로 폴백 테스트"""
        # Gemini 클라이언트 예외 발생
        mock_gemini_client.models.generate_content.side_effect = Exception("Gemini API 오류")
        
        request_data = {
            'message': '철광석 제작법 알려줘',
            'player_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'response' in data
        assert 'Gemini API 오류가 발생했습니다' in data['response']
    
    @patch('backend.app.openai_client')
    def test_chat_endpoint_with_openai(self, mock_openai_client, client):
        """OpenAI 모델을 사용한 채팅 엔드포인트 테스트"""
        # OpenAI 클라이언트 모킹
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "OpenAI 응답"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        # Gemini 클라이언트를 None으로 설정하여 OpenAI 사용
        with patch('backend.app.gemini_client', None):
            with patch('backend.app.current_model', 'openai'):
                request_data = {
                    'message': '철광석 제작법 알려줘',
                    'player_uuid': 'test-user-123',
                    'modpack_name': 'TestModpack',
                    'modpack_version': '1.0.0'
                }
                
                response = client.post('/chat',
                                     data=json.dumps(request_data),
                                     content_type='application/json')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] == True
                assert data['response'] == 'OpenAI 응답'
                assert data['model'] == 'openai'
    
    def test_chat_endpoint_missing_data(self, client):
        """채팅 엔드포인트 누락된 데이터 테스트"""
        # 필수 필드 누락
        request_data = {
            'message': '테스트 메시지'
            # player_uuid, modpack_name 누락
        }
        
        response = client.post('/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200  # 현재는 모든 요청이 성공하도록 설계됨
        data = json.loads(response.data)
        assert 'response' in data
    
    def test_models_endpoint(self, client):
        """AI 모델 목록 엔드포인트 테스트"""
        response = client.get('/models')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert isinstance(data['models'], list)
    
    def test_switch_model_endpoint_success(self, client):
        """모델 전환 엔드포인트 성공 테스트"""
        request_data = {
            'model_id': 'gemini'
        }
        
        response = client.post('/models/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'message' in data
    
    def test_switch_model_endpoint_invalid_model(self, client):
        """모델 전환 엔드포인트 잘못된 모델 테스트"""
        request_data = {
            'model_id': 'invalid-model'
        }
        
        response = client.post('/models/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    @patch('backend.app.gemini_client')
    def test_recipe_endpoint_with_gemini(self, mock_gemini_client, client):
        """Gemini를 사용한 레시피 엔드포인트 테스트"""
        # Gemini 클라이언트 모킹
        mock_response = Mock()
        mock_response.text = "다이아몬드 제작법: 다이아몬드 블록을 9개 배치하면 됩니다."
        mock_gemini_client.models.generate_content.return_value = mock_response
        
        response = client.get('/recipe/diamond')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'recipe' in data
        assert data['recipe']['item'] == 'diamond'
        assert '다이아몬드 제작법' in data['recipe']['recipe']
    
    def test_recipe_endpoint_no_model(self, client):
        """AI 모델이 없을 때 레시피 엔드포인트 테스트"""
        # 모든 AI 모델을 None으로 설정
        with patch('backend.app.gemini_client', None):
            with patch('backend.app.openai_client', None):
                with patch('backend.app.claude_client', None):
                    with patch('backend.app.current_model', None):
                        response = client.get('/recipe/diamond')
                        
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] == True
                        assert 'recipe' in data
                        assert '제작법을 찾을 수 없습니다' in data['recipe']['recipe']
    
    def test_error_handling(self, client):
        """오류 처리 테스트"""
        # 잘못된 JSON 데이터로 요청
        response = client.post('/chat',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'error' in data
    
    def test_cors_headers(self, client):
        """CORS 헤더 테스트"""
        response = client.get('/health')
        
        # CORS 헤더가 설정되어 있는지 확인
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_options_request(self, client):
        """OPTIONS 요청 테스트 (CORS preflight)"""
        response = client.options('/chat')
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers 