# GCP 기반 RAG 시스템
# 모드팩 데이터를 GCP에 저장하고 벡터 검색을 수행

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

# GCP 라이브러리
try:
    from google.cloud import firestore
    from google.cloud import aiplatform
    from vertexai.language_models import TextEmbeddingModel
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    print("⚠️ GCP 라이브러리가 설치되지 않음. pip install google-cloud-firestore google-cloud-aiplatform vertexai 필요")

# 기존 모듈
from modpack_parser import scan_modpack

logger = logging.getLogger(__name__)

class GCPRAGSystem:
    """GCP 기반 RAG 시스템"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID')
        self.location = location
        self.enabled = False
        
        if not GCP_AVAILABLE:
            logger.warning("GCP 라이브러리 불가능 - RAG 시스템 비활성화")
            return
            
        if not self.project_id:
            logger.warning("GCP_PROJECT_ID 환경변수 없음 - RAG 시스템 비활성화")
            return
            
        try:
            # Firestore 클라이언트 초기화
            self.db = firestore.Client(project=self.project_id)
            
            # Vertex AI 초기화
            aiplatform.init(project=self.project_id, location=self.location)
            self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
            
            self.enabled = True
            logger.info(f"✅ GCP RAG 시스템 초기화 완료 - Project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"❌ GCP RAG 시스템 초기화 실패: {e}")
            self.enabled = False

    def is_enabled(self) -> bool:
        """RAG 시스템이 활성화되어 있는지 확인"""
        return self.enabled
    
    def _generate_doc_id(self, modpack_name: str, modpack_version: str, doc_source: str) -> str:
        """문서 고유 ID 생성"""
        content = f"{modpack_name}:{modpack_version}:{doc_source}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _chunk_text(self, text: str, max_chars: int = 1000) -> List[str]:
        """텍스트를 적절한 크기로 분할"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        words = text.split(' ')
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # 공백 포함
            if current_length + word_length > max_chars and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def build_modpack_index(self, modpack_name: str, modpack_version: str, modpack_path: str) -> Dict[str, Any]:
        """모드팩 데이터를 분석하고 GCP에 인덱스 구축"""
        if not self.enabled:
            return {"success": False, "error": "GCP RAG 시스템 비활성화"}
        
        try:
            logger.info(f"📦 모드팩 인덱스 구축 시작: {modpack_name} v{modpack_version}")
            
            # 1. 모드팩 데이터 스캔
            scan_result = scan_modpack(modpack_path)
            docs = scan_result.get('docs', [])
            stats = scan_result.get('stats', {})
            
            if not docs:
                return {"success": False, "error": "분석할 문서가 없음"}
            
            # 2. 컬렉션 이름 생성
            collection_name = f"modpack_{modpack_name}_{modpack_version}".replace('.', '_').replace('-', '_')
            collection_ref = self.db.collection(collection_name)
            
            # 3. 기존 데이터 삭제 (재구축 시)
            try:
                existing_docs = collection_ref.limit(100).stream()
                batch = self.db.batch()
                delete_count = 0
                for doc in existing_docs:
                    batch.delete(doc.reference)
                    delete_count += 1
                if delete_count > 0:
                    batch.commit()
                    logger.info(f"🗑️ 기존 문서 {delete_count}개 삭제")
            except Exception as e:
                logger.warning(f"기존 데이터 삭제 실패 (무시): {e}")
            
            # 4. 문서별 벡터화 및 저장
            batch = self.db.batch()
            processed_count = 0
            embedding_texts = []
            doc_metadata = []
            
            for doc in docs:
                doc_text = doc.get('text', '')
                if not doc_text:
                    continue
                
                # 텍스트 청킹
                chunks = self._chunk_text(doc_text, max_chars=800)
                
                for i, chunk in enumerate(chunks):
                    doc_id = self._generate_doc_id(modpack_name, modpack_version, 
                                                 f"{doc.get('source', 'unknown')}_{i}")
                    
                    embedding_texts.append(chunk)
                    doc_metadata.append({
                        'doc_id': doc_id,
                        'modpack_name': modpack_name,
                        'modpack_version': modpack_version,
                        'doc_type': doc.get('type', 'unknown'),
                        'doc_source': doc.get('source', 'unknown'),
                        'text': chunk,
                        'chunk_index': i,
                        'created_at': datetime.utcnow(),
                        'original_doc': doc
                    })
            
            # 5. 임베딩 생성 (배치 처리)
            logger.info(f"🔄 임베딩 생성 중... ({len(embedding_texts)}개 텍스트)")
            
            # Vertex AI의 배치 크기 제한 고려
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(embedding_texts), batch_size):
                batch_texts = embedding_texts[i:i + batch_size]
                try:
                    embeddings_response = self.embedding_model.get_embeddings(batch_texts)
                    batch_embeddings = [emb.values for emb in embeddings_response]
                    all_embeddings.extend(batch_embeddings)
                    logger.info(f"✅ 배치 {i//batch_size + 1} 완료")
                except Exception as e:
                    logger.error(f"❌ 임베딩 생성 실패 (배치 {i//batch_size + 1}): {e}")
                    continue
            
            if len(all_embeddings) != len(doc_metadata):
                return {"success": False, "error": f"임베딩 수({len(all_embeddings)})와 문서 수({len(doc_metadata)}) 불일치"}
            
            # 6. Firestore에 저장
            logger.info(f"💾 Firestore에 저장 중...")
            batch = self.db.batch()
            
            for metadata, embedding in zip(doc_metadata, all_embeddings):
                doc_ref = collection_ref.document(metadata['doc_id'])
                
                # Firestore 데이터 준비
                firestore_data = {
                    'modpack_name': metadata['modpack_name'],
                    'modpack_version': metadata['modpack_version'],
                    'doc_type': metadata['doc_type'],
                    'doc_source': metadata['doc_source'],
                    'text': metadata['text'],
                    'chunk_index': metadata['chunk_index'],
                    'embedding': embedding,
                    'created_at': metadata['created_at'],
                    'text_length': len(metadata['text'])
                }
                
                batch.set(doc_ref, firestore_data)
                processed_count += 1
                
                # Firestore 배치 제한 (500개)
                if processed_count % 400 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"📝 {processed_count}개 문서 저장 완료")
            
            # 남은 문서들 저장
            if processed_count % 400 != 0:
                batch.commit()
            
            # 7. 메타데이터 컬렉션에 모드팩 정보 저장
            metadata_ref = self.db.collection('modpack_metadata').document(f"{modpack_name}_{modpack_version}")
            metadata_ref.set({
                'modpack_name': modpack_name,
                'modpack_version': modpack_version,
                'modpack_path': modpack_path,
                'collection_name': collection_name,
                'document_count': processed_count,
                'stats': stats,
                'created_at': datetime.utcnow(),
                'last_updated': datetime.utcnow()
            })
            
            logger.info(f"🎉 모드팩 인덱스 구축 완료: {processed_count}개 문서")
            
            return {
                "success": True,
                "modpack_name": modpack_name,
                "modpack_version": modpack_version,
                "collection_name": collection_name,
                "document_count": processed_count,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ 모드팩 인덱스 구축 실패: {e}")
            return {"success": False, "error": str(e)}

    def search_documents(self, query: str, modpack_name: str, modpack_version: str, 
                        top_k: int = 5, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """모드팩에서 관련 문서 검색"""
        if not self.enabled:
            return []
        
        try:
            # 1. 쿼리 임베딩 생성
            query_embedding = self.embedding_model.get_embeddings([query])[0].values
            
            # 2. 컬렉션 참조
            collection_name = f"modpack_{modpack_name}_{modpack_version}".replace('.', '_').replace('-', '_')
            collection_ref = self.db.collection(collection_name)
            
            # 3. 모든 문서 조회 (Firestore는 벡터 검색 미지원이므로 브루트포스)
            docs = list(collection_ref.stream())
            
            if not docs:
                logger.warning(f"모드팩 데이터 없음: {modpack_name} v{modpack_version}")
                return []
            
            # 4. 유사도 계산
            results = []
            for doc in docs:
                doc_data = doc.to_dict()
                doc_embedding = doc_data.get('embedding', [])
                
                if not doc_embedding:
                    continue
                
                # 코사인 유사도 계산
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= min_score:
                    results.append({
                        'doc_id': doc.id,
                        'text': doc_data.get('text', ''),
                        'doc_type': doc_data.get('doc_type', 'unknown'),
                        'doc_source': doc_data.get('doc_source', 'unknown'),
                        'similarity': similarity,
                        'text_length': doc_data.get('text_length', 0)
                    })
            
            # 5. 유사도 기준 정렬 및 상위 K개 선택
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:top_k]
            
            logger.info(f"🔍 검색 완료: {len(results)}개 문서 (쿼리: {query[:50]}...)")
            return results
            
        except Exception as e:
            logger.error(f"❌ 문서 검색 실패: {e}")
            return []
    
    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """코사인 유사도 계산"""
        if len(vec_a) != len(vec_b):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        magnitude_a = sum(a * a for a in vec_a) ** 0.5
        magnitude_b = sum(b * b for b in vec_b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0
        
        return dot_product / (magnitude_a * magnitude_b)
    
    def get_modpack_list(self) -> List[Dict[str, Any]]:
        """등록된 모드팩 목록 조회"""
        if not self.enabled:
            return []
        
        try:
            metadata_docs = self.db.collection('modpack_metadata').stream()
            modpacks = []
            
            for doc in metadata_docs:
                data = doc.to_dict()
                modpacks.append({
                    'modpack_name': data.get('modpack_name'),
                    'modpack_version': data.get('modpack_version'),
                    'document_count': data.get('document_count', 0),
                    'created_at': data.get('created_at'),
                    'last_updated': data.get('last_updated'),
                    'stats': data.get('stats', {})
                })
            
            return modpacks
        except Exception as e:
            logger.error(f"모드팩 목록 조회 실패: {e}")
            return []
    
    def delete_modpack_index(self, modpack_name: str, modpack_version: str) -> bool:
        """모드팩 인덱스 삭제"""
        if not self.enabled:
            return False
        
        try:
            # 1. 문서 컬렉션 삭제
            collection_name = f"modpack_{modpack_name}_{modpack_version}".replace('.', '_').replace('-', '_')
            collection_ref = self.db.collection(collection_name)
            
            # 배치 삭제
            docs = list(collection_ref.stream())
            if docs:
                batch = self.db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                batch.commit()
                logger.info(f"🗑️ 컬렉션 {collection_name} 삭제 완료 ({len(docs)}개 문서)")
            
            # 2. 메타데이터 삭제
            metadata_ref = self.db.collection('modpack_metadata').document(f"{modpack_name}_{modpack_version}")
            metadata_ref.delete()
            
            return True
        except Exception as e:
            logger.error(f"모드팩 인덱스 삭제 실패: {e}")
            return False


# 전역 인스턴스
gcp_rag = GCPRAGSystem()