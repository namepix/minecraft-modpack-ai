import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, db_path: str = "chat_history.db"):
        """채팅 매니저를 초기화합니다."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """데이터베이스를 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 채팅 기록 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_uuid TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        modpack_name TEXT DEFAULT 'unknown',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 플레이어 정보 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS player_info (
                        player_uuid TEXT PRIMARY KEY,
                        player_name TEXT,
                        first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                        total_messages INTEGER DEFAULT 0
                    )
                ''')
                
                conn.commit()
                logger.info("채팅 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def save_message(
        self, 
        player_uuid: str, 
        user_message: str, 
        ai_response: str, 
        modpack_name: str = "unknown"
    ):
        """메시지를 저장합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 채팅 기록 저장
                cursor.execute('''
                    INSERT INTO chat_history (player_uuid, user_message, ai_response, modpack_name)
                    VALUES (?, ?, ?, ?)
                ''', (player_uuid, user_message, ai_response, modpack_name))
                
                # 플레이어 정보 업데이트
                cursor.execute('''
                    INSERT OR REPLACE INTO player_info (player_uuid, last_seen, total_messages)
                    VALUES (?, CURRENT_TIMESTAMP, 
                        COALESCE((SELECT total_messages FROM player_info WHERE player_uuid = ?), 0) + 1)
                ''', (player_uuid, player_uuid))
                
                conn.commit()
                logger.debug(f"메시지 저장 완료: {player_uuid}")
                
        except Exception as e:
            logger.error(f"메시지 저장 오류: {e}")
            raise
    
    def get_chat_history(
        self, 
        player_uuid: str, 
        limit: int = 20
    ) -> List[Dict]:
        """플레이어의 채팅 기록을 가져옵니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT user_message, ai_response, modpack_name, timestamp
                    FROM chat_history
                    WHERE player_uuid = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (player_uuid, limit))
                
                rows = cursor.fetchall()
                history = []
                
                for row in reversed(rows):  # 시간순으로 정렬
                    history.append({
                        'user_message': row[0],
                        'ai_response': row[1],
                        'modpack_name': row[2],
                        'timestamp': row[3]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"채팅 기록 조회 오류: {e}")
            return []
    
    def get_player_stats(self, player_uuid: str) -> Optional[Dict]:
        """플레이어 통계를 가져옵니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT player_name, first_seen, last_seen, total_messages
                    FROM player_info
                    WHERE player_uuid = ?
                ''', (player_uuid,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'player_name': row[0],
                        'first_seen': row[1],
                        'last_seen': row[2],
                        'total_messages': row[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"플레이어 통계 조회 오류: {e}")
            return None
    
    def update_player_name(self, player_uuid: str, player_name: str):
        """플레이어 이름을 업데이트합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO player_info (player_uuid, player_name, last_seen)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (player_uuid, player_name))
                
                conn.commit()
                logger.debug(f"플레이어 이름 업데이트: {player_uuid} -> {player_name}")
                
        except Exception as e:
            logger.error(f"플레이어 이름 업데이트 오류: {e}")
    
    def get_modpack_usage_stats(self, modpack_name: str) -> Dict:
        """특정 모드팩의 사용 통계를 가져옵니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) as total_messages,
                           COUNT(DISTINCT player_uuid) as unique_players,
                           MIN(timestamp) as first_used,
                           MAX(timestamp) as last_used
                    FROM chat_history
                    WHERE modpack_name = ?
                ''', (modpack_name,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'total_messages': row[0],
                        'unique_players': row[1],
                        'first_used': row[2],
                        'last_used': row[3]
                    }
                return {
                    'total_messages': 0,
                    'unique_players': 0,
                    'first_used': None,
                    'last_used': None
                }
                
        except Exception as e:
            logger.error(f"모드팩 사용 통계 조회 오류: {e}")
            return {
                'total_messages': 0,
                'unique_players': 0,
                'first_used': None,
                'last_used': None
            }
    
    def cleanup_old_messages(self, days: int = 30):
        """오래된 메시지를 정리합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM chat_history
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"오래된 메시지 {deleted_count}개 정리 완료")
                return deleted_count
                
        except Exception as e:
            logger.error(f"메시지 정리 오류: {e}")
            return 0 