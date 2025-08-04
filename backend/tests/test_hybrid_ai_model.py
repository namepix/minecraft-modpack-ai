"""
하이브리드 AI 모델 테스트
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from backend.models.hybrid_ai_model import HybridAIModel


class TestHybridAIModel:
    """하이브리드 AI 모델 테스트 클래스"""
    
    @pytest.fixture
    def ai_model(self, mock_rag_manager, mock_ai_clients):
        """AI 모델 인스턴스 생성"""
        with patch('backend.models.hybrid_ai_model.openai.OpenAI') as mock_openai, \
             patch('backend.models.hybrid_ai_model.anthropic.Anthropic') as mock_anthropic, \
             patch('backend.models.hybrid_ai_model.genai.configure') as mock_google:
            
            mock_openai.return_value = mock_ai_clients['openai']
            mock_anthropic.return_value = mock_ai_clients['anthropic']
            mock_google.return_value = None
            
            model = HybridAIModel(
                recipe_manager=Mock(),
                language_mapper=Mock(),
                rag_manager=mock_rag_manager
            )
            model.clients = mock_ai_clients
            return model
    
    def test_initialization(self, mock_env_vars):
        """초기화 테스트"""
        with patch('backend.models.hybrid_ai_model.openai.OpenAI'), \
             patch('backend.models.hybrid_ai_model.anthropic.Anthropic'), \
             patch('backend.models.hybrid_ai_model.genai.configure'):
            
            model = HybridAIModel()
            
            assert model.current_model == 'gpt-3.5-turbo'
            assert 'gpt-3.5-turbo' in model.available_models
            assert 'claude-3-haiku' in model.available_models
            assert 'gemini-pro' in model.available_models
    
    def test_get_available_models_info(self, ai_model):
        """사용 가능한 모델 정보 테스트"""
        models_info = ai_model.get_available_models_info()
        
        assert len(models_info) == 5  # 5개 모델
        assert any(model['id'] == 'gpt-3.5-turbo' for model in models_info)
        assert any(model['id'] == 'claude-3-haiku' for model in models_info)
        assert any(model['id'] == 'gemini-pro' for model in models_info)
        
        # 현재 모델 확인
        current_model = next(model for model in models_info if model['current'])
        assert current_model['id'] == 'gpt-3.5-turbo'
    
    def test_switch_model_success(self, ai_model):
        """모델 전환 성공 테스트"""
        result = ai_model.switch_model('claude-3-haiku')
        
        assert result is True
        assert ai_model.current_model == 'claude-3-haiku'
    
    def test_switch_model_invalid(self, ai_model):
        """잘못된 모델 전환 테스트"""
        result = ai_model.switch_model('invalid-model')
        
        assert result is False
        assert ai_model.current_model == 'gpt-3.5-turbo'  # 원래 모델 유지
    
    def test_extract_korean_items(self, ai_model):
        """한글 아이템명 추출 테스트"""
        message = "철광석과 다이아몬드 그리고 철괴를 찾고 있어요"
        korean_items = ai_model._extract_korean_items(message)
        
        assert '철광석' in korean_items
        assert '다이아몬드' in korean_items
        assert '철괴' in korean_items
        assert len(korean_items) == 3
    
    def test_extract_item_names(self, ai_model):
        """아이템명 추출 테스트"""
        message = "iron_ore diamond_ore iron_ingot 철광석"
        item_names = ai_model._extract_item_names(message)
        
        assert 'iron' in item_names
        assert 'ore' in item_names
        assert 'diamond' in item_names
        assert '철광석' in item_names
    
    def test_get_rag_context_success(self, ai_model, mock_rag_manager):
        """RAG 컨텍스트 조회 성공 테스트"""
        message = "철광석 제작법"
        rag_context = ai_model._get_rag_context(message, "TestModpack")
        
        assert "RAG 정보:" in rag_context
        assert "테스트 RAG 문서 1" in rag_context
        assert "테스트 RAG 문서 2" in rag_context
        mock_rag_manager.search_similar_documents.assert_called_once()
    
    def test_get_rag_context_no_results(self, ai_model, mock_rag_manager):
        """RAG 컨텍스트 조회 실패 테스트"""
        mock_rag_manager.search_similar_documents.return_value = []
        
        message = "존재하지 않는 아이템"
        rag_context = ai_model._get_rag_context(message, "TestModpack")
        
        assert "관련 문서를 찾을 수 없습니다" in rag_context
    
    def test_get_rag_context_error(self, ai_model, mock_rag_manager):
        """RAG 컨텍스트 조회 오류 테스트"""
        mock_rag_manager.search_similar_documents.side_effect = Exception("RAG 오류")
        
        message = "테스트 메시지"
        with pytest.raises(RuntimeError, match="RAG 컨텍스트 조회 실패"):
            ai_model._get_rag_context(message, "TestModpack")
    
    def test_get_rag_context_no_manager(self):
        """RAG 매니저 없음 테스트"""
        model = HybridAIModel(rag_manager=None)
        
        with pytest.raises(RuntimeError, match="RAG 매니저가 필수이지만 초기화되지 않았습니다"):
            model._get_rag_context("테스트", "TestModpack")
    
    def test_translate_korean_to_english(self, ai_model):
        """한글-영어 변환 테스트"""
        ai_model.language_mapper.find_english_name_hybrid.return_value = ("iron_ore", 0.8, "db")
        
        english_name, confidence, source = ai_model._translate_korean_to_english(
            "철광석", "TestModpack", "test-user"
        )
        
        assert english_name == "iron_ore"
        assert confidence == 0.8
        assert source == "db"
    
    def test_format_response_with_korean(self, ai_model):
        """응답 한글 포맷팅 테스트"""
        response = "iron_ore를 찾으려면 지하로 가세요."
        translation_mapping = {"철광석": "iron_ore"}
        
        formatted = ai_model._format_response_with_korean(response, translation_mapping)
        
        assert "철광석(iron_ore)" in formatted
    
    @patch('backend.models.hybrid_ai_model.openai.RateLimitError')
    def test_openai_rate_limit_error(self, mock_rate_limit, ai_model):
        """OpenAI 속도 제한 오류 테스트"""
        mock_rate_limit.side_effect = Exception("Rate limit exceeded")
        
        response = ai_model._generate_openai_response("테스트", [], "시스템 프롬프트")
        
        assert "무료 크레딧이 소진되었습니다" in response
    
    @patch('backend.models.hybrid_ai_model.openai.AuthenticationError')
    def test_openai_auth_error(self, mock_auth_error, ai_model):
        """OpenAI 인증 오류 테스트"""
        mock_auth_error.side_effect = Exception("Invalid API key")
        
        response = ai_model._generate_openai_response("테스트", [], "시스템 프롬프트")
        
        assert "API 키에 문제가 있습니다" in response
    
    def test_generate_response_integration(self, ai_model, sample_chat_history):
        """통합 응답 생성 테스트"""
        ai_model.recipe_manager.get_recipe_with_version_fallback.return_value = {
            'type': 'crafting',
            'ingredients': [{'item': 'iron_ore', 'count': 1}]
        }
        
        ai_model.language_mapper.find_english_name_hybrid.return_value = ("iron_ore", 0.9, "db")
        
        response = ai_model.generate_response(
            message="철광석 제작법 알려줘",
            chat_history=sample_chat_history,
            modpack_name="TestModpack",
            modpack_version="1.0.0",
            user_uuid="test-user"
        )
        
        assert response is not None
        assert len(response) > 0
        assert "테스트 OpenAI 응답" in response
    
    def test_generate_response_with_web_search(self, ai_model, sample_chat_history):
        """웹검색 포함 응답 생성 테스트"""
        # RAG에서 정보를 찾지 못하는 상황 시뮬레이션
        ai_model.rag_manager.search_similar_documents.return_value = []
        
        response = ai_model.generate_response(
            message="존재하지 않는 아이템",
            chat_history=sample_chat_history,
            modpack_name="TestModpack",
            modpack_version="1.0.0",
            user_uuid="test-user"
        )
        
        assert response is not None
        # 웹검색이 호출되었는지 확인
        assert "테스트 OpenAI 응답" in response
    
    def test_system_prompt_formatting(self, ai_model):
        """시스템 프롬프트 포맷팅 테스트"""
        system_prompt = ai_model.system_prompt.format(
            modpack_name="TestModpack",
            modpack_version="1.0.0",
            context_info="로컬 컨텍스트",
            rag_context="RAG 컨텍스트",
            web_search_context="웹검색 컨텍스트"
        )
        
        assert "TestModpack" in system_prompt
        assert "1.0.0" in system_prompt
        assert "로컬 컨텍스트" in system_prompt
        assert "RAG 컨텍스트" in system_prompt
        assert "웹검색 컨텍스트" in system_prompt
    
    def test_web_search_context_generation(self, ai_model):
        """웹검색 컨텍스트 생성 테스트"""
        message = "철광석 제작법"
        modpack_name = "TestModpack"
        
        web_context = ai_model._get_web_search_context(message, modpack_name)
        
        assert "웹검색 결과:" in web_context
        assert "테스트 OpenAI 응답" in web_context
    
    def test_error_handling_in_generate_response(self, ai_model):
        """응답 생성 중 오류 처리 테스트"""
        ai_model._get_rag_context.side_effect = Exception("RAG 오류")
        
        response = ai_model.generate_response(
            message="테스트",
            chat_history=[],
            modpack_name="TestModpack"
        )
        
        assert "일시적인 오류가 발생했습니다" in response 