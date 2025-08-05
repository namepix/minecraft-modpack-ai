"""
채팅 매니저 테스트
"""
import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from backend.database.chat_manager import ChatManager


class TestChatManager:
    """채팅 매니저 테스트 클래스"""
    
    @pytest.fixture
    def chat_manager(self, temp_db):
        """채팅 매니저 인스턴스 생성"""
        manager = ChatManager(db_path=temp_db)
        return manager
    
    def test_initialization(self, temp_db):
        """초기화 테스트"""
        manager = ChatManager(db_path=temp_db)
        
        # 데이터베이스 테이블이 생성되었는지 확인
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'chat_history' in tables
            assert 'user_sessions' in tables
    
    def test_add_message_success(self, chat_manager):
        """메시지 추가 성공 테스트"""
        message_data = {
            'user_uuid': 'test-user-123',
            'user_message': '철광석 제작법 알려줘',
            'ai_response': '철광석은 지하에서 캘 수 있습니다.',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        result = chat_manager.add_message(message_data)
        
        assert result is True
        
        # 데이터베이스에 저장되었는지 확인
        with sqlite3.connect(chat_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_message, ai_response FROM chat_history 
                WHERE user_uuid = ?
            """, ('test-user-123',))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == '철광석 제작법 알려줘'
            assert result[1] == '철광석은 지하에서 캘 수 있습니다.'
    
    def test_add_message_missing_data(self, chat_manager):
        """메시지 추가 누락된 데이터 테스트"""
        # 필수 필드 누락
        message_data = {
            'user_uuid': 'test-user-123',
            'user_message': '테스트 메시지'
            # ai_response, modpack_name 누락
        }
        
        result = chat_manager.add_message(message_data)
        
        assert result is False
    
    def test_get_chat_history_success(self, chat_manager):
        """채팅 기록 조회 성공 테스트"""
        # 테스트 메시지들 추가
        messages = [
            {
                'user_uuid': 'test-user-123',
                'user_message': '첫 번째 질문',
                'ai_response': '첫 번째 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'test-user-123',
                'user_message': '두 번째 질문',
                'ai_response': '두 번째 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # 채팅 기록 조회
        history = chat_manager.get_chat_history('test-user-123', limit=10)
        
        assert len(history) == 2
        assert history[0]['user_message'] == '첫 번째 질문'
        assert history[1]['user_message'] == '두 번째 질문'
        
        # 시간순 정렬 확인 (최신순)
        assert history[0]['timestamp'] <= history[1]['timestamp']
    
    def test_get_chat_history_limit(self, chat_manager):
        """채팅 기록 제한 테스트"""
        # 5개의 메시지 추가
        for i in range(5):
            message_data = {
                'user_uuid': 'test-user-123',
                'user_message': f'질문 {i+1}',
                'ai_response': f'답변 {i+1}',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
            chat_manager.add_message(message_data)
        
        # 3개만 조회
        history = chat_manager.get_chat_history('test-user-123', limit=3)
        
        assert len(history) == 3
        # 최신 메시지들이 조회되어야 함
        assert history[0]['user_message'] == '질문 5'
        assert history[1]['user_message'] == '질문 4'
        assert history[2]['user_message'] == '질문 3'
    
    def test_get_chat_history_no_messages(self, chat_manager):
        """채팅 기록 없음 테스트"""
        history = chat_manager.get_chat_history('nonexistent-user', limit=10)
        
        assert history == []
    
    def test_get_chat_history_by_modpack(self, chat_manager):
        """모드팩별 채팅 기록 조회 테스트"""
        # 다른 모드팩의 메시지들 추가
        messages = [
            {
                'user_uuid': 'test-user-123',
                'user_message': 'TestModpack 질문',
                'ai_response': 'TestModpack 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'test-user-123',
                'user_message': 'OtherModpack 질문',
                'ai_response': 'OtherModpack 답변',
                'modpack_name': 'OtherModpack',
                'modpack_version': '2.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # TestModpack의 채팅 기록만 조회
        history = chat_manager.get_chat_history_by_modpack('test-user-123', 'TestModpack', limit=10)
        
        assert len(history) == 1
        assert history[0]['modpack_name'] == 'TestModpack'
        assert history[0]['user_message'] == 'TestModpack 질문'
    
    def test_delete_chat_history(self, chat_manager):
        """채팅 기록 삭제 테스트"""
        # 테스트 메시지 추가
        message_data = {
            'user_uuid': 'test-user-123',
            'user_message': '삭제될 메시지',
            'ai_response': '삭제될 답변',
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        chat_manager.add_message(message_data)
        
        # 삭제 전 확인
        history = chat_manager.get_chat_history('test-user-123')
        assert len(history) == 1
        
        # 삭제 실행
        result = chat_manager.delete_chat_history('test-user-123')
        
        assert result is True
        
        # 삭제 후 확인
        history = chat_manager.get_chat_history('test-user-123')
        assert len(history) == 0
    
    def test_delete_chat_history_nonexistent_user(self, chat_manager):
        """존재하지 않는 사용자의 채팅 기록 삭제 테스트"""
        result = chat_manager.delete_chat_history('nonexistent-user')
        
        assert result is True  # 삭제할 것이 없어도 성공으로 처리
    
    def test_cleanup_old_messages(self, chat_manager):
        """오래된 메시지 정리 테스트"""
        # 오래된 메시지 추가 (30일 전)
        old_timestamp = datetime.now() - timedelta(days=31)
        
        with sqlite3.connect(chat_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_uuid, user_message, ai_response, modpack_name, modpack_version, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('test-user-123', '오래된 메시지', '오래된 답변', 'TestModpack', '1.0.0', old_timestamp.isoformat()))
            conn.commit()
        
        # 정리 실행
        cleaned_count = chat_manager.cleanup_old_messages(days=30)
        
        assert cleaned_count >= 1
        
        # 정리되었는지 확인
        history = chat_manager.get_chat_history('test-user-123')
        assert len(history) == 0
    
    def test_get_user_statistics(self, chat_manager):
        """사용자 통계 조회 테스트"""
        # 여러 메시지 추가
        messages = [
            {
                'user_uuid': 'test-user-123',
                'user_message': '질문 1',
                'ai_response': '답변 1',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'test-user-123',
                'user_message': '질문 2',
                'ai_response': '답변 2',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'other-user-456',
                'user_message': '다른 사용자 질문',
                'ai_response': '다른 사용자 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # 통계 조회
        stats = chat_manager.get_user_statistics('test-user-123')
        
        assert 'total_messages' in stats
        assert 'modpacks_used' in stats
        assert 'first_message' in stats
        assert 'last_message' in stats
        assert stats['total_messages'] == 2
        assert len(stats['modpacks_used']) == 1
        assert 'TestModpack' in stats['modpacks_used']
    
    def test_get_modpack_statistics(self, chat_manager):
        """모드팩 통계 조회 테스트"""
        # 여러 모드팩의 메시지 추가
        messages = [
            {
                'user_uuid': 'test-user-123',
                'user_message': 'TestModpack 질문',
                'ai_response': 'TestModpack 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'test-user-123',
                'user_message': 'OtherModpack 질문',
                'ai_response': 'OtherModpack 답변',
                'modpack_name': 'OtherModpack',
                'modpack_version': '2.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # TestModpack 통계 조회
        stats = chat_manager.get_modpack_statistics('TestModpack')
        
        assert 'total_messages' in stats
        assert 'unique_users' in stats
        assert 'versions_used' in stats
        assert stats['total_messages'] == 1
        assert len(stats['unique_users']) == 1
        assert 'test-user-123' in stats['unique_users']
        assert len(stats['versions_used']) == 1
        assert '1.0.0' in stats['versions_used']
    
    def test_search_messages(self, chat_manager):
        """메시지 검색 테스트"""
        # 검색 가능한 메시지들 추가
        messages = [
            {
                'user_uuid': 'test-user-123',
                'user_message': '철광석 제작법 알려줘',
                'ai_response': '철광석은 지하에서 캘 수 있습니다.',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'test-user-123',
                'user_message': '다이아몬드 제작법 알려줘',
                'ai_response': '다이아몬드는 Y=12 이하에서 찾을 수 있습니다.',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # 철광석 검색
        results = chat_manager.search_messages('test-user-123', '철광석', limit=10)
        
        assert len(results) == 1
        assert '철광석' in results[0]['user_message']
    
    def test_search_messages_no_results(self, chat_manager):
        """메시지 검색 결과 없음 테스트"""
        results = chat_manager.search_messages('test-user-123', '존재하지 않는 키워드', limit=10)
        
        assert results == []
    
    def test_get_recent_activity(self, chat_manager):
        """최근 활동 조회 테스트"""
        # 여러 사용자의 메시지 추가
        messages = [
            {
                'user_uuid': 'user1',
                'user_message': '사용자1 질문',
                'ai_response': '사용자1 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            },
            {
                'user_uuid': 'user2',
                'user_message': '사용자2 질문',
                'ai_response': '사용자2 답변',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
        ]
        
        for msg in messages:
            chat_manager.add_message(msg)
        
        # 최근 활동 조회
        activity = chat_manager.get_recent_activity(limit=10)
        
        assert len(activity) == 2
        assert any('user1' in item['user_uuid'] for item in activity)
        assert any('user2' in item['user_uuid'] for item in activity)
    
    def test_add_message_with_long_content(self, chat_manager):
        """긴 내용의 메시지 추가 테스트"""
        long_message = 'a' * 1000  # 1000자 메시지
        long_response = 'b' * 1000  # 1000자 응답
        
        message_data = {
            'user_uuid': 'test-user-123',
            'user_message': long_message,
            'ai_response': long_response,
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        result = chat_manager.add_message(message_data)
        
        assert result is True
        
        # 저장된 내용 확인
        history = chat_manager.get_chat_history('test-user-123')
        assert len(history) == 1
        assert history[0]['user_message'] == long_message
        assert history[0]['ai_response'] == long_response
    
    def test_add_message_with_special_characters(self, chat_manager):
        """특수문자가 포함된 메시지 추가 테스트"""
        special_message = "특수문자: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_response = "특수문자 응답: <script>alert('test')</script>"
        
        message_data = {
            'user_uuid': 'test-user-123',
            'user_message': special_message,
            'ai_response': special_response,
            'modpack_name': 'TestModpack',
            'modpack_version': '1.0.0'
        }
        
        result = chat_manager.add_message(message_data)
        
        assert result is True
        
        # 저장된 내용 확인
        history = chat_manager.get_chat_history('test-user-123')
        assert len(history) == 1
        assert history[0]['user_message'] == special_message
        assert history[0]['ai_response'] == special_response
    
    def test_get_chat_history_with_offset(self, chat_manager):
        """오프셋이 있는 채팅 기록 조회 테스트"""
        # 10개의 메시지 추가
        for i in range(10):
            message_data = {
                'user_uuid': 'test-user-123',
                'user_message': f'질문 {i+1}',
                'ai_response': f'답변 {i+1}',
                'modpack_name': 'TestModpack',
                'modpack_version': '1.0.0'
            }
            chat_manager.add_message(message_data)
        
        # 오프셋 5, 제한 3으로 조회
        history = chat_manager.get_chat_history('test-user-123', offset=5, limit=3)
        
        assert len(history) == 3
        # 오프셋 이후의 메시지들이 조회되어야 함
        assert history[0]['user_message'] == '질문 5'
        assert history[1]['user_message'] == '질문 4'
        assert history[2]['user_message'] == '질문 3' 