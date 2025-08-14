#!/usr/bin/env python3
"""
개선된 모드팩 파서 - Enigmatica 10, Prominence 2 등 대형 모드팩 지원
기존 modpack_parser.py의 확장 버전
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class EnhancedModpackParser:
    """대형 모드팩 전용 향상된 파서"""
    
    def __init__(self):
        self.supported_recipe_types = {
            'minecraft:crafting_shaped',
            'minecraft:crafting_shapeless', 
            'minecraft:smelting',
            'minecraft:blasting',
            'minecraft:smoking',
            'minecraft:campfire_cooking',
            'thermal:pulverizer',
            'thermal:smelter',
            'thermal:centrifuge',
            'mekanism:enriching',
            'mekanism:crushing',
            'mekanism:smelting',
            'create:mixing',
            'create:pressing',
            'create:cutting',
            'appliedenergistics2:grinder',
            'appliedenergistics2:inscriber'
        }
        
        self.mod_categories = {
            'tech': ['thermal', 'mekanism', 'industrialcraft', 'applied', 'refined'],
            'magic': ['thaumcraft', 'botania', 'blood', 'astral', 'embers'],
            'exploration': ['twilight', 'aether', 'dimensional', 'mining'],
            'automation': ['create', 'integrated', 'xnet', 'logistics'],
            'storage': ['applied', 'refined', 'storage', 'colossal'],
            'tools': ['tinkers', 'thermal', 'mekanism', 'ender']
        }
    
    def scan_enhanced_modpack(self, modpack_path: str) -> Dict[str, Any]:
        """향상된 모드팩 스캔"""
        print(f"🔍 향상된 모드팩 스캔 시작: {modpack_path}")
        
        if not os.path.exists(modpack_path):
            return {'docs': [], 'stats': {}, 'error': 'Path not found'}
        
        docs = []
        stats = {
            'recipes': 0,
            'mods': 0, 
            'kubejs': 0,
            'configs': 0,
            'quests': 0,
            'lang_files': 0,
            'mod_categories': {},
            'recipe_types': {}
        }
        
        # 1. 모드 분석 (향상된 버전)
        mod_docs, mod_stats = self._analyze_mods_enhanced(modpack_path)
        docs.extend(mod_docs)
        stats.update(mod_stats)
        
        # 2. 레시피 분석 (확장된 지원)
        recipe_docs, recipe_stats = self._analyze_recipes_enhanced(modpack_path)
        docs.extend(recipe_docs)
        stats['recipes'] = recipe_stats['count']
        stats['recipe_types'] = recipe_stats['types']
        
        # 3. KubeJS 스크립트 분석
        kubejs_docs, kubejs_count = self._analyze_kubejs_enhanced(modpack_path)
        docs.extend(kubejs_docs)
        stats['kubejs'] = kubejs_count
        
        # 4. 설정 파일 분석
        config_docs, config_count = self._analyze_configs(modpack_path)
        docs.extend(config_docs)
        stats['configs'] = config_count
        
        # 5. 퀘스트 분석 (FTB Quests, HQM 등)
        quest_docs, quest_count = self._analyze_quests(modpack_path)
        docs.extend(quest_docs)
        stats['quests'] = quest_count
        
        # 6. 언어 파일 분석 (다국어 지원)
        lang_docs, lang_count = self._analyze_lang_files(modpack_path)
        docs.extend(lang_docs)
        stats['lang_files'] = lang_count
        
        print(f"✅ 스캔 완료: {len(docs)}개 문서, {stats}")
        
        return {
            'docs': docs,
            'stats': stats,
            'modpack_analysis': self._analyze_modpack_type(stats, docs)
        }
    
    def _analyze_mods_enhanced(self, modpack_path: str) -> Tuple[List[Dict], Dict]:
        """향상된 모드 분석"""
        mods_dir = os.path.join(modpack_path, 'mods')
        if not os.path.isdir(mods_dir):
            return [], {'mods': 0, 'mod_categories': {}}
        
        docs = []
        mod_categories = {cat: 0 for cat in self.mod_categories}
        
        try:
            jar_files = [f for f in os.listdir(mods_dir) if f.lower().endswith('.jar')]
            
            for jar_file in jar_files:
                # 모드명에서 정보 추출
                mod_name = self._extract_mod_name(jar_file)
                mod_category = self._categorize_mod(mod_name)
                
                if mod_category:
                    mod_categories[mod_category] += 1
                
                # 향상된 텍스트 정보
                text = f"Mod: {mod_name} (category: {mod_category or 'general'})"
                if self._is_major_mod(mod_name):
                    text += " [MAJOR MOD]"
                
                docs.append({
                    'type': 'mod',
                    'mod_name': mod_name,
                    'category': mod_category,
                    'is_major': self._is_major_mod(mod_name),
                    'source': os.path.join(mods_dir, jar_file),
                    'text': text
                })
            
            return docs, {'mods': len(jar_files), 'mod_categories': mod_categories}
            
        except Exception as e:
            logger.error(f"모드 분석 실패: {e}")
            return [], {'mods': 0, 'mod_categories': {}}
    
    def _analyze_recipes_enhanced(self, modpack_path: str) -> Tuple[List[Dict], Dict]:
        """확장된 레시피 분석"""
        data_dir = os.path.join(modpack_path, 'data')
        if not os.path.isdir(data_dir):
            return [], {'count': 0, 'types': {}}
        
        docs = []
        recipe_types = {}
        
        for root, _, files in os.walk(data_dir):
            for file_name in files:
                if not file_name.endswith('.json'):
                    continue
                
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    recipe_type = data.get('type', 'unknown')
                    recipe_types[recipe_type] = recipe_types.get(recipe_type, 0) + 1
                    
                    # 향상된 레시피 파싱
                    recipe_doc = self._parse_recipe_enhanced(data, file_path, recipe_type)
                    if recipe_doc:
                        docs.append(recipe_doc)
                        
                except Exception as e:
                    logger.debug(f"레시피 파일 파싱 실패 {file_path}: {e}")
                    continue
        
        return docs, {'count': len(docs), 'types': recipe_types}
    
    def _parse_recipe_enhanced(self, recipe_data: Dict, file_path: str, recipe_type: str) -> Dict:
        """향상된 레시피 파싱"""
        result = recipe_data.get('result')
        
        # 결과 아이템 정보 추출
        result_item = "unknown"
        result_count = 1
        
        if isinstance(result, dict):
            result_item = result.get('item') or result.get('id') or "unknown"
            result_count = result.get('count', 1)
        elif isinstance(result, str):
            result_item = result
        elif isinstance(result, list) and result:
            # 다중 결과 처리
            first_result = result[0]
            if isinstance(first_result, dict):
                result_item = first_result.get('item') or first_result.get('id') or "unknown"
                result_count = first_result.get('count', 1)
        
        # 입력 재료 정보 추출
        ingredients = self._extract_ingredients(recipe_data)
        
        # 모드 이름 추출
        mod_id = result_item.split(':')[0] if ':' in result_item else 'minecraft'
        
        # 향상된 텍스트 생성
        clean_item = result_item.split(':')[-1].replace('_', ' ')
        text_parts = [
            f"Recipe: {clean_item} x{result_count}",
            f"Type: {recipe_type.split(':')[-1]}",
            f"Mod: {mod_id}"
        ]
        
        if ingredients:
            text_parts.append(f"Ingredients: {', '.join(ingredients[:3])}")
        
        return {
            'type': 'recipe',
            'subtype': recipe_type,
            'result_item': result_item,
            'result_count': result_count,
            'mod_id': mod_id,
            'ingredients': ingredients,
            'source': file_path,
            'text': ' | '.join(text_parts)
        }
    
    def _extract_ingredients(self, recipe_data: Dict) -> List[str]:
        """레시피 재료 정보 추출"""
        ingredients = []
        
        # ingredients 필드
        if 'ingredients' in recipe_data:
            for ing in recipe_data['ingredients']:
                if isinstance(ing, dict):
                    item = ing.get('item') or ing.get('tag') or ""
                    if item:
                        ingredients.append(item.split(':')[-1].replace('_', ' '))
        
        # pattern과 key 조합 (shaped recipes)
        if 'pattern' in recipe_data and 'key' in recipe_data:
            key_map = recipe_data['key']
            for symbol, spec in key_map.items():
                if isinstance(spec, dict):
                    item = spec.get('item') or spec.get('tag') or ""
                    if item:
                        ingredients.append(item.split(':')[-1].replace('_', ' '))
        
        # input 필드 (기계 레시피)
        if 'input' in recipe_data:
            input_data = recipe_data['input']
            if isinstance(input_data, dict):
                item = input_data.get('item') or input_data.get('tag') or ""
                if item:
                    ingredients.append(item.split(':')[-1].replace('_', ' '))
            elif isinstance(input_data, list):
                for inp in input_data:
                    if isinstance(inp, dict):
                        item = inp.get('item') or inp.get('tag') or ""
                        if item:
                            ingredients.append(item.split(':')[-1].replace('_', ' '))
        
        return ingredients[:5]  # 최대 5개 재료만
    
    def _analyze_kubejs_enhanced(self, modpack_path: str) -> Tuple[List[Dict], int]:
        """향상된 KubeJS 분석"""
        kubejs_dir = os.path.join(modpack_path, 'kubejs')
        if not os.path.isdir(kubejs_dir):
            return [], 0
        
        docs = []
        
        for root, _, files in os.walk(kubejs_dir):
            for file_name in files:
                if not file_name.endswith(('.js', '.json')):
                    continue
                
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(3000)  # 더 많은 내용 읽기
                    
                    # 스크립트 타입 분석
                    script_type = self._analyze_kubejs_type(content, file_path)
                    
                    # 내용 요약
                    summary = self._summarize_kubejs_content(content)
                    
                    relative_path = os.path.relpath(file_path, kubejs_dir)
                    text = f"KubeJS {script_type}: {relative_path} | {summary}"
                    
                    docs.append({
                        'type': 'kubejs',
                        'script_type': script_type,
                        'summary': summary,
                        'source': file_path,
                        'text': text
                    })
                    
                except Exception as e:
                    logger.debug(f"KubeJS 파일 읽기 실패 {file_path}: {e}")
        
        return docs, len(docs)
    
    def _analyze_configs(self, modpack_path: str) -> Tuple[List[Dict], int]:
        """설정 파일 분석"""
        config_dir = os.path.join(modpack_path, 'config')
        if not os.path.isdir(config_dir):
            return [], 0
        
        docs = []
        important_configs = {
            'thermal.toml', 'mekanism.toml', 'create.toml', 
            'appliedenergistics2.toml', 'botania.toml'
        }
        
        for root, _, files in os.walk(config_dir):
            for file_name in files:
                if file_name not in important_configs:
                    continue
                
                file_path = os.path.join(root, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)
                    
                    mod_name = file_name.replace('.toml', '')
                    text = f"Config: {mod_name} | {content[:200].replace('\n', ' ')}"
                    
                    docs.append({
                        'type': 'config',
                        'mod_name': mod_name,
                        'source': file_path,
                        'text': text
                    })
                    
                except Exception as e:
                    logger.debug(f"설정 파일 읽기 실패 {file_path}: {e}")
        
        return docs, len(docs)
    
    def _analyze_quests(self, modpack_path: str) -> Tuple[List[Dict], int]:
        """퀘스트 시스템 분석"""
        docs = []
        quest_dirs = ['ftbquests', 'config/ftbquests', 'questbook', 'config/hqm']
        
        for quest_dir_name in quest_dirs:
            quest_dir = os.path.join(modpack_path, quest_dir_name)
            if not os.path.isdir(quest_dir):
                continue
            
            for root, _, files in os.walk(quest_dir):
                for file_name in files:
                    if not file_name.endswith('.snbt'):
                        continue
                    
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(2000)
                        
                        # 퀘스트 정보 추출
                        quest_info = self._extract_quest_info(content)
                        
                        text = f"Quest: {quest_info.get('title', file_name)} | {quest_info.get('description', '')[:100]}"
                        
                        docs.append({
                            'type': 'quest',
                            'quest_info': quest_info,
                            'source': file_path,
                            'text': text
                        })
                        
                    except Exception as e:
                        logger.debug(f"퀘스트 파일 읽기 실패 {file_path}: {e}")
        
        return docs, len(docs)
    
    def _analyze_lang_files(self, modpack_path: str) -> Tuple[List[Dict], int]:
        """언어 파일 분석 (국제화 지원)"""
        docs = []
        
        # 언어 파일 위치들
        lang_locations = [
            'assets/*/lang/*.json',
            'resourcepacks/*/assets/*/lang/*.json'
        ]
        
        for location_pattern in lang_locations:
            import glob
            pattern = os.path.join(modpack_path, location_pattern)
            
            for file_path in glob.glob(pattern, recursive=True):
                if 'ko_kr.json' not in file_path and 'en_us.json' not in file_path:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lang_data = json.load(f)
                    
                    lang_code = 'ko_kr' if 'ko_kr' in file_path else 'en_us'
                    mod_id = self._extract_mod_from_path(file_path)
                    
                    # 중요한 번역 항목들만 추출
                    important_keys = [k for k in lang_data.keys() 
                                    if any(term in k.lower() for term in ['item.', 'block.', 'gui.'])]
                    
                    if important_keys:
                        sample_translations = {k: lang_data[k] for k in important_keys[:10]}
                        text = f"Lang ({lang_code}): {mod_id} | {len(lang_data)} translations"
                        
                        docs.append({
                            'type': 'lang',
                            'lang_code': lang_code,
                            'mod_id': mod_id,
                            'translation_count': len(lang_data),
                            'sample_translations': sample_translations,
                            'source': file_path,
                            'text': text
                        })
                
                except Exception as e:
                    logger.debug(f"언어 파일 읽기 실패 {file_path}: {e}")
        
        return docs, len(docs)
    
    def _extract_mod_name(self, jar_filename: str) -> str:
        """JAR 파일명에서 모드명 추출"""
        # 버전 번호 제거
        name = re.sub(r'-\d+\.\d+.*\.jar$', '', jar_filename, flags=re.IGNORECASE)
        name = name.replace('.jar', '')
        return name.lower()
    
    def _categorize_mod(self, mod_name: str) -> str:
        """모드를 카테고리로 분류"""
        for category, keywords in self.mod_categories.items():
            if any(keyword in mod_name for keyword in keywords):
                return category
        return None
    
    def _is_major_mod(self, mod_name: str) -> bool:
        """주요 모드인지 확인"""
        major_mods = {
            'thermal', 'mekanism', 'create', 'appliedenergistics', 'refined',
            'tinkers', 'botania', 'thaumcraft', 'industrialcraft', 'buildcraft'
        }
        return any(major in mod_name for major in major_mods)
    
    def _analyze_kubejs_type(self, content: str, file_path: str) -> str:
        """KubeJS 스크립트 타입 분석"""
        if 'recipe' in content.lower():
            return 'recipe_modification'
        elif 'startup' in file_path:
            return 'startup_script'
        elif 'server' in file_path:
            return 'server_script'
        elif 'client' in file_path:
            return 'client_script'
        else:
            return 'general_script'
    
    def _summarize_kubejs_content(self, content: str) -> str:
        """KubeJS 내용 요약"""
        keywords = []
        
        if 'recipe' in content.lower():
            keywords.append('recipe changes')
        if 'remove' in content.lower():
            keywords.append('recipe removal')
        if 'shaped' in content.lower():
            keywords.append('shaped crafting')
        if 'smelting' in content.lower():
            keywords.append('smelting')
        
        return ', '.join(keywords) if keywords else 'script modifications'
    
    def _extract_quest_info(self, content: str) -> Dict[str, str]:
        """퀘스트 정보 추출"""
        info = {}
        
        # 제목 추출
        title_match = re.search(r'title:\s*"([^"]+)"', content)
        if title_match:
            info['title'] = title_match.group(1)
        
        # 설명 추출
        desc_match = re.search(r'description:\s*\[([^\]]+)\]', content)
        if desc_match:
            info['description'] = desc_match.group(1).replace('"', '').replace(',', ' ')
        
        return info
    
    def _extract_mod_from_path(self, file_path: str) -> str:
        """파일 경로에서 모드 ID 추출"""
        parts = file_path.split(os.sep)
        for i, part in enumerate(parts):
            if part == 'assets' and i + 1 < len(parts):
                return parts[i + 1]
        return 'unknown'
    
    def _analyze_modpack_type(self, stats: Dict, docs: List[Dict]) -> Dict[str, Any]:
        """모드팩 타입 분석"""
        analysis = {
            'modpack_type': 'unknown',
            'complexity': 'medium',
            'primary_focus': 'mixed',
            'has_quests': stats.get('quests', 0) > 0,
            'has_custom_recipes': stats.get('kubejs', 0) > 0,
            'tech_heavy': False,
            'magic_heavy': False
        }
        
        # 모드 카테고리 분석
        categories = stats.get('mod_categories', {})
        tech_mods = categories.get('tech', 0)
        magic_mods = categories.get('magic', 0)
        
        if tech_mods > magic_mods * 2:
            analysis['primary_focus'] = 'tech'
            analysis['tech_heavy'] = True
        elif magic_mods > tech_mods * 2:
            analysis['primary_focus'] = 'magic'
            analysis['magic_heavy'] = True
        
        # 복잡도 결정
        total_docs = len(docs)
        if total_docs > 1000:
            analysis['complexity'] = 'high'
        elif total_docs < 200:
            analysis['complexity'] = 'low'
        
        # 모드팩 타입 추정
        if analysis['has_quests'] and total_docs > 500:
            analysis['modpack_type'] = 'expert'
        elif tech_mods > 10:
            analysis['modpack_type'] = 'tech'
        elif magic_mods > 5:
            analysis['modpack_type'] = 'magic'
        
        return analysis


def main():
    """테스트 함수"""
    parser = EnhancedModpackParser()
    
    # 테스트용 경로 (실제 사용시 수정 필요)
    test_path = input("테스트할 모드팩 경로: ")
    
    if os.path.exists(test_path):
        result = parser.scan_enhanced_modpack(test_path)
        
        print(f"\n📊 스캔 결과:")
        print(f"총 문서: {len(result['docs'])}개")
        print(f"통계: {result['stats']}")
        print(f"분석: {result['modpack_analysis']}")
    else:
        print(f"❌ 경로가 존재하지 않습니다: {test_path}")


if __name__ == "__main__":
    main()