"""
모드팩 분석기 테스트
"""
import pytest
import json
import tempfile
import os
import zipfile
from unittest.mock import Mock, patch, mock_open
from backend.modpack_parser.modpack_analyzer import ModpackAnalyzer


class TestModpackAnalyzer:
    """모드팩 분석기 테스트 클래스"""
    
    @pytest.fixture
    def analyzer(self):
        """모드팩 분석기 인스턴스 생성"""
        return ModpackAnalyzer()
    
    @pytest.fixture
    def temp_modpack_file(self):
        """임시 모드팩 파일 생성"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            # 간단한 ZIP 파일 생성
            with zipfile.ZipFile(f.name, 'w') as zf:
                # mods 폴더에 가짜 JAR 파일들 추가
                zf.writestr('mods/testmod1-1.0.0.jar', 'fake jar content')
                zf.writestr('mods/testmod2-2.0.0.jar', 'fake jar content')
                
                # recipes 폴더에 가짜 JSON 파일들 추가
                zf.writestr('data/minecraft/recipes/test_recipe.json', json.dumps({
                    'type': 'minecraft:crafting',
                    'ingredients': [{'item': 'minecraft:dirt'}],
                    'result': {'item': 'minecraft:test_item', 'count': 1}
                }))
                
                # assets 폴더에 가짜 언어 파일 추가
                zf.writestr('assets/testmod1/lang/ko_kr.json', json.dumps({
                    'item.testmod1.test_item': '테스트 아이템'
                }))
                
                # pack.mcmeta 파일 추가
                zf.writestr('pack.mcmeta', json.dumps({
                    'pack': {
                        'pack_format': 15,
                        'description': 'Test Modpack'
                    }
                }))
            
            yield f.name
            
            # 테스트 후 정리
            if os.path.exists(f.name):
                os.unlink(f.name)
    
    def test_initialization(self, analyzer):
        """초기화 테스트"""
        assert analyzer is not None
        assert hasattr(analyzer, 'extract_modpack_info')
        assert hasattr(analyzer, 'analyze_mods')
        assert hasattr(analyzer, 'extract_recipes')
        assert hasattr(analyzer, 'extract_items')
    
    def test_extract_modpack_info_success(self, analyzer, temp_modpack_file):
        """모드팩 정보 추출 성공 테스트"""
        info = analyzer.extract_modpack_info(temp_modpack_file)
        
        assert info is not None
        assert 'pack_format' in info
        assert 'description' in info
        assert info['pack_format'] == 15
        assert info['description'] == 'Test Modpack'
    
    def test_extract_modpack_info_no_mcmeta(self, analyzer):
        """pack.mcmeta 파일 없음 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # pack.mcmeta 없이 ZIP 파일 생성
                zf.writestr('mods/testmod.jar', 'fake content')
            
            info = analyzer.extract_modpack_info(f.name)
            
            # 기본값이 설정되어야 함
            assert info is not None
            assert info['pack_format'] == 15  # 기본값
            assert info['description'] == 'Unknown Modpack'
            
            os.unlink(f.name)
    
    def test_extract_modpack_info_invalid_zip(self, analyzer):
        """잘못된 ZIP 파일 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            f.write(b'invalid zip content')
            f.close()
            
            info = analyzer.extract_modpack_info(f.name)
            
            # 오류가 발생해도 기본값 반환
            assert info is not None
            assert info['pack_format'] == 15
            assert info['description'] == 'Unknown Modpack'
            
            os.unlink(f.name)
    
    @patch('zipfile.ZipFile')
    def test_extract_modpack_info_zip_error_mocked(self, mock_zipfile, analyzer):
        """ZIP 파일 오류 모킹 테스트 (더 격리된 테스트)"""
        mock_zipfile.side_effect = Exception("ZIP 오류")
        
        info = analyzer.extract_modpack_info('fake_file.zip')
        
        # 오류가 발생해도 기본값 반환
        assert info is not None
        assert info['pack_format'] == 15
        assert info['description'] == 'Unknown Modpack'
    
    def test_analyze_mods_success(self, analyzer, temp_modpack_file):
        """모드 분석 성공 테스트"""
        mods = analyzer.analyze_mods(temp_modpack_file)
        
        assert len(mods) == 2
        assert any('testmod1' in mod['name'] for mod in mods)
        assert any('testmod2' in mod['name'] for mod in mods)
        
        # 각 모드에 필수 필드가 있는지 확인
        for mod in mods:
            assert 'name' in mod
            assert 'version' in mod
            assert 'file_name' in mod
    
    def test_analyze_mods_no_mods_folder(self, analyzer):
        """mods 폴더 없음 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # mods 폴더 없이 ZIP 파일 생성
                zf.writestr('other_file.txt', 'content')
            
            mods = analyzer.analyze_mods(f.name)
            
            assert mods == []
            
            os.unlink(f.name)
    
    def test_extract_recipes_success(self, analyzer, temp_modpack_file):
        """레시피 추출 성공 테스트"""
        recipes = analyzer.extract_recipes(temp_modpack_file)
        
        assert len(recipes) >= 1
        assert any('test_recipe' in recipe['recipe_id'] for recipe in recipes)
        
        # 레시피 구조 확인
        for recipe in recipes:
            assert 'recipe_id' in recipe
            assert 'type' in recipe
            assert 'ingredients' in recipe
            assert 'result' in recipe
    
    def test_extract_recipes_no_recipes(self, analyzer):
        """레시피 없음 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # 레시피 없이 ZIP 파일 생성
                zf.writestr('mods/testmod.jar', 'fake content')
            
            recipes = analyzer.extract_recipes(f.name)
            
            assert recipes == []
            
            os.unlink(f.name)
    
    def test_extract_recipes_invalid_json(self, analyzer):
        """잘못된 JSON 레시피 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # 잘못된 JSON 레시피 추가
                zf.writestr('data/minecraft/recipes/invalid.json', 'invalid json')
            
            recipes = analyzer.extract_recipes(f.name)
            
            # 잘못된 JSON은 무시되어야 함
            assert recipes == []
            
            os.unlink(f.name)
    
    def test_extract_items_success(self, analyzer, temp_modpack_file):
        """아이템 추출 성공 테스트"""
        items = analyzer.extract_items(temp_modpack_file)
        
        assert len(items) >= 1
        assert any('test_item' in item['name'] for item in items)
        
        # 아이템 구조 확인
        for item in items:
            assert 'name' in item
            assert 'display_name' in item
            assert 'mod' in item
    
    def test_extract_items_with_language_files(self, analyzer):
        """언어 파일이 있는 아이템 추출 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # 언어 파일 추가
                zf.writestr('assets/testmod/lang/ko_kr.json', json.dumps({
                    'item.testmod.iron_ore': '철광석',
                    'item.testmod.diamond_ore': '다이아몬드 광석'
                }))
                zf.writestr('assets/testmod/lang/en_us.json', json.dumps({
                    'item.testmod.iron_ore': 'Iron Ore',
                    'item.testmod.diamond_ore': 'Diamond Ore'
                }))
            
            items = analyzer.extract_items(f.name)
            
            # 언어 파일에서 아이템 정보가 추출되어야 함
            assert len(items) >= 2
            assert any('iron_ore' in item['name'] for item in items)
            assert any('diamond_ore' in item['name'] for item in items)
            
            os.unlink(f.name)
    
    def test_extract_items_no_language_files(self, analyzer):
        """언어 파일 없음 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # 언어 파일 없이 ZIP 파일 생성
                zf.writestr('mods/testmod.jar', 'fake content')
            
            items = analyzer.extract_items(f.name)
            
            assert items == []
            
            os.unlink(f.name)
    
    def test_analyze_modpack_integration(self, analyzer, temp_modpack_file):
        """모드팩 분석 통합 테스트"""
        result = analyzer.analyze_modpack(temp_modpack_file)
        
        assert result is not None
        assert 'modpack_name' in result
        assert 'version' in result
        assert 'mods' in result
        assert 'recipes' in result
        assert 'items' in result
        assert 'pack_format' in result
        assert 'description' in result
        
        # 각 섹션이 올바르게 분석되었는지 확인
        assert len(result['mods']) == 2
        assert len(result['recipes']) >= 1
        assert len(result['items']) >= 1
    
    def test_analyze_modpack_with_custom_name(self, analyzer, temp_modpack_file):
        """사용자 정의 이름으로 모드팩 분석 테스트"""
        custom_name = "CustomTestModpack"
        result = analyzer.analyze_modpack(temp_modpack_file, custom_name)
        
        assert result['modpack_name'] == custom_name
    
    def test_extract_version_from_filename(self, analyzer):
        """파일명에서 버전 추출 테스트"""
        test_cases = [
            ('TestModpack-1.0.0.zip', '1.0.0'),
            ('MyModpack_v2.1.3.zip', '2.1.3'),
            ('Modpack-3.0.0-beta.zip', '3.0.0'),
            ('NoVersion.zip', '1.0.0'),  # 기본값
            ('Complex-Name-4.2.1-release.zip', '4.2.1')
        ]
        
        for filename, expected_version in test_cases:
            version = analyzer.extract_version_from_filename(filename)
            assert version == expected_version
    
    def test_parse_recipe_ingredients(self, analyzer):
        """레시피 재료 파싱 테스트"""
        test_recipe = {
            'type': 'minecraft:crafting',
            'ingredients': [
                {'item': 'minecraft:dirt'},
                {'item': 'minecraft:stone', 'count': 2},
                {'tag': 'minecraft:logs'}
            ],
            'result': {'item': 'minecraft:test_item', 'count': 1}
        }
        
        parsed = analyzer.parse_recipe_ingredients(test_recipe['ingredients'])
        
        assert len(parsed) == 3
        assert parsed[0]['item'] == 'minecraft:dirt'
        assert parsed[0]['count'] == 1  # 기본값
        assert parsed[1]['item'] == 'minecraft:stone'
        assert parsed[1]['count'] == 2
        assert parsed[2]['item'] == 'minecraft:logs'
        assert parsed[2]['count'] == 1
    
    def test_parse_recipe_result(self, analyzer):
        """레시피 결과 파싱 테스트"""
        test_result = {'item': 'minecraft:test_item', 'count': 3}
        
        parsed = analyzer.parse_recipe_result(test_result)
        
        assert parsed['item'] == 'minecraft:test_item'
        assert parsed['count'] == 3
    
    def test_parse_recipe_result_default_count(self, analyzer):
        """레시피 결과 기본 개수 테스트"""
        test_result = {'item': 'minecraft:test_item'}  # count 없음
        
        parsed = analyzer.parse_recipe_result(test_result)
        
        assert parsed['item'] == 'minecraft:test_item'
        assert parsed['count'] == 1  # 기본값
    
    def test_extract_mod_info_from_filename(self, analyzer):
        """파일명에서 모드 정보 추출 테스트"""
        test_cases = [
            ('testmod-1.0.0.jar', ('testmod', '1.0.0')),
            ('MyMod_v2.1.3.jar', ('MyMod', '2.1.3')),
            ('Complex-Mod-Name-3.0.0-beta.jar', ('Complex-Mod-Name', '3.0.0')),
            ('NoVersion.jar', ('NoVersion', '1.0.0')),  # 기본값
            ('mod_with_underscores_4.2.1.jar', ('mod_with_underscores', '4.2.1'))
        ]
        
        for filename, expected in test_cases:
            name, version = analyzer.extract_mod_info_from_filename(filename)
            assert name == expected[0]
            assert version == expected[1]
    
    def test_validate_recipe_structure(self, analyzer):
        """레시피 구조 검증 테스트"""
        valid_recipe = {
            'type': 'minecraft:crafting',
            'ingredients': [{'item': 'minecraft:dirt'}],
            'result': {'item': 'minecraft:test_item'}
        }
        
        invalid_recipe = {
            'type': 'minecraft:crafting'
            # ingredients와 result 누락
        }
        
        assert analyzer.validate_recipe_structure(valid_recipe) is True
        assert analyzer.validate_recipe_structure(invalid_recipe) is False
    
    def test_extract_language_mappings(self, analyzer):
        """언어 매핑 추출 테스트"""
        korean_lang = {
            'item.testmod.iron_ore': '철광석',
            'item.testmod.diamond_ore': '다이아몬드 광석',
            'block.testmod.furnace': '화로'
        }
        
        english_lang = {
            'item.testmod.iron_ore': 'Iron Ore',
            'item.testmod.diamond_ore': 'Diamond Ore',
            'block.testmod.furnace': 'Furnace'
        }
        
        mappings = analyzer.extract_language_mappings(korean_lang, english_lang)
        
        assert len(mappings) == 3
        assert any(m['korean'] == '철광석' and m['english'] == 'Iron Ore' for m in mappings)
        assert any(m['korean'] == '다이아몬드 광석' and m['english'] == 'Diamond Ore' for m in mappings)
    
    def test_analyze_modpack_error_handling(self, analyzer):
        """모드팩 분석 오류 처리 테스트"""
        # 존재하지 않는 파일
        result = analyzer.analyze_modpack('nonexistent_file.zip')
        
        # 오류가 발생해도 기본 구조 반환
        assert result is not None
        assert 'modpack_name' in result
        assert 'version' in result
        assert 'mods' in result
        assert 'recipes' in result
        assert 'items' in result
        assert result['mods'] == []
        assert result['recipes'] == []
        assert result['items'] == []
    
    def test_extract_recipes_with_different_types(self, analyzer):
        """다양한 레시피 타입 추출 테스트"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as f:
            with zipfile.ZipFile(f.name, 'w') as zf:
                # 다양한 타입의 레시피 추가
                zf.writestr('data/minecraft/recipes/crafting.json', json.dumps({
                    'type': 'minecraft:crafting',
                    'ingredients': [{'item': 'minecraft:dirt'}],
                    'result': {'item': 'minecraft:test_item'}
                }))
                zf.writestr('data/minecraft/recipes/smelting.json', json.dumps({
                    'type': 'minecraft:smelting',
                    'ingredient': {'item': 'minecraft:iron_ore'},
                    'result': 'minecraft:iron_ingot',
                    'experience': 0.7,
                    'cookingtime': 200
                }))
                zf.writestr('data/minecraft/recipes/shaped.json', json.dumps({
                    'type': 'minecraft:crafting_shaped',
                    'pattern': ['DDD', 'D D', 'DDD'],
                    'key': {'D': {'item': 'minecraft:diamond'}},
                    'result': {'item': 'minecraft:test_block'}
                }))
            
            recipes = analyzer.extract_recipes(f.name)
            
            assert len(recipes) == 3
            recipe_types = [r['type'] for r in recipes]
            assert 'minecraft:crafting' in recipe_types
            assert 'minecraft:smelting' in recipe_types
            assert 'minecraft:crafting_shaped' in recipe_types
            
            os.unlink(f.name) 