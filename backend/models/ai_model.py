import os
import json
import logging
from typing import List, Dict, Optional, Tuple
import openai
import anthropic
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self, recipe_manager=None, language_mapper=None):
        """AI 모델을 초기화합니다."""
        self.provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.model_name = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        self.recipe_manager = recipe_manager
        self.language_mapper = language_mapper
        
        if self.provider == 'openai':
            self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        elif self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        else:
            raise ValueError(f"지원하지 않는 AI 제공자: {self.provider}")
        
        # 모드팩 전문가 프롬프트 템플릿
        self.system_prompt = self._load_system_prompt()
        
        logger.info(f"AI 모델 초기화 완료: {self.provider} - {self.model_name}")
    
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

이전 대화 기록을 참고하여 일관성 있는 답변을 제공하세요."""
        
        return base_prompt
    
    def _extract_item_names(self, message: str) -> List[str]:
        """메시지에서 아이템명을 추출합니다."""
        # 간단한 패턴 매칭 (실제로는 더 정교한 NLP 사용 가능)
        item_patterns = [
            r'(\w+)_(\w+)',  # snake_case
            r'([A-Z][a-z]+)([A-Z][a-z]+)',  # CamelCase
            r'([가-힣]+)',  # 한글 아이템명
        ]
        
        items = []
        for pattern in item_patterns:
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple):
                    items.extend(match)
                else:
                    items.append(match)
        
        return list(set(items))  # 중복 제거
    
    def _translate_korean_to_english(self, korean_name: str, modpack_name: str, user_uuid: str = None) -> Tuple[Optional[str], float, str]:
        """한글 아이템명을 영어로 변환합니다 (하이브리드 방식)."""
        if not self.language_mapper:
            return None, 0.0, "no_mapper"
        
        # 하이브리드 방식 사용
        english_name, confidence, source = self.language_mapper.find_english_name_hybrid(
            korean_name, modpack_name, user_uuid, self
        )
        
        if english_name and confidence > 0.5:
            # 사용 횟수 업데이트
            self.language_mapper.update_usage_count(korean_name, english_name)
            return english_name, confidence, source
        
        return None, confidence, source
    
    def _generate_ai_translation(self, korean_name: str, modpack_name: str, context_items: List[str]) -> Optional[str]:
        """AI를 사용하여 한글을 영어로 변환합니다."""
        try:
            prompt = f"""
당신은 마인크래프트 모드팩 전문가입니다. 한글 아이템명을 정확한 영어 아이템명으로 변환해주세요.

모드팩: {modpack_name}
한글 아이템명: {korean_name}

사용 가능한 영어 아이템명들 (일부):
{', '.join(context_items[:30])}

규칙:
1. 정확한 영어 아이템명만 답변
2. 확실하지 않으면 "UNKNOWN" 답변
3. 답변은 영어 아이템명만 (설명 없이)
4. snake_case 형식 사용 (예: iron_ingot, diamond_sword)

답변:
"""
            
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.1  # 낮은 온도로 정확성 향상
                )
                result = response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=50,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text.strip()
            else:
                return None
            
            # "UNKNOWN"이 아닌 경우에만 반환
            if result and result.upper() != "UNKNOWN":
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"AI 번역 오류: {e}")
            return None
    
    def _get_relevant_context(self, message: str, modpack_name: str, modpack_version: str = "1.0", user_uuid: str = None) -> str:
        """질문과 관련된 컨텍스트 정보를 가져옵니다."""
        if not self.recipe_manager:
            return ""
        
        context_parts = []
        translation_info = []
        
        # 1. 아이템명 추출
        item_names = self._extract_item_names(message)
        
        # 2. 한글-영어 변환 및 관련 정보 수집
        for item_name in item_names:
            # 한글로 추출된 경우 영어로 변환 시도
            if re.search(r'[가-힣]', item_name):
                english_name, confidence, source = self._translate_korean_to_english(
                    item_name, modpack_name, user_uuid
                )
                
                if english_name:
                    translation_info.append(f"'{item_name}' → '{english_name}' (신뢰도: {confidence:.1f})")
                    search_name = english_name
                else:
                    # 변환 실패 시 원본 사용
                    search_name = item_name
                    if confidence < 0.3:  # 매우 낮은 신뢰도
                        context_parts.append(f"⚠️ '{item_name}'의 영어 이름을 찾을 수 없습니다. 정확한 영어 이름을 입력해주세요.")
                        continue
            else:
                search_name = item_name
            
            # 3. 버전별 제작법 정보 수집
            recipe = self.recipe_manager.get_recipe_with_version_fallback(
                search_name, modpack_name, modpack_version
            )
            if recipe:
                context_parts.append(f"제작법 정보 - {search_name}: {json.dumps(recipe, ensure_ascii=False)}")
                
                # 버전 경고가 있으면 추가
                if recipe.get('version_warning'):
                    context_parts.append(f"버전 정보: {recipe['version_warning']}")
            
            # 4. 버전별 아이템 정보 수집
            item_info = self.recipe_manager.get_item_info_with_version_fallback(
                search_name, modpack_name, modpack_version
            )
            if item_info:
                context_parts.append(f"아이템 정보 - {search_name}: {json.dumps(item_info, ensure_ascii=False)}")
                
                # 버전 경고가 있으면 추가
                if item_info.get('version_warning'):
                    context_parts.append(f"버전 정보: {item_info['version_warning']}")
        
        # 5. 모드팩 기본 정보 (간단하게)
        modpack_stats = self.recipe_manager.get_modpack_stats(modpack_name)
        if modpack_stats:
            context_parts.append(f"모드팩 정보: {modpack_stats.get('mod_count', 0)}개 모드, {modpack_stats.get('recipe_count', 0)}개 제작법")
        
        # 6. 번역 정보 추가
        if translation_info:
            context_parts.append(f"번역 정보: {'; '.join(translation_info)}")
        
        return "\n".join(context_parts) if context_parts else "모드팩 기본 정보만 사용 가능합니다."
    
    def generate_response(
        self, 
        message: str, 
        chat_history: List[Dict] = None, 
        modpack_name: str = "unknown",
        modpack_version: str = "1.0",
        user_uuid: str = None
    ) -> str:
        """AI 응답을 생성합니다."""
        try:
            if chat_history is None:
                chat_history = []
            
            # 질문과 관련된 컨텍스트 정보 가져오기
            context_info = self._get_relevant_context(message, modpack_name, modpack_version, user_uuid)
            
            # 시스템 프롬프트에 모드팩 정보와 컨텍스트 추가
            system_prompt = self.system_prompt.format(
                modpack_name=modpack_name,
                modpack_version=modpack_version,
                context_info=context_info
            )
            
            if self.provider == 'openai':
                return self._generate_openai_response(message, chat_history, system_prompt)
            elif self.provider == 'anthropic':
                return self._generate_anthropic_response(message, chat_history, system_prompt)
            else:
                raise ValueError(f"지원하지 않는 AI 제공자: {self.provider}")
                
        except Exception as e:
            logger.error(f"AI 응답 생성 중 오류: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_openai_response(
        self, 
        message: str, 
        chat_history: List[Dict], 
        system_prompt: str
    ) -> str:
        """OpenAI API를 사용하여 응답을 생성합니다."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                messages = [{"role": "system", "content": system_prompt}]
                
                # 이전 대화 기록 추가
                for msg in chat_history[-10:]:  # 최근 10개 메시지만 사용
                    if msg.get('user_message'):
                        messages.append({"role": "user", "content": msg['user_message']})
                    if msg.get('ai_response'):
                        messages.append({"role": "assistant", "content": msg['ai_response']})
                
                # 현재 메시지 추가
                messages.append({"role": "user", "content": message})
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=30  # 30초 타임아웃
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"OpenAI API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                else:
                    logger.error(f"OpenAI API 최대 재시도 횟수 초과: {e}")
                    return "죄송합니다. AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _generate_anthropic_response(
        self, 
        message: str, 
        chat_history: List[Dict], 
        system_prompt: str
    ) -> str:
        """Anthropic API를 사용하여 응답을 생성합니다."""
        # 대화 기록을 문자열로 변환
        conversation = system_prompt + "\n\n"
        
        for msg in chat_history[-10:]:
            if msg.get('user_message'):
                conversation += f"사용자: {msg['user_message']}\n"
            if msg.get('ai_response'):
                conversation += f"AI: {msg['ai_response']}\n"
        
        conversation += f"사용자: {message}\nAI:"
        
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": conversation}]
        )
        
        return response.content[0].text.strip()
    
    def get_recipe_analysis(self, recipe_data: Dict) -> str:
        """제작법 데이터를 분석하여 설명을 생성합니다."""
        try:
            prompt = f"""
다음 마인크래프트 아이템의 제작법을 분석하여 설명해주세요:

아이템명: {recipe_data.get('item_name', '알 수 없음')}
재료: {recipe_data.get('ingredients', [])}
결과물: {recipe_data.get('result', {})}
모드: {recipe_data.get('mod', '알 수 없음')}

다음 형식으로 답변해주세요:
1. 아이템 설명
2. 제작법 설명
3. 사용법 및 팁
4. 관련 아이템이나 발전 과정
"""
            
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=800,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
                
        except Exception as e:
            logger.error(f"제작법 분석 오류: {e}")
            return "제작법 분석 중 오류가 발생했습니다." 