import os
import json
import logging
from typing import List, Dict, Optional, Tuple
import openai
import anthropic
import google.generativeai as genai
from datetime import datetime
import re
import requests
from google.cloud import aiplatform
from google.cloud import storage
import vertexai
from vertexai.language_models import TextGenerationModel
from vertexai.vision_models import ImageGenerationModel

logger = logging.getLogger(__name__)

class HybridAIModel:
    def __init__(self, recipe_manager=None, language_mapper=None, rag_manager=None):
        """하이브리드 AI 모델을 초기화합니다."""
        self.recipe_manager = recipe_manager
        self.language_mapper = language_mapper
        self.rag_manager = rag_manager
        
        # GCP 설정 (기본 활성화)
        self.gcp_project_id = os.getenv('GCP_PROJECT_ID')
        self.gcs_bucket_name = os.getenv('GCS_BUCKET_NAME')
        
        if not self.gcp_project_id or not self.gcs_bucket_name:
            logger.warning("GCP 설정이 없습니다. RAG 기능이 제한됩니다.")
        
        # AI 모델 설정
        self.available_models = self._get_available_models()
        self.current_model = os.getenv('DEFAULT_AI_MODEL', 'gemini-pro')  # Gemini Pro를 기본 모델로 설정
        
        # AI 클라이언트들 초기화
        self.clients = self._init_ai_clients()
        
        # 시스템 프롬프트 템플릿
        self.system_prompt = self._load_system_prompt()
        
        logger.info(f"하이브리드 AI 모델 초기화 완료. 사용 가능한 모델: {list(self.available_models.keys())}")
    
    def _get_available_models(self) -> Dict:
        """사용 가능한 AI 모델들을 정의합니다."""
        return {
            'gemini-pro': {
                'name': 'Gemini Pro (웹검색)',
                'provider': 'google',
                'free_tier': True,
                'web_search': True,  # 웹검색 항상 활성화
                'max_tokens': 8192,
                'cost_per_1k_tokens': 0.0005,
                'description': 'Google의 최신 AI 모델 (웹검색 포함, GCP 크레딧 사용)',
                'is_main': True  # 메인 모델로 표시
            },
            'gpt-3.5-turbo': {
                'name': 'GPT-3.5 Turbo (무료)',
                'provider': 'openai',
                'free_tier': True,
                'web_search': False,  # 웹검색 비활성화
                'max_tokens': 4096,
                'cost_per_1k_tokens': 0.002,
                'description': '빠르고 효율적인 OpenAI 모델 (무료 티어)',
                'is_main': False
            },
            'claude-3-haiku': {
                'name': 'Claude 3 Haiku (무료)',
                'provider': 'anthropic',
                'free_tier': True,
                'web_search': False,  # 웹검색 비활성화
                'max_tokens': 4096,
                'cost_per_1k_tokens': 0.00025,
                'description': '빠르고 경제적인 Anthropic 모델 (무료 티어)',
                'is_main': False
            },
            # 유료 모델들 (나중에 활성화 가능)
            'gpt-4': {
                'name': 'GPT-4 (유료)',
                'provider': 'openai',
                'free_tier': False,
                'web_search': True,
                'max_tokens': 8192,
                'cost_per_1k_tokens': 0.03,
                'description': '고성능 OpenAI 모델 (유료)',
                'is_main': False,
                'enabled': False  # 기본적으로 비활성화
            },
            'claude-3-sonnet': {
                'name': 'Claude 3 Sonnet (유료)',
                'provider': 'anthropic',
                'free_tier': False,
                'web_search': True,
                'max_tokens': 4096,
                'cost_per_1k_tokens': 0.003,
                'description': '균형잡힌 성능의 Anthropic 모델 (유료)',
                'is_main': False,
                'enabled': False  # 기본적으로 비활성화
            }
        }
    
    def _init_ai_clients(self) -> Dict:
        """AI 클라이언트들을 초기화합니다."""
        clients = {}
        
        try:
            # OpenAI 클라이언트
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                clients['openai'] = openai.OpenAI(api_key=openai_api_key)
                logger.info("OpenAI 클라이언트 초기화 완료")
            else:
                logger.warning("OpenAI API 키가 설정되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {e}")
        
        try:
            # Anthropic 클라이언트
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_api_key:
                clients['anthropic'] = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Anthropic 클라이언트 초기화 완료")
            else:
                logger.warning("Anthropic API 키가 설정되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"Anthropic 클라이언트 초기화 실패: {e}")
        
        try:
            # Google Gemini 클라이언트
            google_api_key = os.getenv('GOOGLE_API_KEY')
            if google_api_key:
                genai.configure(api_key=google_api_key)
                clients['google'] = genai
                logger.info("Google Gemini 클라이언트 초기화 완료")
            else:
                logger.warning("Google API 키가 설정되지 않았습니다.")
        
        except Exception as e:
            logger.error(f"Google Gemini 클라이언트 초기화 실패: {e}")
        
        return clients
    
    def get_available_models_info(self) -> List[Dict]:
        """사용 가능한 모델 정보를 반환합니다."""
        models_info = []
        
        for model_id, model_info in self.available_models.items():
            provider = model_info['provider']
            is_available = provider in self.clients
            
            models_info.append({
                'id': model_id,
                'name': model_info['name'],
                'provider': provider,
                'free_tier': model_info['free_tier'],
                'description': model_info['description'],
                'available': is_available,
                'current': model_id == self.current_model
            })
        
        return models_info
    
    def switch_model(self, model_id: str) -> bool:
        """AI 모델을 전환합니다."""
        if model_id not in self.available_models:
            logger.error(f"지원하지 않는 모델: {model_id}")
            return False
        
        provider = self.available_models[model_id]['provider']
        if provider not in self.clients:
            logger.error(f"모델 {model_id}의 클라이언트가 초기화되지 않았습니다.")
            return False
        
        self.current_model = model_id
        logger.info(f"AI 모델을 {model_id}로 전환했습니다.")
        return True
    
    def _load_system_prompt(self) -> str:
        """시스템 프롬프트를 로드합니다."""
        base_prompt = """당신은 마인크래프트 모드팩 전문가 AI 어시스턴트입니다.

주요 역할:
1. 모드팩 관련 질문에 정확하고 도움이 되는 답변 제공
2. 아이템 제작법, 사용법, 획득 방법 등 상세 정보 제공
3. 모드팩 간의 상호작용과 최적화 방법 안내
4. 플레이어의 진행 상황에 맞는 조언 제공

답변 규칙:
- 항상 한국어로 답변
- 구체적이고 실용적인 정보 제공
- 게임 내 아이템명은 정확히 표기
- 복잡한 내용은 단계별로 설명
- 친근하고 도움이 되는 톤 유지

현재 모드팩: {modpack_name}
모드팩 버전: {modpack_version}

{context_info}

{rag_context}

{web_search_context}

이전 대화 기록을 참고하여 일관성 있는 답변을 제공하세요."""
        
        return base_prompt
    
    def _get_local_context(self, message: str, modpack_name: str, modpack_version: str = "1.0", user_uuid: str = None) -> str:
        """로컬 데이터베이스에서 컨텍스트를 가져옵니다."""
        if not self.recipe_manager:
            return ""
        
        context_parts = []
        translation_info = []
        
        # 아이템명 추출 및 변환
        item_names = self._extract_item_names(message)
        
        for item_name in item_names:
            if re.search(r'[가-힣]', item_name):
                english_name, confidence, source = self._translate_korean_to_english(
                    item_name, modpack_name, user_uuid
                )
                
                if english_name:
                    translation_info.append(f"'{item_name}' → '{english_name}' (신뢰도: {confidence:.1f})")
                    search_name = english_name
                else:
                    search_name = item_name
                    if confidence < 0.3:
                        context_parts.append(f"⚠️ '{item_name}'의 영어 이름을 찾을 수 없습니다.")
                        continue
            else:
                search_name = item_name
            
            # 로컬 제작법 정보
            recipe = self.recipe_manager.get_recipe_with_version_fallback(
                search_name, modpack_name, modpack_version
            )
            if recipe:
                context_parts.append(f"로컬 제작법 - {search_name}: {json.dumps(recipe, ensure_ascii=False)}")
            
            # 로컬 아이템 정보
            item_info = self.recipe_manager.get_item_info_with_version_fallback(
                search_name, modpack_name, modpack_version
            )
            if item_info:
                context_parts.append(f"로컬 아이템 정보 - {search_name}: {json.dumps(item_info, ensure_ascii=False)}")
        
        # 번역 정보 추가
        if translation_info:
            context_parts.append(f"번역 정보: {'; '.join(translation_info)}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _get_rag_context(self, message: str, modpack_name: str) -> str:
        """GCP RAG에서 컨텍스트를 가져옵니다. (필수)"""
        if not self.rag_manager:
            logger.error("❌ RAG 매니저가 초기화되지 않았습니다!")
            raise RuntimeError("RAG 매니저가 필수이지만 초기화되지 않았습니다.")
        
        try:
            # RAG 매니저를 통한 검색
            relevant_docs = self.rag_manager.search_similar_documents(message, modpack_name, top_k=3)
            
            if relevant_docs:
                logger.info(f"✅ RAG에서 {len(relevant_docs)}개 문서 검색됨")
                return f"RAG 정보:\n{json.dumps(relevant_docs, ensure_ascii=False)}"
            else:
                logger.warning(f"⚠️ RAG에서 관련 문서를 찾을 수 없음: {message}")
                return "RAG 정보: 관련 문서를 찾을 수 없습니다."
            
        except Exception as e:
            logger.error(f"❌ RAG 컨텍스트 조회 오류: {e}")
            raise RuntimeError(f"RAG 컨텍스트 조회 실패: {e}")
    
    def _get_web_search_context(self, message: str, modpack_name: str) -> str:
        """AI 웹검색을 통해 컨텍스트를 가져옵니다."""
        try:
            # AI에게 웹검색 요청
            search_prompt = f"""
다음 마인크래프트 모드팩 관련 정보를 웹에서 검색해주세요:

모드팩: {modpack_name}
질문: {message}

검색해야 할 키워드:
1. "{modpack_name}" 마인크래프트 모드팩
2. 관련 아이템명이나 모드명
3. 제작법, 사용법, 가이드

신뢰할 수 있는 사이트에서만 검색하고, 검색 결과를 요약해서 제공해주세요.
"""
            
            # 현재 모델의 제공자 확인
            provider = self.available_models[self.current_model]['provider']
            
            if provider == 'openai':
                return self._openai_web_search(search_prompt)
            elif provider == 'anthropic':
                return self._anthropic_web_search(search_prompt)
            elif provider == 'google':
                return self._google_web_search(search_prompt)
            else:
                return ""
            
        except Exception as e:
            logger.error(f"웹검색 컨텍스트 조회 오류: {e}")
            return ""
    
    def _openai_web_search(self, search_prompt: str) -> str:
        """OpenAI를 사용한 웹검색."""
        try:
            response = self.clients['openai'].chat.completions.create(
                model=self.current_model,
                messages=[{"role": "user", "content": search_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            return f"웹검색 결과:\n{response.choices[0].message.content.strip()}"
        except Exception as e:
            logger.error(f"OpenAI 웹검색 실패: {e}")
            return ""
    
    def _anthropic_web_search(self, search_prompt: str) -> str:
        """Anthropic을 사용한 웹검색."""
        try:
            response = self.clients['anthropic'].messages.create(
                model=self.current_model,
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": search_prompt}]
            )
            return f"웹검색 결과:\n{response.content[0].text.strip()}"
        except Exception as e:
            logger.error(f"Anthropic 웹검색 실패: {e}")
            return ""
    
    def _google_web_search(self, search_prompt: str) -> str:
        """Google Gemini를 사용한 웹검색."""
        try:
            # Gemini Pro with web search
            model = self.clients['google'].GenerativeModel('gemini-pro')
            
            # 웹검색을 위한 특별한 프롬프트 구성
            web_search_prompt = f"""
다음 마인크래프트 모드팩 관련 질문에 대해 웹에서 최신 정보를 검색하여 답변해주세요:

{search_prompt}

검색할 때 다음 사이트들을 우선적으로 참고해주세요:
- CurseForge (모드팩 정보)
- MinecraftWiki (기본 정보)
- Reddit r/feedthebeast (커뮤니티)
- 공식 모드 문서

검색 결과를 바탕으로 정확하고 신뢰할 수 있는 정보를 제공해주세요.
"""
            
            response = model.generate_content(
                web_search_prompt,
                generation_config={
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 800,
                }
            )
            
            if response.text:
                logger.info("✅ Gemini Pro 웹검색 완료")
                return f"웹검색 결과 (Gemini Pro):\n{response.text.strip()}"
            else:
                logger.warning("⚠️ Gemini Pro 웹검색 결과가 비어있음")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Google 웹검색 실패: {e}")
            return ""
    
    def _translate_korean_to_english(self, korean_name: str, modpack_name: str, user_uuid: str = None) -> Tuple[Optional[str], float, str]:
        """한글 아이템명을 영어로 변환합니다."""
        if not self.language_mapper:
            return None, 0.0, "no_mapper"
        
        english_name, confidence, source = self.language_mapper.find_english_name_hybrid(
            korean_name, modpack_name, user_uuid, self
        )
        
        if english_name and confidence > 0.5:
            self.language_mapper.update_usage_count(korean_name, english_name)
            return english_name, confidence, source
        
        return None, confidence, source
    
    def _extract_korean_items(self, message: str) -> List[str]:
        """메시지에서 한글 아이템명을 추출합니다."""
        korean_pattern = r'[가-힣]+'
        korean_items = re.findall(korean_pattern, message)
        
        # 의미있는 한글 단어만 필터링 (1글자 제외)
        meaningful_items = [item for item in korean_items if len(item) > 1]
        
        return list(set(meaningful_items))
    
    def _extract_item_names(self, message: str) -> List[str]:
        """메시지에서 아이템명을 추출합니다."""
        item_patterns = [
            r'(\w+)_(\w+)',
            r'([A-Z][a-z]+)([A-Z][a-z]+)',
            r'([가-힣]+)',
        ]
        
        items = []
        for pattern in item_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple):
                    items.extend(match)
                else:
                    items.append(match)
        
        return list(set(items))
    
    def _format_response_with_korean(self, response: str, translation_mapping: Dict[str, str]) -> str:
        """응답에서 영어 아이템명을 한글(영어) 형식으로 변환합니다."""
        if not translation_mapping:
            return response
        
        formatted_response = response
        
        # 영어 아이템명을 한글(영어) 형식으로 변환
        for korean, english in translation_mapping.items():
            # 영어 이름이 응답에 포함되어 있는지 확인
            if english in formatted_response:
                # 첫 번째 등장만 변환 (중복 방지)
                formatted_response = formatted_response.replace(
                    english, 
                    f"{korean}({english})", 
                    1
                )
        
        return formatted_response
    
    def generate_response(
        self, 
        message: str, 
        chat_history: List[Dict] = None, 
        modpack_name: str = "unknown",
        modpack_version: str = "1.0",
        user_uuid: str = None
    ) -> str:
        """하이브리드 AI 응답을 생성합니다."""
        try:
            if chat_history is None:
                chat_history = []
            
            # 한글 아이템명 감지 및 변환
            korean_items = self._extract_korean_items(message)
            translation_mapping = {}
            
            for korean_item in korean_items:
                english_name, confidence, source = self._translate_korean_to_english(
                    korean_item, modpack_name, user_uuid
                )
                if english_name and confidence > 0.5:
                    translation_mapping[korean_item] = english_name
            
            # 변환된 영어 이름으로 메시지 업데이트
            processed_message = message
            for korean, english in translation_mapping.items():
                processed_message = processed_message.replace(korean, english)
            
            # 1. 로컬 컨텍스트 (빠른 응답)
            local_context = self._get_local_context(processed_message, modpack_name, modpack_version, user_uuid)
            
            # 2. RAG 컨텍스트 (필수 - 상세 정보)
            rag_context = self._get_rag_context(processed_message, modpack_name)
            
            # 3. 웹검색 컨텍스트 (Gemini Pro에서 항상 활성화)
            web_context = ""
            current_model_info = self.available_models.get(self.current_model, {})
            web_search_enabled = current_model_info.get('web_search', False)
            
            if web_search_enabled:
                logger.info(f"🌐 {self.current_model}에서 웹검색을 활성화합니다.")
                web_context = self._get_web_search_context(processed_message, modpack_name)
            else:
                logger.info(f"📖 {self.current_model}에서는 웹검색을 사용하지 않습니다.")
            
            # 시스템 프롬프트 구성
            system_prompt = self.system_prompt.format(
                modpack_name=modpack_name,
                modpack_version=modpack_version,
                context_info=local_context,
                rag_context=rag_context,
                web_search_context=web_context
            )
            
            # AI 응답 생성
            provider = self.available_models[self.current_model]['provider']
            
            if provider == 'openai':
                ai_response = self._generate_openai_response(processed_message, chat_history, system_prompt)
            elif provider == 'anthropic':
                ai_response = self._generate_anthropic_response(processed_message, chat_history, system_prompt)
            elif provider == 'google':
                ai_response = self._generate_google_response(processed_message, chat_history, system_prompt)
            else:
                raise ValueError(f"지원하지 않는 AI 제공자: {provider}")
            
            # 응답에서 영어 아이템명을 한글(영어) 형식으로 변환
            formatted_response = self._format_response_with_korean(ai_response, translation_mapping)
            
            return formatted_response
                
        except Exception as e:
            logger.error(f"하이브리드 AI 응답 생성 중 오류: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_openai_response(self, message: str, chat_history: List[Dict], system_prompt: str) -> str:
        """OpenAI API를 사용하여 응답을 생성합니다."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                messages = [{"role": "system", "content": system_prompt}]
                
                # 이전 대화 기록 추가
                for msg in chat_history[-10:]:
                    if msg.get('user_message'):
                        messages.append({"role": "user", "content": msg['user_message']})
                    if msg.get('ai_response'):
                        messages.append({"role": "assistant", "content": msg['ai_response']})
                
                # 현재 메시지 추가
                messages.append({"role": "user", "content": message})
                
                response = self.clients['openai'].chat.completions.create(
                    model=self.current_model,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=30
                )
                
                return response.choices[0].message.content.strip()
                
            except openai.RateLimitError as e:
                logger.warning(f"OpenAI 무료 크레딧 소진 또는 속도 제한: {e}")
                return "⚠️ OpenAI의 무료 크레딧이 소진되었습니다. 다른 AI 모델을 선택해주세요. (/modpackai models)"
            except openai.AuthenticationError as e:
                logger.error(f"OpenAI 인증 오류: {e}")
                return "⚠️ OpenAI API 키에 문제가 있습니다. 다른 AI 모델을 선택해주세요."
            except Exception as e:
                logger.warning(f"OpenAI API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"OpenAI API 최대 재시도 횟수 초과: {e}")
                    return "죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_anthropic_response(self, message: str, chat_history: List[Dict], system_prompt: str) -> str:
        """Anthropic API를 사용하여 응답을 생성합니다."""
        try:
            conversation = system_prompt + "\n\n"
            
            for msg in chat_history[-10:]:
                if msg.get('user_message'):
                    conversation += f"사용자: {msg['user_message']}\n"
                if msg.get('ai_response'):
                    conversation += f"AI: {msg['ai_response']}\n"
            
            conversation += f"사용자: {message}\nAI:"
            
            response = self.clients['anthropic'].messages.create(
                model=self.current_model,
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": conversation}]
            )
            
            return response.content[0].text.strip()
            
        except anthropic.RateLimitError as e:
            logger.warning(f"Anthropic 무료 크레딧 소진 또는 속도 제한: {e}")
            return "⚠️ Anthropic의 무료 크레딧이 소진되었습니다. 다른 AI 모델을 선택해주세요. (/modpackai models)"
        except anthropic.AuthenticationError as e:
            logger.error(f"Anthropic 인증 오류: {e}")
            return "⚠️ Anthropic API 키에 문제가 있습니다. 다른 AI 모델을 선택해주세요."
        except Exception as e:
            logger.error(f"Anthropic API 호출 실패: {e}")
            return "죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_google_response(self, message: str, chat_history: List[Dict], system_prompt: str) -> str:
        """Google Gemini API를 사용하여 응답을 생성합니다."""
        try:
            model = self.clients['google'].GenerativeModel('gemini-pro')
            
            # 대화 기록 구성
            chat = model.start_chat(history=[])
            
            # 시스템 프롬프트와 대화 기록 추가
            full_prompt = system_prompt + "\n\n"
            for msg in chat_history[-10:]:
                if msg.get('user_message'):
                    full_prompt += f"사용자: {msg['user_message']}\n"
                if msg.get('ai_response'):
                    full_prompt += f"AI: {msg['ai_response']}\n"
            
            full_prompt += f"사용자: {message}"
            
            response = chat.send_message(full_prompt)
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "limit" in error_msg:
                logger.warning(f"Google Gemini 무료 크레딧 소진: {e}")
                return "⚠️ Google Gemini의 무료 크레딧이 소진되었습니다. 다른 AI 모델을 선택해주세요. (/modpackai models)"
            elif "authentication" in error_msg or "api_key" in error_msg:
                logger.error(f"Google Gemini 인증 오류: {e}")
                return "⚠️ Google API 키에 문제가 있습니다. 다른 AI 모델을 선택해주세요."
            else:
                logger.error(f"Google Gemini API 호출 실패: {e}")
                return "죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요." 