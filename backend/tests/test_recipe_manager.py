"""
레시피 매니저 테스트
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch
from backend.database.recipe_manager import RecipeManager


class TestRecipeManager:
    """레시피 매니저 테스트 클래스"""
    
    @pytest.fixture
    def recipe_manager(self, temp_db):
        """레시피 매니저 인스턴스 생성"""
        manager = RecipeManager(db_path=temp_db)
        return manager
    
    def test_initialization(self, temp_db):
        """초기화 테스트"""
        manager = RecipeManager(db_path=temp_db)
        
        # 데이터베이스 테이블이 생성되었는지 확인
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'recipes' in tables
            assert 'items' in tables
            assert 'modpacks' in tables
            assert 'version_mappings' in tables
    
    def test_add_modpack(self, recipe_manager):
        """모드팩 추가 테스트"""
        modpack_data = {
            'name': 'TestModpack',
            'version': '1.0.0',
            'description': '테스트 모드팩'
        }
        
        result = recipe_manager.add_modpack(modpack_data)
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, version, description FROM modpacks 
                WHERE name = ? AND version = ?
            """, ('TestModpack', '1.0.0'))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 'TestModpack'
            assert result[1] == '1.0.0'
            assert result[2] == '테스트 모드팩'
    
    def test_add_modpack_duplicate(self, recipe_manager):
        """중복 모드팩 추가 테스트"""
        modpack_data = {
            'name': 'TestModpack',
            'version': '1.0.0',
            'description': '테스트 모드팩'
        }
        
        # 첫 번째 추가
        recipe_manager.add_modpack(modpack_data)
        
        # 두 번째 추가 (실패해야 함)
        result = recipe_manager.add_modpack(modpack_data)
        
        assert result is False
    
    def test_add_recipe(self, recipe_manager):
        """레시피 추가 테스트"""
        recipe_data = {
            'item_name': 'test_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'test_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        result = recipe_manager.add_recipe(recipe_data)
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT item_name, recipe_type FROM recipes 
                WHERE item_name = ? AND modpack_name = ?
            """, ('test_item', 'TestModpack'))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 'test_item'
            assert result[1] == 'crafting'
    
    def test_add_item_info(self, recipe_manager):
        """아이템 정보 추가 테스트"""
        item_data = {
            'name': 'test_item',
            'display_name': '테스트 아이템',
            'mod': 'testmod',
            'description': '테스트용 아이템입니다.',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        result = recipe_manager.add_item_info(item_data)
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, display_name, mod FROM items 
                WHERE name = ? AND modpack_name = ?
            """, ('test_item', 'TestModpack'))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 'test_item'
            assert result[1] == '테스트 아이템'
            assert result[2] == 'testmod'
    
    def test_get_recipe_with_version_fallback_success(self, recipe_manager):
        """버전 폴백이 있는 레시피 조회 성공 테스트"""
        # 정확한 버전의 레시피 추가
        recipe_data = {
            'item_name': 'test_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'test_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_recipe(recipe_data)
        
        # 정확한 버전으로 조회
        recipe = recipe_manager.get_recipe_with_version_fallback(
            'test_item', 'TestModpack', '1.0.0'
        )
        
        assert recipe is not None
        assert recipe['item_name'] == 'test_item'
        assert recipe['recipe_type'] == 'crafting'
    
    def test_get_recipe_with_version_fallback_older_version(self, recipe_manager):
        """이전 버전으로 폴백 테스트"""
        # 이전 버전의 레시피 추가
        old_recipe_data = {
            'item_name': 'test_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'stone', 'count': 1}],
            'result': {'item': 'test_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '0.9.0'
        }
        recipe_manager.add_recipe(old_recipe_data)
        
        # 새 버전으로 조회 (이전 버전으로 폴백)
        recipe = recipe_manager.get_recipe_with_version_fallback(
            'test_item', 'TestModpack', '1.0.0'
        )
        
        assert recipe is not None
        assert recipe['item_name'] == 'test_item'
        assert recipe['modpack_version'] == '0.9.0'
    
    def test_get_recipe_with_version_fallback_newer_version(self, recipe_manager):
        """새 버전으로 폴백 테스트"""
        # 새 버전의 레시피 추가
        new_recipe_data = {
            'item_name': 'test_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'diamond', 'count': 1}],
            'result': {'item': 'test_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '1.1.0'
        }
        recipe_manager.add_recipe(new_recipe_data)
        
        # 이전 버전으로 조회 (새 버전으로 폴백)
        recipe = recipe_manager.get_recipe_with_version_fallback(
            'test_item', 'TestModpack', '1.0.0'
        )
        
        assert recipe is not None
        assert recipe['item_name'] == 'test_item'
        assert recipe['modpack_version'] == '1.1.0'
    
    def test_get_recipe_with_version_fallback_no_match(self, recipe_manager):
        """매칭되는 레시피 없음 테스트"""
        recipe = recipe_manager.get_recipe_with_version_fallback(
            'nonexistent_item', 'TestModpack', '1.0.0'
        )
        
        assert recipe is None
    
    def test_get_item_info_with_version_fallback(self, recipe_manager):
        """버전 폴백이 있는 아이템 정보 조회 테스트"""
        # 아이템 정보 추가
        item_data = {
            'name': 'test_item',
            'display_name': '테스트 아이템',
            'mod': 'testmod',
            'description': '테스트용 아이템입니다.',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_item_info(item_data)
        
        # 조회
        item_info = recipe_manager.get_item_info_with_version_fallback(
            'test_item', 'TestModpack', '1.0.0'
        )
        
        assert item_info is not None
        assert item_info['name'] == 'test_item'
        assert item_info['display_name'] == '테스트 아이템'
        assert item_info['mod'] == 'testmod'
    
    def test_get_modpack_stats(self, recipe_manager):
        """모드팩 통계 조회 테스트"""
        # 테스트 데이터 추가
        modpack_data = {
            'name': 'TestModpack',
            'version': '1.0.0',
            'description': '테스트 모드팩'
        }
        recipe_manager.add_modpack(modpack_data)
        
        recipe_data = {
            'item_name': 'test_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'test_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_recipe(recipe_data)
        
        item_data = {
            'name': 'test_item',
            'display_name': '테스트 아이템',
            'mod': 'testmod',
            'description': '테스트용 아이템입니다.',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_item_info(item_data)
        
        # 통계 조회
        stats = recipe_manager.get_modpack_stats('TestModpack')
        
        assert 'total_recipes' in stats
        assert 'total_items' in stats
        assert 'recipe_types' in stats
        assert 'mods' in stats
        assert stats['total_recipes'] == 1
        assert stats['total_items'] == 1
    
    def test_search_recipes(self, recipe_manager):
        """레시피 검색 테스트"""
        # 테스트 레시피 추가
        recipe_data = {
            'item_name': 'iron_ore',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'iron_ore', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_recipe(recipe_data)
        
        # 검색
        results = recipe_manager.search_recipes('iron', 'TestModpack')
        
        assert len(results) == 1
        assert results[0]['item_name'] == 'iron_ore'
    
    def test_search_items(self, recipe_manager):
        """아이템 검색 테스트"""
        # 테스트 아이템 추가
        item_data = {
            'name': 'iron_ore',
            'display_name': '철광석',
            'mod': 'minecraft',
            'description': '철광석입니다.',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        recipe_manager.add_item_info(item_data)
        
        # 검색
        results = recipe_manager.search_items('철', 'TestModpack')
        
        assert len(results) == 1
        assert results[0]['name'] == 'iron_ore'
        assert results[0]['display_name'] == '철광석'
    
    def test_add_version_mapping(self, recipe_manager):
        """버전 매핑 추가 테스트"""
        mapping_data = {
            'old_version': '0.9.0',
            'new_version': '1.0.0',
            'modpack_name': 'TestModpack',
            'mapping_type': 'recipe',
            'old_item': 'old_item',
            'new_item': 'new_item'
        }
        
        result = recipe_manager.add_version_mapping(mapping_data)
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT old_item, new_item FROM version_mappings 
                WHERE modpack_name = ? AND mapping_type = ?
            """, ('TestModpack', 'recipe'))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 'old_item'
            assert result[1] == 'new_item'
    
    def test_get_version_mappings(self, recipe_manager):
        """버전 매핑 조회 테스트"""
        # 매핑 데이터 추가
        mapping_data = {
            'old_version': '0.9.0',
            'new_version': '1.0.0',
            'modpack_name': 'TestModpack',
            'mapping_type': 'recipe',
            'old_item': 'old_item',
            'new_item': 'new_item'
        }
        recipe_manager.add_version_mapping(mapping_data)
        
        # 조회
        mappings = recipe_manager.get_version_mappings('TestModpack', 'recipe')
        
        assert len(mappings) == 1
        assert mappings[0]['old_item'] == 'old_item'
        assert mappings[0]['new_item'] == 'new_item'
    
    def test_bulk_insert_recipes(self, recipe_manager):
        """대량 레시피 삽입 테스트"""
        recipes = [
            {
                'item_name': 'item1',
                'recipe_type': 'crafting',
                'ingredients': [{'item': 'dirt', 'count': 1}],
                'result': {'item': 'item1', 'count': 1},
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'item_name': 'item2',
                'recipe_type': 'smelting',
                'ingredients': [{'item': 'iron_ore', 'count': 1}],
                'result': {'item': 'item2', 'count': 1},
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        result = recipe_manager.bulk_insert_recipes(recipes)
        
        assert result is True
        
        # 두 개의 레시피가 모두 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE modpack_name = 'TestModpack'")
            count = cursor.fetchone()[0]
            
            assert count == 2
    
    def test_bulk_insert_items(self, recipe_manager):
        """대량 아이템 삽입 테스트"""
        items = [
            {
                'name': 'item1',
                'display_name': '아이템1',
                'mod': 'testmod',
                'description': '첫 번째 아이템',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'name': 'item2',
                'display_name': '아이템2',
                'mod': 'testmod',
                'description': '두 번째 아이템',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        result = recipe_manager.bulk_insert_items(items)
        
        assert result is True
        
        # 두 개의 아이템이 모두 저장되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items WHERE modpack_name = 'TestModpack'")
            count = cursor.fetchone()[0]
            
            assert count == 2
    
    def test_cleanup_old_data(self, recipe_manager):
        """오래된 데이터 정리 테스트"""
        # 오래된 데이터 추가
        old_recipe_data = {
            'item_name': 'old_item',
            'recipe_type': 'crafting',
            'ingredients': [{'item': 'dirt', 'count': 1}],
            'result': {'item': 'old_item', 'count': 1},
            'modpack_name': 'TestModpack',
            'modpack_version': '0.9.0'
        }
        recipe_manager.add_recipe(old_recipe_data)
        
        # 정리 실행
        cleaned_count = recipe_manager.cleanup_old_data('TestModpack', '1.0.0')
        
        assert cleaned_count >= 1
        
        # 정리되었는지 확인
        with sqlite3.connect(recipe_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM recipes 
                WHERE modpack_name = 'TestModpack' AND modpack_version = '0.9.0'
            """)
            count = cursor.fetchone()[0]
            
            assert count == 0 