import unittest
from unittest.mock import Mock, patch
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.models.hybrid_ai_model import HybridAIModel
from backend.database.recipe_manager import RecipeManager
from backend.utils.language_mapper import LanguageMapper

class TestHybridAIModel(unittest.TestCase):
    """HybridAIModel 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.recipe_manager = Mock(spec=RecipeManager)
        self.language_mapper = Mock(spec=LanguageMapper)
        self.rag_manager = Mock()
        
        self.ai_model = HybridAIModel(
            recipe_manager=self.recipe_manager,
            language_mapper=self.language_mapper,
            rag_manager=self.rag_manager
        )
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsNotNone(self.ai_model)
        self.assertEqual(self.ai_model.current_model, 'gpt-3.5-turbo')
    
    def test_get_available_models(self):
        """사용 가능한 모델 목록 테스트"""
        models = self.ai_model.get_available_models_info()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        
        # GPT-3.5 Turbo가 있는지 확인
        model_names = [model['name'] for model in models]
        self.assertIn('gpt-3.5-turbo', model_names)
    
    def test_switch_model(self):
        """모델 전환 테스트"""
        # 유효한 모델로 전환
        result = self.ai_model.switch_model('gpt-4')
        self.assertTrue(result['success'])
        self.assertEqual(self.ai_model.current_model, 'gpt-4')
        
        # 잘못된 모델로 전환 시도
        result = self.ai_model.switch_model('invalid-model')
        self.assertFalse(result['success'])
    
    def test_extract_korean_items(self):
        """한국어 아이템 추출 테스트"""
        message = "철광석과 다이아몬드로 무엇을 만들 수 있나요?"
        korean_items = self.ai_model._extract_korean_items(message)
        self.assertIn("철광석", korean_items)
        self.assertIn("다이아몬드", korean_items)
    
    @patch('backend.models.hybrid_ai_model.openai.OpenAI')
    def test_generate_openai_response(self, mock_openai):
        """OpenAI 응답 생성 테스트"""
        # Mock 설정
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "테스트 응답입니다."
        mock_client.chat.completions.create.return_value = mock_response
        
        # 테스트 실행
        response = self.ai_model._generate_openai_response(
            "테스트 메시지",
            [],
            "테스트 시스템 프롬프트"
        )
        
        self.assertEqual(response, "테스트 응답입니다.")
        mock_client.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main() 