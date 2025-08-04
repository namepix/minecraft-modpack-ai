import sqlite3
import json
import logging
from typing import List, Dict, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class RecipeManager:
    def __init__(self, db_path: str = "recipes.db"):
        """제작법 매니저를 초기화합니다."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """데이터베이스를 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 제작법 테이블 생성 (버전 정보 추가)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS recipes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        modpack_name TEXT NOT NULL,
                        modpack_version TEXT NOT NULL,
                        mod_name TEXT NOT NULL,
                        recipe_type TEXT DEFAULT 'crafting',
                        ingredients TEXT NOT NULL,
                        result TEXT NOT NULL,
                        crafting_grid TEXT,
                        shapeless BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(item_name, modpack_name, modpack_version)
                    )
                ''')
                
                # 성능 최적화를 위한 인덱스 추가
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_item_name ON recipes(item_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_modpack ON recipes(modpack_name, modpack_version)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_mod_name ON recipes(mod_name)')
                
                # 아이템 정보 테이블 생성 (버전 정보 추가)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        modpack_name TEXT NOT NULL,
                        modpack_version TEXT NOT NULL,
                        mod_name TEXT NOT NULL,
                        display_name TEXT,
                        description TEXT,
                        item_type TEXT,
                        rarity TEXT DEFAULT 'common',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(item_name, modpack_name, modpack_version)
                    )
                ''')
                
                # 아이템 테이블 인덱스
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_item_name ON items(item_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_modpack ON items(modpack_name, modpack_version)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_display_name ON items(display_name)')
                
                # 모드팩 정보 테이블 생성 (버전별 정보)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS modpacks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        modpack_name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        minecraft_version TEXT,
                        forge_version TEXT,
                        mod_count INTEGER DEFAULT 0,
                        recipe_count INTEGER DEFAULT 0,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(modpack_name, version)
                    )
                ''')
                
                # 모드팩 테이블 인덱스
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_modpacks_name_version ON modpacks(modpack_name, version)')
                
                # 버전 매핑 테이블 생성 (구버전 → 신버전)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS version_mappings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        modpack_name TEXT NOT NULL,
                        old_version TEXT NOT NULL,
                        new_version TEXT NOT NULL,
                        compatibility_level TEXT DEFAULT 'partial',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(modpack_name, old_version, new_version)
                    )
                ''')
                
                # 버전 매핑 테이블 인덱스
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_version_mappings_modpack ON version_mappings(modpack_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_version_mappings_old_version ON version_mappings(old_version)')
                
                conn.commit()
                logger.info("제작법 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"제작법 데이터베이스 초기화 오류: {e}")
            raise
    
    def save_recipe(
        self, 
        item_name: str, 
        modpack_name: str, 
        mod_name: str,
        ingredients: List[Dict],
        result: Dict,
        recipe_type: str = "crafting",
        crafting_grid: Optional[List[List[str]]] = None,
        shapeless: bool = False
    ):
        """제작법을 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 제작법 저장
                cursor.execute('''
                    INSERT OR REPLACE INTO recipes 
                    (item_name, modpack_name, modpack_version, mod_name, recipe_type, ingredients, result, crafting_grid, shapeless)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_name,
                    modpack_name,
                    "1.0", # 임시 버전
                    mod_name,
                    recipe_type,
                    json.dumps(ingredients),
                    json.dumps(result),
                    json.dumps(crafting_grid) if crafting_grid else None,
                    shapeless
                ))
                
                conn.commit()
                logger.debug(f"제작법 저장 완료: {item_name} ({modpack_name})")
                
        except Exception as e:
            logger.error(f"제작법 저장 오류: {e}")
            raise
    
    def get_recipe(
        self, 
        item_name: str, 
        modpack_name: str
    ) -> Optional[Dict]:
        """제작법을 조회합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, recipe_type, 
                           ingredients, result, crafting_grid, shapeless
                    FROM recipes
                    WHERE item_name = ? AND modpack_name = ?
                ''', (item_name, modpack_name))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'item_name': row[0],
                        'modpack_name': row[1],
                        'mod_name': row[3], # mod_name 인덱스 변경
                        'recipe_type': row[4],
                        'ingredients': json.loads(row[5]),
                        'result': json.loads(row[6]),
                        'crafting_grid': json.loads(row[7]) if row[7] else None,
                        'shapeless': bool(row[8])
                    }
                return None
                
        except Exception as e:
            logger.error(f"제작법 조회 오류: {e}")
            return None
    
    def search_recipes(
        self, 
        query: str, 
        modpack_name: str,
        limit: int = 10
    ) -> List[Dict]:
        """제작법을 검색합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, recipe_type, 
                           ingredients, result, crafting_grid, shapeless
                    FROM recipes
                    WHERE modpack_name = ? AND 
                          (item_name LIKE ? OR mod_name LIKE ?)
                    LIMIT ?
                ''', (modpack_name, f"%{query}%", f"%{query}%", limit))
                
                rows = cursor.fetchall()
                recipes = []
                
                for row in rows:
                    recipes.append({
                        'item_name': row[0],
                        'modpack_name': row[1],
                        'mod_name': row[3], # mod_name 인덱스 변경
                        'recipe_type': row[4],
                        'ingredients': json.loads(row[5]),
                        'result': json.loads(row[6]),
                        'crafting_grid': json.loads(row[7]) if row[7] else None,
                        'shapeless': bool(row[8])
                    })
                
                return recipes
                
        except Exception as e:
            logger.error(f"제작법 검색 오류: {e}")
            return []
    
    def save_item_info(
        self,
        item_name: str,
        modpack_name: str,
        mod_name: str,
        display_name: str = None,
        description: str = None,
        item_type: str = None,
        rarity: str = "common"
    ):
        """아이템 정보를 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO items 
                    (item_name, modpack_name, modpack_version, mod_name, display_name, description, item_type, rarity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_name,
                    modpack_name,
                    "1.0", # 임시 버전
                    mod_name,
                    display_name,
                    description,
                    item_type,
                    rarity
                ))
                
                conn.commit()
                logger.debug(f"아이템 정보 저장 완료: {item_name}")
                
        except Exception as e:
            logger.error(f"아이템 정보 저장 오류: {e}")
    
    def get_item_info(
        self, 
        item_name: str, 
        modpack_name: str
    ) -> Optional[Dict]:
        """아이템 정보를 조회합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, display_name, 
                           description, item_type, rarity
                    FROM items
                    WHERE item_name = ? AND modpack_name = ?
                ''', (item_name, modpack_name))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'item_name': row[0],
                        'modpack_name': row[1],
                        'mod_name': row[3], # mod_name 인덱스 변경
                        'display_name': row[4],
                        'description': row[5],
                        'item_type': row[6],
                        'rarity': row[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"아이템 정보 조회 오류: {e}")
            return None
    
    def save_modpack_info(
        self,
        modpack_name: str,
        version: str = None,
        minecraft_version: str = None,
        forge_version: str = None,
        mod_count: int = 0,
        recipe_count: int = 0
    ):
        """모드팩 정보를 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO modpacks 
                    (modpack_name, version, minecraft_version, forge_version, mod_count, recipe_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    modpack_name,
                    version,
                    minecraft_version,
                    forge_version,
                    mod_count,
                    recipe_count
                ))
                
                conn.commit()
                logger.debug(f"모드팩 정보 저장 완료: {modpack_name}")
                
        except Exception as e:
            logger.error(f"모드팩 정보 저장 오류: {e}")
    
    def get_modpack_stats(self, modpack_name: str) -> Dict:
        """모드팩 통계를 가져옵니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 모드팩 기본 정보
                cursor.execute('''
                    SELECT version, minecraft_version, forge_version, mod_count, recipe_count, last_updated
                    FROM modpacks
                    WHERE modpack_name = ?
                ''', (modpack_name,))
                
                modpack_row = cursor.fetchone()
                
                # 실제 통계 계산
                cursor.execute('''
                    SELECT COUNT(*) as total_recipes,
                           COUNT(DISTINCT mod_name) as total_mods
                    FROM recipes
                    WHERE modpack_name = ?
                ''', (modpack_name,))
                
                stats_row = cursor.fetchone()
                
                if modpack_row and stats_row:
                    return {
                        'modpack_name': modpack_name,
                        'version': modpack_row[0],
                        'minecraft_version': modpack_row[1],
                        'forge_version': modpack_row[2],
                        'mod_count': modpack_row[3],
                        'recipe_count': modpack_row[4],
                        'last_updated': modpack_row[5],
                        'actual_recipe_count': stats_row[0],
                        'actual_mod_count': stats_row[1]
                    }
                return {
                    'modpack_name': modpack_name,
                    'recipe_count': 0,
                    'mod_count': 0
                }
                
        except Exception as e:
            logger.error(f"모드팩 통계 조회 오류: {e}")
            return {
                'modpack_name': modpack_name,
                'recipe_count': 0,
                'mod_count': 0
            }
    
    def format_recipe_for_gui(self, recipe: Dict) -> Dict:
        """GUI 표시용으로 제작법을 포맷합니다."""
        try:
            formatted_recipe = {
                'item_name': recipe['item_name'],
                'mod_name': recipe['mod_name'],
                'recipe_type': recipe['recipe_type'],
                'shapeless': recipe['shapeless'],
                'grid': self._format_crafting_grid(recipe),
                'ingredients': self._format_ingredients(recipe['ingredients']),
                'result': self._format_result(recipe['result'])
            }
            
            return formatted_recipe
            
        except Exception as e:
            logger.error(f"제작법 포맷 오류: {e}")
            return recipe
    
    def _format_crafting_grid(self, recipe: Dict) -> List[List[str]]:
        """3x3 크래프팅 그리드를 포맷합니다."""
        if recipe.get('crafting_grid'):
            return recipe['crafting_grid']
        
        # 기본 3x3 빈 그리드 생성
        grid = [['' for _ in range(3)] for _ in range(3)]
        
        # 재료를 그리드에 배치 (간단한 구현)
        ingredients = recipe['ingredients']
        if isinstance(ingredients, list) and len(ingredients) <= 9:
            for i, ingredient in enumerate(ingredients):
                row = i // 3
                col = i % 3
                if isinstance(ingredient, dict):
                    grid[row][col] = ingredient.get('item', '')
                else:
                    grid[row][col] = str(ingredient)
        
        return grid
    
    def _format_ingredients(self, ingredients: List) -> List[Dict]:
        """재료 목록을 포맷합니다."""
        formatted = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                formatted.append({
                    'item': ingredient.get('item', ''),
                    'count': ingredient.get('count', 1),
                    'tag': ingredient.get('tag', '')
                })
            else:
                formatted.append({
                    'item': str(ingredient),
                    'count': 1,
                    'tag': ''
                })
        return formatted
    
    def _format_result(self, result: Dict) -> Dict:
        """결과물을 포맷합니다."""
        if isinstance(result, dict):
            return {
                'item': result.get('item', ''),
                'count': result.get('count', 1),
                'nbt': result.get('nbt', '')
            }
        return {
            'item': str(result),
            'count': 1,
            'nbt': ''
        } 

    def get_recipe_with_version_fallback(
        self, 
        item_name: str, 
        modpack_name: str, 
        target_version: str
    ) -> Optional[Dict]:
        """버전별 제작법을 조회하고, 없으면 구버전에서 찾습니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. 정확한 버전에서 먼저 찾기
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, recipe_type, 
                            ingredients, result, crafting_grid, shapeless
                    FROM recipes
                    WHERE item_name = ? AND modpack_name = ? AND modpack_version = ?
                ''', (item_name, modpack_name, target_version))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'item_name': row[0],
                        'modpack_name': row[1],
                        'modpack_version': row[2],
                        'mod_name': row[3],
                        'recipe_type': row[4],
                        'ingredients': json.loads(row[5]),
                        'result': json.loads(row[6]),
                        'crafting_grid': json.loads(row[7]) if row[7] else None,
                        'shapeless': bool(row[8]),
                        'version_source': 'exact'
                    }
                
                # 2. 구버전에서 찾기 (버전 번호 비교)
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, recipe_type, 
                            ingredients, result, crafting_grid, shapeless
                    FROM recipes
                    WHERE item_name = ? AND modpack_name = ?
                    ORDER BY modpack_version ASC
                ''', (item_name, modpack_name))
                
                rows = cursor.fetchall()
                if rows:
                    # 가장 가까운 구버전 선택
                    best_match = rows[0]
                    return {
                        'item_name': best_match[0],
                        'modpack_name': best_match[1],
                        'modpack_version': best_match[2],
                        'mod_name': best_match[3],
                        'recipe_type': best_match[4],
                        'ingredients': json.loads(best_match[5]),
                        'result': json.loads(best_match[6]),
                        'crafting_grid': json.loads(best_match[7]) if best_match[7] else None,
                        'shapeless': bool(best_match[8]),
                        'version_source': 'fallback',
                        'version_warning': f"참고: 이 정보는 {best_match[2]} 버전 기준입니다. 현재 버전({target_version})과 다를 수 있습니다."
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"버전별 제작법 조회 오류: {e}")
            return None
    
    def get_item_info_with_version_fallback(
        self, 
        item_name: str, 
        modpack_name: str, 
        target_version: str
    ) -> Optional[Dict]:
        """버전별 아이템 정보를 조회하고, 없으면 구버전에서 찾습니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. 정확한 버전에서 먼저 찾기
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, display_name, 
                            description, item_type, rarity
                    FROM items
                    WHERE item_name = ? AND modpack_name = ? AND modpack_version = ?
                ''', (item_name, modpack_name, target_version))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'item_name': row[0],
                        'modpack_name': row[1],
                        'modpack_version': row[2],
                        'mod_name': row[3],
                        'display_name': row[4],
                        'description': row[5],
                        'item_type': row[6],
                        'rarity': row[7],
                        'version_source': 'exact'
                    }
                
                # 2. 구버전에서 찾기
                cursor.execute('''
                    SELECT item_name, modpack_name, modpack_version, mod_name, display_name, 
                            description, item_type, rarity
                    FROM items
                    WHERE item_name = ? AND modpack_name = ?
                    ORDER BY modpack_version ASC
                ''', (item_name, modpack_name))
                
                rows = cursor.fetchall()
                if rows:
                    best_match = rows[0]
                    return {
                        'item_name': best_match[0],
                        'modpack_name': best_match[1],
                        'modpack_version': best_match[2],
                        'mod_name': best_match[3],
                        'display_name': best_match[4],
                        'description': best_match[5],
                        'item_type': best_match[6],
                        'rarity': best_match[7],
                        'version_source': 'fallback',
                        'version_warning': f"참고: 이 정보는 {best_match[2]} 버전 기준입니다. 현재 버전({target_version})과 다를 수 있습니다."
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"버전별 아이템 정보 조회 오류: {e}")
            return None
    
    def save_version_mapping(
        self,
        modpack_name: str,
        old_version: str,
        new_version: str,
        compatibility_level: str = "partial"
    ):
        """버전 매핑 정보를 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO version_mappings 
                    (modpack_name, old_version, new_version, compatibility_level)
                    VALUES (?, ?, ?, ?)
                ''', (modpack_name, old_version, new_version, compatibility_level))
                
                conn.commit()
                logger.info(f"버전 매핑 저장: {modpack_name} {old_version} → {new_version}")
                
        except Exception as e:
            logger.error(f"버전 매핑 저장 오류: {e}")
    
    def get_compatible_versions(self, modpack_name: str, target_version: str) -> List[str]:
        """호환 가능한 버전들을 조회합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT old_version, new_version, compatibility_level
                    FROM version_mappings
                    WHERE modpack_name = ? AND (old_version = ? OR new_version = ?)
                ''', (modpack_name, target_version, target_version))
                
                versions = []
                for row in cursor.fetchall():
                    if row[2] == 'full':  # 완전 호환
                        versions.extend([row[0], row[1]])
                    elif row[2] == 'partial':  # 부분 호환
                        versions.extend([row[0], row[1]])
                
                return list(set(versions))  # 중복 제거
                
        except Exception as e:
            logger.error(f"호환 버전 조회 오류: {e}")
            return [] 