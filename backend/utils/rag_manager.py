import os
import json
import logging
from typing import List, Dict, Optional
from google.cloud import storage
from google.cloud import aiplatform
import vertexai
from vertexai.language_models import TextGenerationModel
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from datetime import datetime

logger = logging.getLogger(__name__)

class RAGManager:
    def __init__(self, project_id: str, bucket_name: str):
        """RAG 매니저를 초기화합니다."""
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.storage_client = None
        self.bucket = None
        self.embedding_model = None
        self.vector_index = None
        
        self._init_gcp_services()
        self._init_embedding_model()
    
    def _init_gcp_services(self):
        """GCP 서비스들을 초기화합니다."""
        try:
            # GCS 클라이언트 초기화
            self.storage_client = storage.Client(project=self.project_id)
            self.bucket = self.storage_client.bucket(self.bucket_name)
            
            # Vertex AI 초기화
            vertexai.init(project=self.project_id, location="us-central1")
            
            logger.info("GCP RAG 서비스 초기화 완료")
            
        except Exception as e:
            logger.error(f"GCP RAG 서비스 초기화 실패: {e}")
            raise
    
    def _init_embedding_model(self):
        """임베딩 모델을 초기화합니다."""
        try:
            # Sentence Transformers 모델 사용
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("임베딩 모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 실패: {e}")
            raise
    
    def upload_modpack_data(self, modpack_name: str, data: Dict):
        """모드팩 데이터를 GCS에 업로드합니다."""
        try:
            # JSON 파일로 저장
            filename = f"modpacks/{modpack_name}/data.json"
            blob = self.bucket.blob(filename)
            
            # 메타데이터 추가
            data['metadata'] = {
                'modpack_name': modpack_name,
                'upload_timestamp': str(datetime.now()),
                'version': '1.0'
            }
            
            blob.upload_from_string(
                json.dumps(data, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"모드팩 데이터 업로드 완료: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"모드팩 데이터 업로드 실패: {e}")
            return False
    
    def search_similar_documents(self, query: str, modpack_name: str, top_k: int = 3) -> List[Dict]:
        """유사한 문서를 검색합니다."""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode([query])
            
            # GCS에서 모드팩 관련 문서 검색
            relevant_docs = []
            blobs = self.bucket.list_blobs(prefix=f"modpacks/{modpack_name}/")
            
            for blob in blobs:
                if blob.name.endswith('.json'):
                    content = blob.download_as_text()
                    doc_data = json.loads(content)
                    
                    # 문서 텍스트 임베딩
                    if 'text' in doc_data:
                        doc_embedding = self.embedding_model.encode([doc_data['text']])
                        
                        # 코사인 유사도 계산
                        similarity = np.dot(query_embedding, doc_embedding.T) / (
                            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                        )
                        
                        doc_data['similarity'] = float(similarity[0][0])
                        relevant_docs.append(doc_data)
            
            # 유사도 기준으로 정렬
            relevant_docs.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return relevant_docs[:top_k]
            
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}")
            return []
    
    def create_vector_index(self, modpack_name: str):
        """벡터 인덱스를 생성합니다."""
        try:
            # 모든 문서 수집
            documents = []
            embeddings = []
            
            blobs = self.bucket.list_blobs(prefix=f"modpacks/{modpack_name}/")
            
            for blob in blobs:
                if blob.name.endswith('.json'):
                    content = blob.download_as_text()
                    doc_data = json.loads(content)
                    
                    if 'text' in doc_data:
                        documents.append(doc_data)
                        embedding = self.embedding_model.encode([doc_data['text']])
                        embeddings.append(embedding[0])
            
            if not embeddings:
                logger.warning(f"모드팩 {modpack_name}에 대한 문서가 없습니다.")
                return False
            
            # FAISS 인덱스 생성
            embeddings_array = np.array(embeddings)
            dimension = embeddings_array.shape[1]
            
            self.vector_index = faiss.IndexFlatIP(dimension)  # Inner Product (코사인 유사도)
            self.vector_index.add(embeddings_array.astype('float32'))
            
            # 인덱스 저장
            index_filename = f"modpacks/{modpack_name}/vector_index.faiss"
            blob = self.bucket.blob(index_filename)
            
            # FAISS 인덱스를 바이트로 직렬화
            index_bytes = faiss.serialize_index(self.vector_index)
            blob.upload_from_string(index_bytes)
            
            # 문서 메타데이터 저장
            metadata = {
                'documents': documents,
                'index_info': {
                    'dimension': dimension,
                    'num_documents': len(documents),
                    'created_at': str(datetime.now())
                }
            }
            
            metadata_filename = f"modpacks/{modpack_name}/index_metadata.json"
            metadata_blob = self.bucket.blob(metadata_filename)
            metadata_blob.upload_from_string(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"벡터 인덱스 생성 완료: {modpack_name}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 인덱스 생성 실패: {e}")
            return False
    
    def load_vector_index(self, modpack_name: str):
        """벡터 인덱스를 로드합니다."""
        try:
            # 인덱스 파일 로드
            index_filename = f"modpacks/{modpack_name}/vector_index.faiss"
            blob = self.bucket.blob(index_filename)
            
            if not blob.exists():
                logger.warning(f"벡터 인덱스가 존재하지 않습니다: {index_filename}")
                return False
            
            index_bytes = blob.download_as_bytes()
            self.vector_index = faiss.deserialize_index(index_bytes)
            
            # 메타데이터 로드
            metadata_filename = f"modpacks/{modpack_name}/index_metadata.json"
            metadata_blob = self.bucket.blob(metadata_filename)
            
            if metadata_blob.exists():
                metadata_content = metadata_blob.download_as_text()
                self.metadata = json.loads(metadata_content)
            
            logger.info(f"벡터 인덱스 로드 완료: {modpack_name}")
            return True
            
        except Exception as e:
            logger.error(f"벡터 인덱스 로드 실패: {e}")
            return False
    
    def search_with_vector_index(self, query: str, top_k: int = 3) -> List[Dict]:
        """벡터 인덱스를 사용하여 검색합니다."""
        try:
            if self.vector_index is None:
                logger.warning("벡터 인덱스가 로드되지 않았습니다.")
                return []
            
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode([query])
            
            # 벡터 검색 수행
            similarities, indices = self.vector_index.search(
                query_embedding.astype('float32'), top_k
            )
            
            # 결과 구성
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if idx < len(self.metadata.get('documents', [])):
                    doc = self.metadata['documents'][idx].copy()
                    doc['similarity'] = float(similarity)
                    doc['rank'] = i + 1
                    results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"벡터 검색 실패: {e}")
            return []
    
    def update_modpack_knowledge(self, modpack_name: str, new_data: Dict):
        """모드팩 지식을 업데이트합니다."""
        try:
            # 기존 데이터 로드
            existing_data = {}
            filename = f"modpacks/{modpack_name}/data.json"
            blob = self.bucket.blob(filename)
            
            if blob.exists():
                content = blob.download_as_text()
                existing_data = json.loads(content)
            
            # 새 데이터 병합
            existing_data.update(new_data)
            
            # 업데이트된 데이터 업로드
            self.upload_modpack_data(modpack_name, existing_data)
            
            # 벡터 인덱스 재생성
            self.create_vector_index(modpack_name)
            
            logger.info(f"모드팩 지식 업데이트 완료: {modpack_name}")
            return True
            
        except Exception as e:
            logger.error(f"모드팩 지식 업데이트 실패: {e}")
            return False 