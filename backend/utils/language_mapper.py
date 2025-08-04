import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class LanguageMapper:
    def __init__(self, db_path: str = "language_mappings.db"):
        """언어 매퍼를 초기화합니다."""
        self.db_path = db_path
        self._init_database()
        self._load_common_mappings()
    
    def _init_database(self):
        """언어 매핑 데이터베이스를 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 한글-영어 매핑 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS item_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        korean_name TEXT NOT NULL,
                        english_name TEXT NOT NULL,
                        mod_name TEXT,
                        confidence_score REAL DEFAULT 1.0,
                        usage_count INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(korean_name, english_name, mod_name)
                    )
                ''')
                
                # 모드별 매핑 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS mod_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mod_name TEXT NOT NULL,
                        korean_prefix TEXT,
                        english_prefix TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 사용자 정의 매핑 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS custom_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        korean_name TEXT NOT NULL,
                        english_name TEXT NOT NULL,
                        modpack_name TEXT,
                        user_uuid TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(korean_name, english_name, modpack_name, user_uuid)
                    )
                ''')
                
                conn.commit()
                logger.info("언어 매핑 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"언어 매핑 데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_common_mappings(self):
        """일반적인 마인크래프트 아이템 매핑을 로드합니다."""
        common_mappings = {
            # 기본 아이템들
            "다이아몬드": "diamond",
            "철": "iron",
            "금": "gold",
            "석탄": "coal",
            "검": "sword",
            "도끼": "axe",
            "곡괭이": "pickaxe",
            "삽": "shovel",
            "괭이": "hoe",
            "블록": "block",
            "원석": "ore",
            "괴": "ingot",
            "가루": "dust",
            "조각": "nugget",
            "보석": "gem",
            "결정": "crystal",
            "기계": "machine",
            "발전기": "generator",
            "저장소": "storage",
            "파이프": "pipe",
            "케이블": "cable",
            "전선": "wire",
            "배터리": "battery",
            "셀": "cell",
            "탱크": "tank",
            "드럼": "drum",
            "상자": "chest",
            "가방": "bag",
            "백": "backpack",
            "도구": "tool",
            "무기": "weapon",
            "방어구": "armor",
            "헬멧": "helmet",
            "흉갑": "chestplate",
            "각반": "leggings",
            "부츠": "boots",
            "반지": "ring",
            "목걸이": "necklace",
            "팔찌": "bracelet",
            "마법서": "grimoire",
            "지팡이": "staff",
            "완드": "wand",
            "포션": "potion",
            "물약": "potion",
            "약물": "drug",
            "음식": "food",
            "씨앗": "seed",
            "묘목": "sapling",
            "나무": "tree",
            "꽃": "flower",
            "풀": "grass",
            "잎": "leaves",
            "나뭇잎": "leaves",
            "흙": "dirt",
            "모래": "sand",
            "자갈": "gravel",
            "돌": "stone",
            "화강암": "granite",
            "섬록암": "diorite",
            "안산암": "andesite",
            "유리": "glass",
            "양털": "wool",
            "가죽": "leather",
            "끈": "string",
            "실": "string",
            "종이": "paper",
            "책": "book",
            "벽돌": "brick",
            "시멘트": "concrete",
            "플라스틱": "plastic",
            "고무": "rubber",
            "알루미늄": "aluminum",
            "구리": "copper",
            "주석": "tin",
            "납": "lead",
            "은": "silver",
            "백금": "platinum",
            "티타늄": "titanium",
            "크롬": "chrome",
            "니켈": "nickel",
            "아연": "zinc",
            "우라늄": "uranium",
            "플루토늄": "plutonium",
            "토륨": "thorium",
            "리튬": "lithium",
            "나트륨": "sodium",
            "칼륨": "potassium",
            "칼슘": "calcium",
            "마그네슘": "magnesium",
            "망간": "manganese",
            "코발트": "cobalt",
            "바나듐": "vanadium",
            "몰리브덴": "molybdenum",
            "텅스텐": "tungsten",
            "니오븀": "niobium",
            "탄탈럼": "tantalum",
            "레늄": "rhenium",
            "오스뮴": "osmium",
            "이리듐": "iridium",
            "팔라듐": "palladium",
            "로듐": "rhodium",
            "루테늄": "ruthenium",
            "레늄": "rhenium",
            "텔루륨": "tellurium",
            "셀레늄": "selenium",
            "비소": "arsenic",
            "안티몬": "antimony",
            "비스무트": "bismuth",
            "폴로늄": "polonium",
            "아스타틴": "astatine",
            "라돈": "radon",
            "프란슘": "francium",
            "라듐": "radium",
            "악티늄": "actinium",
            "토륨": "thorium",
            "프로탁티늄": "protactinium",
            "우라늄": "uranium",
            "넵투늄": "neptunium",
            "플루토늄": "plutonium",
            "아메리슘": "americium",
            "퀴륨": "curium",
            "버클륨": "berkelium",
            "캘리포늄": "californium",
            "아인슈타이늄": "einsteinium",
            "페르뮴": "fermium",
            "멘델레븀": "mendelevium",
            "노벨륨": "nobelium",
            "로렌슘": "lawrencium",
        }
        
        # 데이터베이스에 저장
        for korean, english in common_mappings.items():
            self.add_mapping(korean, english, "minecraft")
    
    def add_mapping(self, korean_name: str, english_name: str, mod_name: str = None):
        """새로운 매핑을 추가합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO item_mappings 
                    (korean_name, english_name, mod_name, usage_count)
                    VALUES (?, ?, ?, COALESCE((SELECT usage_count FROM item_mappings WHERE korean_name = ? AND english_name = ?), 0))
                ''', (korean_name, english_name, mod_name, korean_name, english_name))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"매핑 추가 오류: {e}")
    
    def find_english_name(self, korean_name: str, modpack_name: str = None, user_uuid: str = None) -> Tuple[Optional[str], float, str]:
        """한글 이름에 해당하는 영어 이름을 찾습니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. 사용자 정의 매핑 먼저 확인
                if user_uuid and modpack_name:
                    cursor.execute('''
                        SELECT english_name FROM custom_mappings
                        WHERE korean_name = ? AND modpack_name = ? AND user_uuid = ?
                    ''', (korean_name, modpack_name, user_uuid))
                    
                    row = cursor.fetchone()
                    if row:
                        return row[0], 1.0, "custom"
                
                # 2. 일반 매핑에서 확인
                cursor.execute('''
                    SELECT english_name, confidence_score, usage_count
                    FROM item_mappings
                    WHERE korean_name = ?
                    ORDER BY confidence_score DESC, usage_count DESC
                ''', (korean_name,))
                
                rows = cursor.fetchall()
                if rows:
                    best_match = rows[0]
                    return best_match[0], best_match[1], "mapped"
                
                # 3. 부분 매칭 시도
                partial_matches = self._find_partial_matches(korean_name)
                if partial_matches:
                    best_match = max(partial_matches, key=lambda x: x[1])
                    if best_match[1] > 0.7:  # 70% 이상 유사도
                        return best_match[0], best_match[1], "partial"
                
                return None, 0.0, "not_found"
                
        except Exception as e:
            logger.error(f"영어 이름 찾기 오류: {e}")
            return None, 0.0, "error"
    
    def find_english_name_hybrid(self, korean_name: str, modpack_name: str = None, user_uuid: str = None, ai_model = None) -> Tuple[Optional[str], float, str]:
        """하이브리드 방식으로 한글 이름에 해당하는 영어 이름을 찾습니다."""
        try:
            # 1. 사용자 정의 매핑 (최우선)
            if user_uuid and modpack_name:
                english_name, confidence, source = self._check_custom_mapping(korean_name, modpack_name, user_uuid)
                if english_name:
                    return english_name, confidence, source
            
            # 2. 일반 매핑 데이터베이스
            english_name, confidence, source = self._check_general_mapping(korean_name)
            if english_name and confidence > 0.7:
                return english_name, confidence, source
            
            # 3. 부분 매칭 (유사도 70% 이상)
            english_name, confidence, source = self._check_partial_matching(korean_name)
            if english_name and confidence > 0.7:
                return english_name, confidence, source
            
            # 4. AI 기반 변환 (신뢰도가 낮은 경우)
            if confidence < 0.5 and ai_model:
                english_name, confidence, source = self._check_ai_translation(korean_name, modpack_name, ai_model)
                if english_name and confidence > 0.6:
                    # AI 결과를 매핑에 저장
                    self.add_mapping(korean_name, english_name, "ai_generated")
                    return english_name, confidence, source
            
            return None, confidence, source
            
        except Exception as e:
            logger.error(f"하이브리드 영어 이름 찾기 오류: {e}")
            return None, 0.0, "error"
    
    def _check_custom_mapping(self, korean_name: str, modpack_name: str, user_uuid: str) -> Tuple[Optional[str], float, str]:
        """사용자 정의 매핑을 확인합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT english_name FROM custom_mappings
                    WHERE korean_name = ? AND modpack_name = ? AND user_uuid = ?
                ''', (korean_name, modpack_name, user_uuid))
                
                row = cursor.fetchone()
                if row:
                    return row[0], 1.0, "custom"
                
                return None, 0.0, "no_custom"
                
        except Exception as e:
            logger.error(f"사용자 정의 매핑 확인 오류: {e}")
            return None, 0.0, "error"
    
    def _check_general_mapping(self, korean_name: str) -> Tuple[Optional[str], float, str]:
        """일반 매핑을 확인합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT english_name, confidence_score, usage_count
                    FROM item_mappings
                    WHERE korean_name = ?
                    ORDER BY confidence_score DESC, usage_count DESC
                ''', (korean_name,))
                
                rows = cursor.fetchall()
                if rows:
                    best_match = rows[0]
                    return best_match[0], best_match[1], "mapped"
                
                return None, 0.0, "no_mapping"
                
        except Exception as e:
            logger.error(f"일반 매핑 확인 오류: {e}")
            return None, 0.0, "error"
    
    def _check_partial_matching(self, korean_name: str) -> Tuple[Optional[str], float, str]:
        """부분 매칭을 확인합니다."""
        try:
            partial_matches = self._find_partial_matches(korean_name)
            if partial_matches:
                best_match = max(partial_matches, key=lambda x: x[1])
                if best_match[1] > 0.7:  # 70% 이상 유사도
                    return best_match[0], best_match[1], "partial"
            
            return None, 0.0, "no_partial"
            
        except Exception as e:
            logger.error(f"부분 매칭 확인 오류: {e}")
            return None, 0.0, "error"
    
    def _check_ai_translation(self, korean_name: str, modpack_name: str, ai_model) -> Tuple[Optional[str], float, str]:
        """AI 기반 변환을 확인합니다."""
        try:
            # 컨텍스트 아이템 수집
            context_items = self.get_context_items_for_ai(modpack_name)
            
            # AI 변환 시도
            english_name = ai_model._generate_ai_translation(korean_name, modpack_name, context_items)
            
            if english_name:
                return english_name, 0.8, "ai_generated"
            
            return None, 0.0, "ai_failed"
            
        except Exception as e:
            logger.error(f"AI 변환 확인 오류: {e}")
            return None, 0.0, "ai_error"
    
    def _find_partial_matches(self, korean_name: str) -> List[Tuple[str, float]]:
        """부분 매칭을 시도합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT korean_name, english_name FROM item_mappings')
                rows = cursor.fetchall()
                
                matches = []
                for row in rows:
                    similarity = SequenceMatcher(None, korean_name, row[0]).ratio()
                    if similarity > 0.5:  # 50% 이상 유사도
                        matches.append((row[1], similarity))
                
                return matches
                
        except Exception as e:
            logger.error(f"부분 매칭 오류: {e}")
            return []
    
    def add_custom_mapping(self, korean_name: str, english_name: str, modpack_name: str, user_uuid: str):
        """사용자 정의 매핑을 추가합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO custom_mappings 
                    (korean_name, english_name, modpack_name, user_uuid)
                    VALUES (?, ?, ?, ?)
                ''', (korean_name, english_name, modpack_name, user_uuid))
                
                conn.commit()
                logger.info(f"사용자 매핑 추가: {korean_name} → {english_name}")
                
        except Exception as e:
            logger.error(f"사용자 매핑 추가 오류: {e}")
    
    def update_usage_count(self, korean_name: str, english_name: str):
        """사용 횟수를 업데이트합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE item_mappings 
                    SET usage_count = usage_count + 1
                    WHERE korean_name = ? AND english_name = ?
                ''', (korean_name, english_name))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"사용 횟수 업데이트 오류: {e}")
    
    def get_suggestions(self, partial_korean: str, limit: int = 5) -> List[str]:
        """부분 한글 이름에 대한 제안을 제공합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT DISTINCT korean_name FROM item_mappings
                    WHERE korean_name LIKE ?
                    ORDER BY usage_count DESC
                    LIMIT ?
                ''', (f'%{partial_korean}%', limit))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"제안 조회 오류: {e}")
            return [] 
    
    def analyze_modpack_for_mappings(self, modpack_analysis_result: Dict):
        """모드팩 분석 결과를 바탕으로 언어 매핑을 자동 생성합니다."""
        try:
            mappings_added = 0
            
            # 1. 아이템명에서 패턴 추출
            for item in modpack_analysis_result.get('items', []):
                item_name = item.get('item_name', '')
                display_name = item.get('display_name', '')
                
                if item_name and display_name:
                    # 영어 아이템명에서 한글 추출 시도
                    korean_name = self._extract_korean_from_display_name(display_name)
                    if korean_name:
                        self.add_mapping(korean_name, item_name, item.get('mod_name'))
                        mappings_added += 1
            
            # 2. 모드명 매핑
            for mod in modpack_analysis_result.get('mods', []):
                mod_name = mod.get('mod_name', '')
                mod_id = mod.get('mod_id', '')
                
                if mod_name and mod_id:
                    # 모드명을 한글-영어 매핑으로 저장
                    self.add_mod_mapping(mod_name, mod_id)
            
            # 3. JEI/REI 언어 파일 분석
            self._analyze_language_files(modpack_analysis_result)
            
            logger.info(f"모드팩 분석으로 {mappings_added}개의 언어 매핑 추가됨")
            return mappings_added
            
        except Exception as e:
            logger.error(f"모드팩 언어 매핑 분석 오류: {e}")
            return 0
    
    def _extract_korean_from_display_name(self, display_name: str) -> Optional[str]:
        """표시명에서 한글 부분을 추출합니다."""
        # 한글 패턴 찾기
        korean_pattern = r'[가-힣]+'
        matches = re.findall(korean_pattern, display_name)
        
        if matches:
            # 가장 긴 한글 부분 반환
            return max(matches, key=len)
        
        return None
    
    def _analyze_language_files(self, modpack_analysis_result: Dict):
        """언어 파일들을 분석하여 매핑을 생성합니다."""
        try:
            # assets/*/lang/ko_kr.json 파일들 분석
            language_files = [
                'assets/minecraft/lang/ko_kr.json',
                'assets/minecraft/lang/ko_kr.json',
                # 모드별 언어 파일들
            ]
            
            for lang_file in language_files:
                # 실제로는 ZIP에서 파일을 읽어서 분석
                # 여기서는 예시만 표시
                pass
                
        except Exception as e:
            logger.error(f"언어 파일 분석 오류: {e}")
    
    def add_mod_mapping(self, korean_mod_name: str, english_mod_id: str):
        """모드명 매핑을 추가합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO mod_mappings 
                    (mod_name, korean_prefix, english_prefix)
                    VALUES (?, ?, ?)
                ''', (english_mod_id, korean_mod_name, english_mod_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"모드 매핑 추가 오류: {e}")
    
    def find_english_name_with_ai(self, korean_name: str, modpack_name: str, context_items: List[str] = None) -> Tuple[Optional[str], float, str]:
        """AI를 활용하여 한글 이름을 영어로 변환합니다."""
        try:
            # AI에게 컨텍스트 제공
            prompt = f"""
다음 마인크래프트 모드팩에서 한글 아이템명을 영어 아이템명으로 변환해주세요.

모드팩: {modpack_name}
한글 아이템명: {korean_name}

사용 가능한 영어 아이템명들:
{', '.join(context_items[:50]) if context_items else '알 수 없음'}

정확한 영어 아이템명만 답변해주세요. 확실하지 않으면 "UNKNOWN"이라고 답변해주세요.
"""
            
            # AI 응답 (실제로는 AI 모델 호출)
            # 여기서는 예시만 표시
            ai_response = "UNKNOWN"  # 실제로는 AI 모델 호출
            
            if ai_response != "UNKNOWN":
                return ai_response, 0.8, "ai_generated"
            
            return None, 0.0, "ai_unknown"
            
        except Exception as e:
            logger.error(f"AI 언어 변환 오류: {e}")
            return None, 0.0, "ai_error"
    
    def get_context_items_for_ai(self, modpack_name: str) -> List[str]:
        """AI 변환을 위한 컨텍스트 아이템 목록을 가져옵니다."""
        try:
            # 해당 모드팩의 모든 아이템명 수집
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT DISTINCT english_name FROM item_mappings
                    WHERE mod_name IN (
                        SELECT mod_name FROM recipes WHERE modpack_name = ?
                    )
                ''', (modpack_name,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"컨텍스트 아이템 조회 오류: {e}")
            return [] 