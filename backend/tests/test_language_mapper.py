"""
언어 매퍼 테스트
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch
from backend.utils.language_mapper import LanguageMapper


class TestLanguageMapper:
    """언어 매퍼 테스트 클래스"""
    
    @pytest.fixture
    def language_mapper(self, temp_db):
        """언어 매퍼 인스턴스 생성"""
        mapper = LanguageMapper(db_path=temp_db)
        return mapper
    
    def test_initialization(self, temp_db):
        """초기화 테스트"""
        mapper = LanguageMapper(db_path=temp_db)
        
        # 데이터베이스 테이블이 생성되었는지 확인
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'item_mappings' in tables
            assert 'mod_mappings' in tables
            assert 'custom_mappings' in tables
    
    def test_load_common_mappings(self, language_mapper):
        """공통 매핑 로드 테스트"""
        # 공통 매핑이 로드되었는지 확인
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM item_mappings WHERE source = 'common'")
            count = cursor.fetchone()[0]
            
            assert count > 0  # 공통 매핑이 로드되어야 함
    
    def test_find_english_name_hybrid_stage1_user_defined(self, language_mapper):
        """1단계: 사용자 정의 매핑 테스트"""
        # 사용자 정의 매핑 추가
        language_mapper.add_custom_mapping('테스트아이템', 'test_item', 'test-user')
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '테스트아이템', 'TestModpack', 'test-user'
        )
        
        assert english_name == 'test_item'
        assert confidence == 1.0
        assert source == 'user_defined'
    
    def test_find_english_name_hybrid_stage2_general_db(self, language_mapper):
        """2단계: 일반 DB 매핑 테스트"""
        # 일반 DB에 매핑 추가
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO item_mappings (korean_name, english_name, modpack_name, source, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, ('철광석', 'iron_ore', 'TestModpack', 'db', 0.9))
            conn.commit()
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '철광석', 'TestModpack', 'test-user'
        )
        
        assert english_name == 'iron_ore'
        assert confidence == 0.9
        assert source == 'db'
    
    def test_find_english_name_hybrid_stage3_partial_match(self, language_mapper):
        """3단계: 부분 매칭 테스트"""
        # 부분 매칭을 위한 데이터 추가
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO item_mappings (korean_name, english_name, modpack_name, source, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, ('철', 'iron', 'TestModpack', 'partial', 0.6))
            conn.commit()
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '철광석', 'TestModpack', 'test-user'
        )
        
        # 부분 매칭이 작동하는지 확인 (철광석에 '철'이 포함됨)
        assert english_name == 'iron'
        assert confidence == 0.6
        assert source == 'partial'
    
    def test_find_english_name_hybrid_stage4_ai_translation(self, language_mapper):
        """4단계: AI 번역 테스트"""
        # AI 번역 모킹
        mock_ai_model = Mock()
        mock_ai_model.clients = {'openai': Mock()}
        mock_ai_model.clients['openai'].chat.completions.create.return_value.choices[0].message.content = 'iron_ore'
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '철광석', 'TestModpack', 'test-user', ai_model=mock_ai_model
        )
        
        assert english_name == 'iron_ore'
        assert confidence == 0.7
        assert source == 'ai'
    
    def test_find_english_name_hybrid_no_match(self, language_mapper):
        """매칭 실패 테스트"""
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '존재하지않는아이템', 'TestModpack', 'test-user'
        )
        
        assert english_name is None
        assert confidence == 0.0
        assert source == 'no_match'
    
    def test_add_custom_mapping(self, language_mapper):
        """사용자 정의 매핑 추가 테스트"""
        result = language_mapper.add_custom_mapping('테스트아이템', 'test_item', 'test-user')
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT english_name FROM custom_mappings 
                WHERE korean_name = ? AND user_uuid = ?
            """, ('테스트아이템', 'test-user'))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 'test_item'
    
    def test_add_custom_mapping_duplicate(self, language_mapper):
        """중복 사용자 정의 매핑 테스트"""
        # 첫 번째 추가
        language_mapper.add_custom_mapping('테스트아이템', 'test_item_1', 'test-user')
        
        # 두 번째 추가 (업데이트)
        result = language_mapper.add_custom_mapping('테스트아이템', 'test_item_2', 'test-user')
        
        assert result is True
        
        # 업데이트되었는지 확인
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT english_name FROM custom_mappings 
                WHERE korean_name = ? AND user_uuid = ?
            """, ('테스트아이템', 'test-user'))
            result = cursor.fetchone()
            
            assert result[0] == 'test_item_2'
    
    def test_update_usage_count(self, language_mapper):
        """사용 횟수 업데이트 테스트"""
        # 초기 매핑 추가
        language_mapper.add_custom_mapping('테스트아이템', 'test_item', 'test-user')
        
        # 사용 횟수 업데이트
        language_mapper.update_usage_count('테스트아이템', 'test_item')
        
        # 업데이트되었는지 확인
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT usage_count FROM custom_mappings 
                WHERE korean_name = ? AND english_name = ?
            """, ('테스트아이템', 'test_item'))
            result = cursor.fetchone()
            
            assert result[0] == 1
    
    def test_analyze_modpack_for_mappings(self, language_mapper, sample_modpack_data):
        """모드팩 분석을 통한 매핑 생성 테스트"""
        mappings = language_mapper.analyze_modpack_for_mappings(sample_modpack_data)
        
        assert len(mappings) > 0
        assert any(mapping['korean_name'] == '테스트 아이템' for mapping in mappings)
        assert any(mapping['english_name'] == 'test_item' for mapping in mappings)
    
    def test_find_english_name_with_ai_success(self, language_mapper):
        """AI 번역 성공 테스트"""
        mock_ai_model = Mock()
        mock_ai_model.clients = {'openai': Mock()}
        mock_ai_model.clients['openai'].chat.completions.create.return_value.choices[0].message.content = 'iron_ore'
        
        english_name, confidence = language_mapper.find_english_name_with_ai(
            '철광석', 'TestModpack', mock_ai_model
        )
        
        assert english_name == 'iron_ore'
        assert confidence == 0.7
    
    def test_find_english_name_with_ai_failure(self, language_mapper):
        """AI 번역 실패 테스트"""
        mock_ai_model = Mock()
        mock_ai_model.clients = {'openai': Mock()}
        mock_ai_model.clients['openai'].chat.completions.create.side_effect = Exception("API 오류")
        
        english_name, confidence = language_mapper.find_english_name_with_ai(
            '철광석', 'TestModpack', mock_ai_model
        )
        
        assert english_name is None
        assert confidence == 0.0
    
    def test_get_mapping_statistics(self, language_mapper):
        """매핑 통계 테스트"""
        # 테스트 데이터 추가
        language_mapper.add_custom_mapping('아이템1', 'item1', 'user1')
        language_mapper.add_custom_mapping('아이템2', 'item2', 'user2')
        
        stats = language_mapper.get_mapping_statistics()
        
        assert 'total_mappings' in stats
        assert 'custom_mappings' in stats
        assert 'db_mappings' in stats
        assert stats['custom_mappings'] >= 2
    
    def test_cleanup_old_mappings(self, language_mapper):
        """오래된 매핑 정리 테스트"""
        # 오래된 매핑 추가 (30일 전)
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO custom_mappings (korean_name, english_name, user_uuid, created_at)
                VALUES (?, ?, ?, datetime('now', '-31 days'))
            """, ('오래된아이템', 'old_item', 'test-user'))
            conn.commit()
        
        # 정리 실행
        cleaned_count = language_mapper.cleanup_old_mappings(days=30)
        
        assert cleaned_count >= 1
        
        # 정리되었는지 확인
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM custom_mappings 
                WHERE korean_name = '오래된아이템'
            """)
            count = cursor.fetchone()[0]
            
            assert count == 0
    
    def test_find_english_name_hybrid_priority_order(self, language_mapper):
        """매핑 우선순위 순서 테스트"""
        # 여러 단계의 매핑을 동시에 설정
        language_mapper.add_custom_mapping('테스트아이템', 'custom_item', 'test-user')
        
        with sqlite3.connect(language_mapper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO item_mappings (korean_name, english_name, modpack_name, source, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, ('테스트아이템', 'db_item', 'TestModpack', 'db', 0.9))
            conn.commit()
        
        # 사용자 정의 매핑이 우선되어야 함
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '테스트아이템', 'TestModpack', 'test-user'
        )
        
        assert english_name == 'custom_item'
        assert confidence == 1.0
        assert source == 'user_defined'
    
    def test_find_english_name_hybrid_case_insensitive(self, language_mapper):
        """대소문자 구분 없는 매칭 테스트"""
        language_mapper.add_custom_mapping('철광석', 'IRON_ORE', 'test-user')
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '철광석', 'TestModpack', 'test-user'
        )
        
        assert english_name == 'IRON_ORE'
        assert confidence == 1.0
        assert source == 'user_defined'
    
    def test_find_english_name_hybrid_special_characters(self, language_mapper):
        """특수문자 처리 테스트"""
        language_mapper.add_custom_mapping('테스트-아이템', 'test-item', 'test-user')
        
        english_name, confidence, source = language_mapper.find_english_name_hybrid(
            '테스트-아이템', 'TestModpack', 'test-user'
        )
        
        assert english_name == 'test-item'
        assert confidence == 1.0
        assert source == 'user_defined' 