import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import json

class Config:
    """중앙화된 설정 관리 시스템"""
    
    def __init__(self):
        load_dotenv()
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """환경 변수에서 설정 로드"""
        self._config = {
            # AI 모델 설정
            'default_ai_model': os.getenv('DEFAULT_AI_MODEL', 'gpt-3.5-turbo'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
            'google_api_key': os.getenv('GOOGLE_API_KEY'),
            
            # GCP 설정
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcs_bucket_name': os.getenv('GCS_BUCKET_NAME'),
            
            # 모드팩 설정
            'current_modpack_name': os.getenv('CURRENT_MODPACK_NAME', 'enigmatica_10'),
            'current_modpack_version': os.getenv('CURRENT_MODPACK_VERSION', '1.0.0'),
            'modpack_upload_dir': os.getenv('MODPACK_UPLOAD_DIR', '/tmp/modpacks'),
            'modpack_backup_dir': os.getenv('MODPACK_BACKUP_DIR'),
            
            # 서버 설정
            'port': int(os.getenv('PORT', 5000)),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            
            # 데이터베이스 설정
            'database_url': os.getenv('DATABASE_URL', 'sqlite:///minecraft_ai.db'),
            
            # 보안 설정
            'secret_key': os.getenv('SECRET_KEY', 'your-secret-key-here'),
            'allowed_origins': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
            
            # 성능 설정
            'max_content_length': int(os.getenv('MAX_CONTENT_LENGTH', 16)) * 1024 * 1024,  # MB to bytes
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', 30)),
            
            # 모니터링 설정
            'log_file': os.getenv('LOG_FILE'),
            'backup_retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', 7)),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 가져오기"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """설정 값 설정하기"""
        self._config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """여러 설정 값 업데이트"""
        self._config.update(updates)
    
    def save_to_env(self, file_path: Optional[str] = None):
        """설정을 .env 파일에 저장"""
        if not file_path:
            file_path = os.path.join(os.path.expanduser("~"), "minecraft-ai-backend", ".env")
        
        env_content = []
        for key, value in self._config.items():
            if value is not None:
                if isinstance(value, list):
                    env_content.append(f"{key.upper()}={','.join(value)}")
                else:
                    env_content.append(f"{key.upper()}={value}")
        
        with open(file_path, 'w') as f:
            f.write('\n'.join(env_content))
    
    def validate(self) -> Dict[str, str]:
        """설정 유효성 검사"""
        errors = {}
        
        # 필수 설정 확인
        required_settings = {
            'openai_api_key': 'OpenAI API 키가 필요합니다.',
            'secret_key': '보안을 위해 SECRET_KEY를 설정하세요.',
            'gcp_project_id': 'RAG 기능을 위해 GCP_PROJECT_ID가 필요합니다.',
            'gcs_bucket_name': 'RAG 기능을 위해 GCS_BUCKET_NAME이 필요합니다.',
        }
        
        for key, message in required_settings.items():
            if not self.get(key):
                errors[key] = message
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 반환 (민감한 정보 제외)"""
        safe_config = self._config.copy()
        # 민감한 정보 제거
        sensitive_keys = ['openai_api_key', 'anthropic_api_key', 'google_api_key', 'secret_key']
        for key in sensitive_keys:
            if key in safe_config:
                safe_config[key] = '***HIDDEN***'
        return safe_config

# 전역 설정 인스턴스
config = Config() 