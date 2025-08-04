"""
RAG 매니저 테스트
"""
import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from backend.utils.rag_manager import RAGManager


class TestRAGManager:
    """RAG 매니저 테스트 클래스"""
    
    @pytest.fixture
    def rag_manager(self):
        """RAG 매니저 인스턴스 생성"""
        with patch('backend.utils.rag_manager.storage.Client'), \
             patch('backend.utils.rag_manager.vertexai.init'), \
             patch('backend.utils.rag_manager.SentenceTransformer'):
            
            manager = RAGManager('test-project', 'test-bucket')
            manager.storage_client = Mock()
            manager.bucket = Mock()
            manager.embedding_model = Mock()
            return manager
    
    def test_initialization(self):
        """초기화 테스트"""
        with patch('backend.utils.rag_manager.storage.Client') as mock_storage, \
             patch('backend.utils.rag_manager.vertexai.init') as mock_vertex, \
             patch('backend.utils.rag_manager.SentenceTransformer') as mock_embedding:
            
            mock_storage.return_value = Mock()
            mock_embedding.return_value = Mock()
            
            manager = RAGManager('test-project', 'test-bucket')
            
            assert manager.project_id == 'test-project'
            assert manager.bucket_name == 'test-bucket'
            mock_storage.assert_called_once_with(project='test-project')
            mock_vertex.assert_called_once_with(project='test-project', location="us-central1")
            mock_embedding.assert_called_once_with('all-MiniLM-L6-v2')
    
    def test_initialization_error(self):
        """초기화 오류 테스트"""
        with patch('backend.utils.rag_manager.storage.Client') as mock_storage:
            mock_storage.side_effect = Exception("GCP 연결 실패")
            
            with pytest.raises(Exception, match="GCP 연결 실패"):
                RAGManager('test-project', 'test-bucket')
    
    def test_upload_modpack_data_success(self, rag_manager):
        """모드팩 데이터 업로드 성공 테스트"""
        test_data = {
            'modpack_name': 'TestModpack',
            'version': '1.0.0',
            'mods': [{'name': 'testmod', 'version': '1.0.0'}]
        }
        
        mock_blob = Mock()
        rag_manager.bucket.blob.return_value = mock_blob
        
        result = rag_manager.upload_modpack_data('TestModpack', test_data)
        
        assert result is True
        rag_manager.bucket.blob.assert_called_once_with('modpacks/TestModpack/data.json')
        mock_blob.upload_from_string.assert_called_once()
        
        # 업로드된 데이터에 메타데이터가 포함되었는지 확인
        call_args = mock_blob.upload_from_string.call_args
        uploaded_data = json.loads(call_args[0][0])
        assert 'metadata' in uploaded_data
        assert uploaded_data['metadata']['modpack_name'] == 'TestModpack'
    
    def test_upload_modpack_data_error(self, rag_manager):
        """모드팩 데이터 업로드 오류 테스트"""
        rag_manager.bucket.blob.side_effect = Exception("업로드 실패")
        
        result = rag_manager.upload_modpack_data('TestModpack', {})
        
        assert result is False
    
    def test_search_similar_documents_success(self, rag_manager):
        """유사 문서 검색 성공 테스트"""
        # 모킹된 문서 데이터
        mock_blob1 = Mock()
        mock_blob1.name = 'modpacks/TestModpack/doc1.json'
        mock_blob1.download_as_text.return_value = json.dumps({
            'text': '철광석 제작법에 대한 문서입니다.'
        })
        
        mock_blob2 = Mock()
        mock_blob2.name = 'modpacks/TestModpack/doc2.json'
        mock_blob2.download_as_text.return_value = json.dumps({
            'text': '다이아몬드 제작법에 대한 문서입니다.'
        })
        
        rag_manager.bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        rag_manager.embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]  # 임베딩 벡터
        
        results = rag_manager.search_similar_documents('철광석', 'TestModpack', top_k=2)
        
        assert len(results) == 2
        assert all('content' in doc for doc in results)
        assert all('source' in doc for doc in results)
        assert all('similarity' in doc for doc in results)
        
        # 유사도 기준으로 정렬되었는지 확인
        similarities = [doc['similarity'] for doc in results]
        assert similarities == sorted(similarities, reverse=True)
    
    def test_search_similar_documents_no_results(self, rag_manager):
        """유사 문서 검색 결과 없음 테스트"""
        rag_manager.bucket.list_blobs.return_value = []
        
        results = rag_manager.search_similar_documents('존재하지 않는 아이템', 'TestModpack')
        
        assert results == []
    
    def test_search_similar_documents_error(self, rag_manager):
        """유사 문서 검색 오류 테스트"""
        rag_manager.bucket.list_blobs.side_effect = Exception("검색 오류")
        
        results = rag_manager.search_similar_documents('테스트', 'TestModpack')
        
        assert results == []
    
    def test_create_vector_index(self, rag_manager):
        """벡터 인덱스 생성 테스트"""
        with patch('backend.utils.rag_manager.faiss') as mock_faiss:
            mock_index = Mock()
            mock_faiss.IndexFlatIP.return_value = mock_index
            
            rag_manager.create_vector_index('TestModpack')
            
            mock_faiss.IndexFlatIP.assert_called_once()
            mock_index.add.assert_called_once()
    
    def test_load_vector_index(self, rag_manager):
        """벡터 인덱스 로드 테스트"""
        with patch('backend.utils.rag_manager.faiss') as mock_faiss:
            mock_index = Mock()
            mock_faiss.read_index.return_value = mock_index
            
            rag_manager.load_vector_index('TestModpack')
            
            mock_faiss.read_index.assert_called_once()
            assert rag_manager.vector_index == mock_index
    
    def test_search_with_vector_index(self, rag_manager):
        """벡터 인덱스 검색 테스트"""
        mock_index = Mock()
        mock_index.search.return_value = ([[0.8, 0.6]], [[0, 1]])  # 거리, 인덱스
        rag_manager.vector_index = mock_index
        
        rag_manager.embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        results = rag_manager.search_with_vector_index('테스트 쿼리', top_k=2)
        
        assert len(results) == 2
        mock_index.search.assert_called_once()
    
    def test_update_modpack_knowledge(self, rag_manager):
        """모드팩 지식 업데이트 테스트"""
        test_data = {'new_data': 'test'}
        
        with patch.object(rag_manager, 'upload_modpack_data') as mock_upload, \
             patch.object(rag_manager, 'create_vector_index') as mock_create:
            
            mock_upload.return_value = True
            
            rag_manager.update_modpack_knowledge('TestModpack', test_data)
            
            mock_upload.assert_called_once_with('TestModpack', test_data)
            mock_create.assert_called_once_with('TestModpack')
    
    def test_search_similar_documents_with_embedding_error(self, rag_manager):
        """임베딩 오류 시 검색 테스트"""
        rag_manager.embedding_model.encode.side_effect = Exception("임베딩 오류")
        
        results = rag_manager.search_similar_documents('테스트', 'TestModpack')
        
        assert results == []
    
    def test_search_similar_documents_with_invalid_json(self, rag_manager):
        """잘못된 JSON 문서 처리 테스트"""
        mock_blob = Mock()
        mock_blob.name = 'modpacks/TestModpack/invalid.json'
        mock_blob.download_as_text.return_value = 'invalid json'
        
        rag_manager.bucket.list_blobs.return_value = [mock_blob]
        rag_manager.embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        results = rag_manager.search_similar_documents('테스트', 'TestModpack')
        
        # JSON 파싱 오류로 인해 결과가 비어있어야 함
        assert results == []
    
    def test_search_similar_documents_without_text_field(self, rag_manager):
        """text 필드가 없는 문서 처리 테스트"""
        mock_blob = Mock()
        mock_blob.name = 'modpacks/TestModpack/no_text.json'
        mock_blob.download_as_text.return_value = json.dumps({
            'title': '제목만 있는 문서',
            'content': '내용은 있지만 text 필드는 없음'
        })
        
        rag_manager.bucket.list_blobs.return_value = [mock_blob]
        rag_manager.embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        results = rag_manager.search_similar_documents('테스트', 'TestModpack')
        
        # text 필드가 없으므로 결과가 비어있어야 함
        assert results == []
    
    def test_upload_modpack_data_with_metadata(self, rag_manager):
        """메타데이터가 포함된 모드팩 데이터 업로드 테스트"""
        test_data = {
            'modpack_name': 'TestModpack',
            'version': '1.0.0'
        }
        
        mock_blob = Mock()
        rag_manager.bucket.blob.return_value = mock_blob
        
        rag_manager.upload_modpack_data('TestModpack', test_data)
        
        # 업로드된 데이터 확인
        call_args = mock_blob.upload_from_string.call_args
        uploaded_data = json.loads(call_args[0][0])
        
        assert 'metadata' in uploaded_data
        assert uploaded_data['metadata']['modpack_name'] == 'TestModpack'
        assert 'upload_timestamp' in uploaded_data['metadata']
        assert uploaded_data['metadata']['version'] == '1.0'
    
    def test_search_similar_documents_filtering(self, rag_manager):
        """문서 필터링 테스트"""
        # 다른 모드팩의 문서
        mock_blob1 = Mock()
        mock_blob1.name = 'modpacks/OtherModpack/doc1.json'
        mock_blob1.download_as_text.return_value = json.dumps({'text': '다른 모드팩 문서'})
        
        # 대상 모드팩의 문서
        mock_blob2 = Mock()
        mock_blob2.name = 'modpacks/TestModpack/doc1.json'
        mock_blob2.download_as_text.return_value = json.dumps({'text': '테스트 모드팩 문서'})
        
        rag_manager.bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
        rag_manager.embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        results = rag_manager.search_similar_documents('테스트', 'TestModpack')
        
        # TestModpack의 문서만 포함되어야 함
        assert len(results) == 1
        assert 'TestModpack' in results[0]['source'] 