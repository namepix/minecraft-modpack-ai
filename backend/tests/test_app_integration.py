"""
Flask 앱 통합 테스트
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
    
    @pytest.fixture
    def mock_managers(self):
        """매니저들 모킹"""
        with patch('backend.app.chat_manager') as mock_chat, \
             patch('backend.app.recipe_manager') as mock_recipe, \
             patch('backend.app.language_mapper') as mock_lang, \
             patch('backend.app.rag_manager') as mock_rag, \
             patch('backend.app.ai_model') as mock_ai:
            
            # 모킹된 매니저들 설정
            mock_chat.get_chat_history.return_value = []
            mock_chat.add_message.return_value = True
            mock_recipe.get_recipe_with_version_fallback.return_value = None
            mock_recipe.get_item_info_with_version_fallback.return_value = None
            mock_lang.find_english_name_hybrid.return_value = (None, 0.0, "no_match")
            mock_rag.search_similar_documents.return_value = []
            mock_ai.generate_response.return_value = "테스트 AI 응답"
            mock_ai.get_available_models_info.return_value = []
            mock_ai.switch_model.return_value = True
            
            yield {
                'chat': mock_chat,
                'recipe': mock_recipe,
                'language': mock_lang,
                'rag': mock_rag,
                'ai': mock_ai
            }
    
    @pytest.mark.integration
    def test_health_check(self, client):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    @pytest.mark.integration
    def test_chat_endpoint_success(self, client, mock_managers):
        """채팅 엔드포인트 성공 테스트"""
        request_data = {
            'message': '철광석 제작법 알려줘',
            'user_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/api/chat', 
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'response' in data
        assert data['response'] == '테스트 AI 응답'
        
        # 매니저들이 호출되었는지 확인
        mock_managers['chat'].add_message.assert_called_once()
        mock_managers['ai'].generate_response.assert_called_once()
    
    def test_chat_endpoint_missing_data(self, client):
        """채팅 엔드포인트 누락된 데이터 테스트"""
        # 필수 필드 누락
        request_data = {
            'message': '테스트 메시지'
            # user_uuid, modpack_name 누락
        }
        
        response = client.post('/api/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_endpoint_invalid_uuid(self, client):
        """채팅 엔드포인트 잘못된 UUID 테스트"""
        request_data = {
            'message': '테스트 메시지',
            'user_uuid': 'invalid-uuid',  # 잘못된 UUID 형식
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/api/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_endpoint_message_too_long(self, client):
        """채팅 엔드포인트 메시지 길이 초과 테스트"""
        long_message = 'a' * 1001  # 1000자 초과
        
        request_data = {
            'message': long_message,
            'user_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/api/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_history_endpoint(self, client, mock_managers):
        """채팅 기록 엔드포인트 테스트"""
        # 모킹된 채팅 기록 설정
        mock_history = [
            {
                'user_message': '철광석은 어떻게 얻나요?',
                'ai_response': '철광석은 지하에서 캘 수 있습니다.',
                'timestamp': '2024-01-01T10:00:00'
            }
        ]
        mock_managers['chat'].get_chat_history.return_value = mock_history
        
        response = client.get('/api/chat/history?user_uuid=test-user-123&limit=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'history' in data
        assert len(data['history']) == 1
        assert data['history'][0]['user_message'] == '철광석은 어떻게 얻나요?'
    
    def test_recipe_endpoint_success(self, client, mock_managers):
        """레시피 엔드포인트 성공 테스트"""
        # 모킹된 레시피 데이터 설정
        mock_recipe_data = {
            'item_name': 'iron_ore',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'iron_ore', 'count': 1}
        }
        mock_managers['recipe'].get_recipe_with_version_fallback.return_value = mock_recipe_data
        
        response = client.get('/api/recipe/iron_ore?modpack_name=TestModpack&version=1.0.0')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'recipe' in data
        assert data['recipe']['item_name'] == 'iron_ore'
    
    def test_recipe_endpoint_not_found(self, client, mock_managers):
        """레시피 엔드포인트 찾을 수 없음 테스트"""
        mock_managers['recipe'].get_recipe_with_version_fallback.return_value = None
        
        response = client.get('/api/recipe/nonexistent?modpack_name=TestModpack&version=1.0.0')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_item_info_endpoint_success(self, client, mock_managers):
        """아이템 정보 엔드포인트 성공 테스트"""
        # 모킹된 아이템 데이터 설정
        mock_item_data = {
            'name': 'iron_ore',
            'display_name': '철광석',
            'mod': 'minecraft',
            'description': '철광석입니다.'
        }
        mock_managers['recipe'].get_item_info_with_version_fallback.return_value = mock_item_data
        
        response = client.get('/api/item/iron_ore?modpack_name=TestModpack&version=1.0.0')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'item' in data
        assert data['item']['name'] == 'iron_ore'
        assert data['item']['display_name'] == '철광석'
    
    def test_item_info_endpoint_not_found(self, client, mock_managers):
        """아이템 정보 엔드포인트 찾을 수 없음 테스트"""
        mock_managers['recipe'].get_item_info_with_version_fallback.return_value = None
        
        response = client.get('/api/item/nonexistent?modpack_name=TestModpack&version=1.0.0')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_models_endpoint(self, client, mock_managers):
        """AI 모델 목록 엔드포인트 테스트"""
        # 모킹된 모델 정보 설정
        mock_models_info = [
            {
                'id': 'gpt-3.5-turbo',
                'name': 'GPT-3.5 Turbo',
                'provider': 'openai',
                'free_tier': True,
                'available': True,
                'current': True
            }
        ]
        mock_managers['ai'].get_available_models_info.return_value = mock_models_info
        
        response = client.get('/api/models')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert len(data['models']) == 1
        assert data['models'][0]['id'] == 'gpt-3.5-turbo'
    
    def test_switch_model_endpoint_success(self, client, mock_managers):
        """모델 전환 엔드포인트 성공 테스트"""
        request_data = {
            'model_id': 'claude-3-haiku'
        }
        
        response = client.post('/api/models/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is True
        
        # AI 모델 전환이 호출되었는지 확인
        mock_managers['ai'].switch_model.assert_called_once_with('claude-3-haiku')
    
    def test_switch_model_endpoint_failure(self, client, mock_managers):
        """모델 전환 엔드포인트 실패 테스트"""
        mock_managers['ai'].switch_model.return_value = False
        
        request_data = {
            'model_id': 'invalid-model'
        }
        
        response = client.post('/api/models/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_current_model_endpoint(self, client, mock_managers):
        """현재 모델 엔드포인트 테스트"""
        # 모킹된 현재 모델 정보 설정
        mock_current_model = {
            'id': 'gpt-3.5-turbo',
            'name': 'GPT-3.5 Turbo',
            'provider': 'openai',
            'free_tier': True,
            'available': True,
            'current': True
        }
        mock_managers['ai'].get_available_models_info.return_value = [mock_current_model]
        
        response = client.get('/api/models/current')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'model' in data
        assert data['model']['id'] == 'gpt-3.5-turbo'
    
    def test_modpack_switch_endpoint_success(self, client, mock_managers):
        """모드팩 전환 엔드포인트 성공 테스트"""
        request_data = {
            'modpack_name': 'NewModpack',
            'version': '2.0.0'
        }
        
        response = client.post('/api/modpack/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
        assert data['success'] is True
    
    def test_modpack_switch_endpoint_missing_data(self, client):
        """모드팩 전환 엔드포인트 누락된 데이터 테스트"""
        request_data = {
            'modpack_name': 'NewModpack'
            # version 누락
        }
        
        response = client.post('/api/modpack/switch',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_rate_limiting(self, client, mock_managers):
        """속도 제한 테스트"""
        request_data = {
            'message': '테스트 메시지',
            'user_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        # 여러 번 요청하여 속도 제한 테스트
        for _ in range(10):
            response = client.post('/api/chat',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            assert response.status_code in [200, 429]  # 성공 또는 속도 제한
    
    def test_xss_prevention(self, client, mock_managers):
        """XSS 방지 테스트"""
        malicious_message = '<script>alert("XSS")</script>'
        
        request_data = {
            'message': malicious_message,
            'user_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/api/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        # XSS가 방지되어야 함
        assert response.status_code == 200
        data = json.loads(response.data)
        assert '<script>' not in data['response']
    
    def test_error_handling(self, client, mock_managers):
        """오류 처리 테스트"""
        # AI 모델에서 예외 발생 시뮬레이션
        mock_managers['ai'].generate_response.side_effect = Exception("AI 오류")
        
        request_data = {
            'message': '테스트 메시지',
            'user_uuid': 'test-user-123',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        response = client.post('/api/chat',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_cors_headers(self, client):
        """CORS 헤더 테스트"""
        response = client.get('/api/health')
        
        # CORS 헤더가 설정되어 있는지 확인
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_options_request(self, client):
        """OPTIONS 요청 테스트 (CORS preflight)"""
        response = client.options('/api/chat')
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers 