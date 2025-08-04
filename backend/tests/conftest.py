"""
pytest 설정 및 공통 fixture
"""
import pytest
import os
import tempfile
import sqlite3
from unittest.mock import Mock, patch
from backend.database.chat_manager import ChatManager
from backend.database.recipe_manager import RecipeManager
from backend.utils.language_mapper import LanguageMapper
from backend.utils.rag_manager import RAGManager
from backend.models.hybrid_ai_model import HybridAIModel


@pytest.fixture
def temp_db():
    """임시 데이터베이스 fixture"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # 테스트 후 정리
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_env_vars():
    """환경 변수 모킹"""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'GOOGLE_API_KEY': 'test-google-key',
        'GCP_PROJECT_ID': 'test-project-id',
        'GCS_BUCKET_NAME': 'test-bucket-name',
        'DEFAULT_AI_MODEL': 'gpt-3.5-turbo',
        'SECRET_KEY': 'test-secret-key'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_rag_manager():
    """RAG 매니저 모킹"""
    mock_rag = Mock(spec=RAGManager)
    mock_rag.search_similar_documents.return_value = [
        {
            'content': '테스트 RAG 문서 1',
            'source': 'test_doc_1.json',
            'similarity': 0.85
        },
        {
            'content': '테스트 RAG 문서 2', 
            'source': 'test_doc_2.json',
            'similarity': 0.72
        }
    ]
    return mock_rag


@pytest.fixture
def mock_ai_clients():
    """AI 클라이언트들 모킹"""
    mock_openai = Mock()
    mock_openai.chat.completions.create.return_value.choices[0].message.content = "테스트 OpenAI 응답"
    
    mock_anthropic = Mock()
    mock_anthropic.messages.create.return_value.content[0].text = "테스트 Anthropic 응답"
    
    mock_google = Mock()
    mock_google.GenerativeModel.return_value.generate_content.return_value.text = "테스트 Google 응답"
    
    return {
        'openai': mock_openai,
        'anthropic': mock_anthropic,
        'google': mock_google
    }


@pytest.fixture
def sample_modpack_data():
    """샘플 모드팩 데이터"""
    return {
        'modpack_name': 'TestModpack',
        'version': '1.0.0',
        'mods': [
            {'name': 'testmod1', 'version': '1.0.0'},
            {'name': 'testmod2', 'version': '2.0.0'}
        ],
        'recipes': [
            {
                'item_name': 'test_item',
                'recipe_type': 'crafting',
                'ingredients': [{'item': 'dirt', 'count': 1}],
                'result': {'item': 'test_item', 'count': 1}
            }
        ],
        'items': [
            {
                'name': 'test_item',
                'display_name': '테스트 아이템',
                'mod': 'testmod1',
                'description': '테스트용 아이템입니다.'
            }
        ]
    }


@pytest.fixture
def sample_chat_history():
    """샘플 채팅 기록"""
    return [
        {
            'user_message': '철광석은 어떻게 얻나요?',
            'ai_response': '철광석은 지하에서 캘 수 있습니다.',
            'timestamp': '2024-01-01T10:00:00'
        },
        {
            'user_message': '다이아몬드는 어디서 찾나요?',
            'ai_response': '다이아몬드는 Y=12 이하에서 찾을 수 있습니다.',
            'timestamp': '2024-01-01T10:05:00'
        }
    ] 