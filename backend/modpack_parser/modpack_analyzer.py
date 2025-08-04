import os
import json
import zipfile
import logging
from typing import List, Dict, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class ModpackAnalyzer:
    def __init__(self):
        """모드팩 분석기를 초기화합니다."""
        self.supported_formats = ['.zip', '.jar']
        self.recipe_patterns = [
            'data/*/recipes/**/*.json',
            'assets/*/recipes/**/*.json'
        ]
        
    def analyze_modpack(self, modpack_path: str) -> Dict:
        """모드팩을 분석합니다."""
        try:
            modpack_path = Path(modpack_path)
            
            if not modpack_path.exists():
                raise FileNotFoundError(f"모드팩 파일을 찾을 수 없습니다: {modpack_path}")
            
            if modpack_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"지원하지 않는 파일 형식: {modpack_path.suffix}")
            
            analysis_result = {
                'modpack_name': modpack_path.stem,
                'file_path': str(modpack_path),
                'file_size': modpack_path.stat().st_size,
                'mods': [],
                'recipes': [],
                'items': [],
                'analysis_status': 'pending'
            }
            
            # ZIP 파일 분석
            if modpack_path.suffix.lower() == '.zip':
                analysis_result.update(self._analyze_zip_modpack(modpack_path))
            elif modpack_path.suffix.lower() == '.jar':
                analysis_result.update(self._analyze_jar_modpack(modpack_path))
            
            analysis_result['analysis_status'] = 'completed'
            logger.info(f"모드팩 분석 완료: {modpack_path.name}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"모드팩 분석 오류: {e}")
            return {
                'modpack_name': Path(modpack_path).stem if modpack_path else 'unknown',
                'error': str(e),
                'analysis_status': 'failed'
            }
    
    def _analyze_zip_modpack(self, modpack_path: Path) -> Dict:
        """ZIP 형식 모드팩을 분석합니다."""
        result = {
            'mods': [],
            'recipes': [],
            'items': [],
            'minecraft_version': None,
            'forge_version': None
        }
        
        try:
            with zipfile.ZipFile(modpack_path, 'r') as zip_file:
                # 모드팩 매니페스트 확인
                manifest_info = self._extract_manifest_info(zip_file)
                result.update(manifest_info)
                
                # 모드 파일들 분석
                mod_files = [f for f in zip_file.namelist() if f.endswith('.jar') and 'mods/' in f]
                for mod_file in mod_files:
                    mod_info = self._analyze_mod_file(zip_file, mod_file)
                    if mod_info:
                        result['mods'].append(mod_info)
                
                # 제작법 파일들 분석
                recipe_files = self._find_recipe_files(zip_file)
                for recipe_file in recipe_files:
                    recipe_data = self._parse_recipe_file(zip_file, recipe_file)
                    if recipe_data:
                        result['recipes'].append(recipe_data)
                
                # 아이템 정보 수집
                result['items'] = self._extract_items_from_recipes(result['recipes'])
                
        except Exception as e:
            logger.error(f"ZIP 모드팩 분석 오류: {e}")
            raise
        
        return result
    
    def _analyze_jar_modpack(self, modpack_path: Path) -> Dict:
        """JAR 형식 모드팩을 분석합니다."""
        # JAR 파일도 ZIP과 동일하게 처리
        return self._analyze_zip_modpack(modpack_path)
    
    def _extract_manifest_info(self, zip_file: zipfile.ZipFile) -> Dict:
        """모드팩 매니페스트 정보를 추출합니다."""
        manifest_info = {
            'minecraft_version': None,
            'forge_version': None,
            'modpack_version': None
        }
        
        # 다양한 매니페스트 파일 위치 확인
        manifest_paths = [
            'manifest.json',
            'pack.mcmeta',
            'modlist.html',
            'modlist.xml'
        ]
        
        for manifest_path in manifest_paths:
            try:
                if manifest_path in zip_file.namelist():
                    with zip_file.open(manifest_path) as f:
                        content = f.read().decode('utf-8')
                        
                        if manifest_path == 'manifest.json':
                            manifest_data = json.loads(content)
                            manifest_info['minecraft_version'] = manifest_data.get('minecraft', {}).get('version')
                            manifest_info['modpack_version'] = manifest_data.get('version')
                            
                        elif manifest_path == 'pack.mcmeta':
                            pack_data = json.loads(content)
                            manifest_info['minecraft_version'] = pack_data.get('pack', {}).get('pack_format')
                            
                        elif manifest_path == 'modlist.html':
                            soup = BeautifulSoup(content, 'html.parser')
                            # HTML에서 버전 정보 추출
                            version_elements = soup.find_all(text=re.compile(r'\d+\.\d+\.\d+'))
                            if version_elements:
                                manifest_info['minecraft_version'] = version_elements[0]
                                
                        elif manifest_path == 'modlist.xml':
                            root = ET.fromstring(content)
                            for mod in root.findall('.//mod'):
                                if mod.get('name') == 'forge':
                                    manifest_info['forge_version'] = mod.get('version')
                                    break
                                    
            except Exception as e:
                logger.debug(f"매니페스트 파일 {manifest_path} 파싱 오류: {e}")
                continue
        
        return manifest_info
    
    def _analyze_mod_file(self, zip_file: zipfile.ZipFile, mod_path: str) -> Optional[Dict]:
        """모드 파일을 분석합니다."""
        try:
            with zip_file.open(mod_path) as mod_zip:
                # 모드 메타데이터 추출
                mod_info = {
                    'file_name': os.path.basename(mod_path),
                    'mod_id': None,
                    'mod_name': None,
                    'version': None,
                    'description': None
                }
                
                # mods.toml 파일 확인
                if 'META-INF/mods.toml' in mod_zip.namelist():
                    with mod_zip.open('META-INF/mods.toml') as f:
                        content = f.read().decode('utf-8')
                        mod_info.update(self._parse_mods_toml(content))
                
                # mcmod.info 파일 확인 (구버전)
                elif 'mcmod.info' in mod_zip.namelist():
                    with mod_zip.open('mcmod.info') as f:
                        content = f.read().decode('utf-8')
                        mod_info.update(self._parse_mcmod_info(content))
                
                return mod_info
                
        except Exception as e:
            logger.debug(f"모드 파일 분석 오류 {mod_path}: {e}")
            return None
    
    def _parse_mods_toml(self, content: str) -> Dict:
        """mods.toml 파일을 파싱합니다."""
        mod_info = {}
        
        try:
            # 간단한 TOML 파싱 (실제로는 toml 라이브러리 사용 권장)
            lines = content.split('\n')
            current_mod = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('modId='):
                    current_mod['mod_id'] = line.split('=')[1].strip().strip('"')
                elif line.startswith('displayName='):
                    current_mod['mod_name'] = line.split('=')[1].strip().strip('"')
                elif line.startswith('version='):
                    current_mod['version'] = line.split('=')[1].strip().strip('"')
                elif line.startswith('description='):
                    current_mod['description'] = line.split('=')[1].strip().strip('"')
            
            mod_info.update(current_mod)
            
        except Exception as e:
            logger.debug(f"mods.toml 파싱 오류: {e}")
        
        return mod_info
    
    def _parse_mcmod_info(self, content: str) -> Dict:
        """mcmod.info 파일을 파싱합니다."""
        mod_info = {}
        
        try:
            # JSON 형식으로 파싱
            mcmod_data = json.loads(content)
            if isinstance(mcmod_data, list) and len(mcmod_data) > 0:
                mod_data = mcmod_data[0]
                mod_info['mod_id'] = mod_data.get('modid')
                mod_info['mod_name'] = mod_data.get('name')
                mod_info['version'] = mod_data.get('version')
                mod_info['description'] = mod_data.get('description')
                
        except Exception as e:
            logger.debug(f"mcmod.info 파싱 오류: {e}")
        
        return mod_info
    
    def _find_recipe_files(self, zip_file: zipfile.ZipFile) -> List[str]:
        """제작법 파일들을 찾습니다."""
        recipe_files = []
        
        for pattern in self.recipe_patterns:
            for file_path in zip_file.namelist():
                if self._matches_pattern(file_path, pattern):
                    recipe_files.append(file_path)
        
        return recipe_files
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """파일 경로가 패턴과 일치하는지 확인합니다."""
        # 간단한 패턴 매칭 구현
        pattern_parts = pattern.split('/')
        file_parts = file_path.split('/')
        
        if len(pattern_parts) != len(file_parts):
            return False
        
        for pattern_part, file_part in zip(pattern_parts, file_parts):
            if pattern_part == '**':
                continue
            elif pattern_part == '*':
                continue
            elif pattern_part != file_part:
                return False
        
        return True
    
    def _parse_recipe_file(self, zip_file: zipfile.ZipFile, recipe_path: str) -> Optional[Dict]:
        """제작법 파일을 파싱합니다."""
        try:
            with zip_file.open(recipe_path) as f:
                content = f.read().decode('utf-8')
                recipe_data = json.loads(content)
                
                # 제작법 타입 확인
                recipe_type = recipe_data.get('type', 'minecraft:crafting_shaped')
                
                if 'minecraft:crafting_shaped' in recipe_type:
                    return self._parse_shaped_recipe(recipe_data, recipe_path)
                elif 'minecraft:crafting_shapeless' in recipe_type:
                    return self._parse_shapeless_recipe(recipe_data, recipe_path)
                else:
                    # 다른 타입의 제작법은 무시 (3x3만 지원)
                    return None
                    
        except Exception as e:
            logger.debug(f"제작법 파일 파싱 오류 {recipe_path}: {e}")
            return None
    
    def _parse_shaped_recipe(self, recipe_data: Dict, recipe_path: str) -> Dict:
        """형상 제작법을 파싱합니다."""
        try:
            # 모드 ID 추출
            mod_id = recipe_path.split('/')[1] if len(recipe_path.split('/')) > 1 else 'unknown'
            
            # 아이템명 추출
            item_name = os.path.splitext(os.path.basename(recipe_path))[0]
            
            # 재료 파싱
            ingredients = []
            pattern = recipe_data.get('pattern', [])
            key = recipe_data.get('key', {})
            
            # 3x3 그리드 생성
            grid = [['' for _ in range(3)] for _ in range(3)]
            
            for row_idx, row in enumerate(pattern[:3]):  # 최대 3행
                for col_idx, char in enumerate(row[:3]):  # 최대 3열
                    if char in key:
                        ingredient = key[char]
                        if isinstance(ingredient, dict):
                            item = ingredient.get('item', '')
                            count = ingredient.get('count', 1)
                            grid[row_idx][col_idx] = item
                            ingredients.append({
                                'item': item,
                                'count': count
                            })
            
            # 결과물 파싱
            result = recipe_data.get('result', {})
            if isinstance(result, dict):
                result_item = result.get('item', '')
                result_count = result.get('count', 1)
            else:
                result_item = str(result)
                result_count = 1
            
            return {
                'item_name': item_name,
                'mod_id': mod_id,
                'recipe_type': 'crafting_shaped',
                'ingredients': ingredients,
                'result': {
                    'item': result_item,
                    'count': result_count
                },
                'crafting_grid': grid,
                'shapeless': False
            }
            
        except Exception as e:
            logger.debug(f"형상 제작법 파싱 오류: {e}")
            return None
    
    def _parse_shapeless_recipe(self, recipe_data: Dict, recipe_path: str) -> Dict:
        """무형상 제작법을 파싱합니다."""
        try:
            # 모드 ID 추출
            mod_id = recipe_path.split('/')[1] if len(recipe_path.split('/')) > 1 else 'unknown'
            
            # 아이템명 추출
            item_name = os.path.splitext(os.path.basename(recipe_path))[0]
            
            # 재료 파싱
            ingredients = []
            ingredients_data = recipe_data.get('ingredients', [])
            
            for ingredient in ingredients_data:
                if isinstance(ingredient, dict):
                    item = ingredient.get('item', '')
                    count = ingredient.get('count', 1)
                    ingredients.append({
                        'item': item,
                        'count': count
                    })
            
            # 결과물 파싱
            result = recipe_data.get('result', {})
            if isinstance(result, dict):
                result_item = result.get('item', '')
                result_count = result.get('count', 1)
            else:
                result_item = str(result)
                result_count = 1
            
            return {
                'item_name': item_name,
                'mod_id': mod_id,
                'recipe_type': 'crafting_shapeless',
                'ingredients': ingredients,
                'result': {
                    'item': result_item,
                    'count': result_count
                },
                'crafting_grid': None,  # 무형상은 그리드 없음
                'shapeless': True
            }
            
        except Exception as e:
            logger.debug(f"무형상 제작법 파싱 오류: {e}")
            return None
    
    def _extract_items_from_recipes(self, recipes: List[Dict]) -> List[Dict]:
        """제작법에서 아이템 정보를 추출합니다."""
        items = set()
        
        for recipe in recipes:
            # 결과물 아이템
            if recipe.get('result', {}).get('item'):
                items.add(recipe['result']['item'])
            
            # 재료 아이템들
            for ingredient in recipe.get('ingredients', []):
                if ingredient.get('item'):
                    items.add(ingredient['item'])
        
        return [{'item_name': item} for item in sorted(items)] 