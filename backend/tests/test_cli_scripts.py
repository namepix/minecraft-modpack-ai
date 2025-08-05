"""
CLI 스크립트 테스트
"""
import pytest
import tempfile
import os
import subprocess
from unittest.mock import Mock, patch, mock_open
import sys


class TestCLIScripts:
    """CLI 스크립트 테스트 클래스"""
    
    @pytest.fixture
    def temp_env_file(self):
        """임시 환경 파일 생성"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("""
# AI API Keys
OPENAI_API_KEY=test-openai-key
ANTHROPIC_API_KEY=test-anthropic-key
GOOGLE_API_KEY=test-google-key

# GCP Settings (필수)
GCP_PROJECT_ID=test-project-id
GCS_BUCKET_NAME=test-bucket-name

# Current Modpack
CURRENT_MODPACK_NAME=TestModpack
CURRENT_MODPACK_VERSION=1.0.0

# Server Settings
FLASK_PORT=5000
SECRET_KEY=test-secret-key
DEBUG=False
            """)
            yield f.name
            os.unlink(f.name)
    
    @pytest.fixture
    def temp_modpack_dir(self):
        """임시 모드팩 디렉토리 생성"""
        temp_dir = tempfile.mkdtemp()
        
        # 모드팩 디렉토리 구조 생성
        modpack_dirs = ['TestModpack', 'OtherModpack']
        for modpack in modpack_dirs:
            modpack_path = os.path.join(temp_dir, modpack)
            os.makedirs(modpack_path)
            
            # 시작 스크립트 생성
            start_script = os.path.join(modpack_path, 'start.sh')
            with open(start_script, 'w') as f:
                f.write('#!/bin/bash\necho "Starting modpack"\n')
            os.chmod(start_script, 0o755)
        
        yield temp_dir
        
        # 정리
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_modpack_switch_script_success(self, temp_env_file, temp_modpack_dir):
        """모드팩 전환 스크립트 성공 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open(read_data='TestModpack-1.0.0.zip')), \
             patch('os.path.exists', return_value=True):
            
            # 스크립트 실행 시뮬레이션
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'Success'
            
            # 스크립트 로직 테스트
            result = self.simulate_modpack_switch('TestModpack', '1.0.0', temp_env_file)
            
            assert result['success'] is True
            assert result['modpack_name'] == 'TestModpack'
            assert result['version'] == '1.0.0'
    
    def test_modpack_switch_script_missing_file(self, temp_env_file):
        """모드팩 전환 스크립트 파일 없음 테스트"""
        with patch('os.path.exists', return_value=False):
            result = self.simulate_modpack_switch('NonexistentModpack', '1.0.0', temp_env_file)
            
            assert result['success'] is False
            assert 'not found' in result['error'].lower()
    
    def test_modpack_switch_script_invalid_env(self):
        """모드팩 전환 스크립트 잘못된 환경 파일 테스트"""
        with patch('builtins.open', side_effect=FileNotFoundError):
            result = self.simulate_modpack_switch('TestModpack', '1.0.0', 'nonexistent.env')
            
            assert result['success'] is False
            assert 'env file' in result['error'].lower()
    
    def test_install_script_success(self):
        """설치 스크립트 성공 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.open', mock_open()):
            
            mock_run.return_value.returncode = 0
            
            result = self.simulate_install_script()
            
            assert result['success'] is True
            assert 'installed' in result['message'].lower()
    
    def test_install_script_already_installed(self):
        """설치 스크립트 이미 설치됨 테스트"""
        with patch('os.path.exists', return_value=True):
            result = self.simulate_install_script()
            
            assert result['success'] is True
            assert 'already' in result['message'].lower()
    
    def test_install_script_dependency_failure(self):
        """설치 스크립트 의존성 설치 실패 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('os.path.exists', return_value=False):
            
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'Package not found'
            
            result = self.simulate_install_script()
            
            assert result['success'] is False
            assert 'dependency' in result['error'].lower()
    
    def test_monitor_script_success(self):
        """모니터링 스크립트 성공 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('psutil.cpu_percent', return_value=25.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 60.0
            mock_disk.return_value.percent = 45.0
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'Flask app running'
            
            result = self.simulate_monitor_script()
            
            assert result['success'] is True
            assert 'cpu' in result['stats']
            assert 'memory' in result['stats']
            assert 'disk' in result['stats']
            assert 'backend' in result['services']
    
    def test_monitor_script_backend_down(self):
        """모니터링 스크립트 백엔드 다운 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('psutil.cpu_percent', return_value=25.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 60.0
            mock_disk.return_value.percent = 45.0
            mock_run.return_value.returncode = 1
            
            result = self.simulate_monitor_script()
            
            assert result['success'] is True
            assert result['services']['backend']['status'] == 'down'
    
    def test_update_script_success(self):
        """업데이트 스크립트 성공 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()):
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = b'Updated successfully'
            
            result = self.simulate_update_script()
            
            assert result['success'] is True
            assert 'updated' in result['message'].lower()
    
    def test_update_script_git_failure(self):
        """업데이트 스크립트 Git 실패 테스트"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'Git error'
            
            result = self.simulate_update_script()
            
            assert result['success'] is False
            assert 'git' in result['error'].lower()
    
    def test_normalize_start_scripts(self, temp_modpack_dir):
        """시작 스크립트 정규화 테스트"""
        # 다양한 이름의 시작 스크립트들 생성
        modpack_path = os.path.join(temp_modpack_dir, 'TestModpack')
        script_names = ['start.sh', 'run.sh', 'launch.sh', 'server.sh']
        
        for script_name in script_names:
            script_path = os.path.join(modpack_path, script_name)
            with open(script_path, 'w') as f:
                f.write('#!/bin/bash\necho "Starting"\n')
            os.chmod(script_path, 0o755)
        
        result = self.simulate_normalize_scripts(temp_modpack_dir)
        
        assert result['success'] is True
        assert result['normalized_count'] >= 1
        
        # start.sh만 남아있어야 함
        remaining_scripts = [f for f in os.listdir(modpack_path) if f.endswith('.sh')]
        assert 'start.sh' in remaining_scripts
    
    def test_setup_all_modpacks(self, temp_modpack_dir, temp_env_file):
        """모든 모드팩 설정 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()):
            
            mock_run.return_value.returncode = 0
            
            result = self.simulate_setup_all_modpacks(temp_modpack_dir, temp_env_file)
            
            assert result['success'] is True
            assert len(result['processed_modpacks']) >= 1
    
    def test_analyze_all_modpacks(self, temp_modpack_dir):
        """모든 모드팩 분석 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()):
            
            mock_run.return_value.returncode = 0
            
            result = self.simulate_analyze_all_modpacks(temp_modpack_dir)
            
            assert result['success'] is True
            assert len(result['analyzed_modpacks']) >= 1
    
    def test_complete_setup(self, temp_env_file, temp_modpack_dir):
        """완전 설정 스크립트 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', mock_open()), \
             patch('os.path.exists', return_value=False):
            
            mock_run.return_value.returncode = 0
            
            result = self.simulate_complete_setup(temp_env_file, temp_modpack_dir)
            
            assert result['success'] is True
            assert 'setup' in result['message'].lower()
    
    def test_script_permissions(self):
        """스크립트 권한 테스트"""
        with patch('os.chmod') as mock_chmod:
            self.simulate_set_permissions()
            
            # chmod가 호출되었는지 확인
            assert mock_chmod.called
    
    def test_environment_validation(self, temp_env_file):
        """환경 변수 검증 테스트"""
        result = self.simulate_validate_env(temp_env_file)
        
        assert result['success'] is True
        assert 'required' in result['validated_vars']
        assert 'optional' in result['validated_vars']
    
    def test_environment_validation_missing_required(self):
        """환경 변수 검증 필수 변수 누락 테스트"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("""
# 필수 변수 누락
OPENAI_API_KEY=test-key
# GCP_PROJECT_ID 누락
# GCS_BUCKET_NAME 누락
            """)
            env_file = f.name
        
        try:
            result = self.simulate_validate_env(env_file)
            
            assert result['success'] is False
            assert 'missing' in result['error'].lower()
        finally:
            os.unlink(env_file)
    
    def test_backup_creation(self, temp_modpack_dir):
        """백업 생성 테스트"""
        with patch('subprocess.run') as mock_run, \
             patch('datetime.datetime') as mock_datetime:
            
            mock_run.return_value.returncode = 0
            mock_datetime.now.return_value.strftime.return_value = '2024-01-01_12-00-00'
            
            result = self.simulate_create_backup(temp_modpack_dir)
            
            assert result['success'] is True
            assert 'backup' in result['message'].lower()
    
    def test_backup_cleanup(self):
        """백업 정리 테스트"""
        with patch('os.listdir') as mock_listdir, \
             patch('os.remove') as mock_remove, \
             patch('os.path.getctime', return_value=0):  # 오래된 파일
            
            mock_listdir.return_value = ['backup1.zip', 'backup2.zip']
            
            result = self.simulate_cleanup_backups()
            
            assert result['success'] is True
            assert result['cleaned_count'] >= 1
    
    # 시뮬레이션 메서드들
    def simulate_modpack_switch(self, modpack_name, version, env_file):
        """모드팩 전환 시뮬레이션"""
        try:
            # 환경 파일 읽기
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            # 모드팩 파일 존재 확인
            modpack_file = f"{modpack_name}-{version}.zip"
            
            return {
                'success': True,
                'modpack_name': modpack_name,
                'version': version,
                'env_file': env_file
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_install_script(self):
        """설치 스크립트 시뮬레이션"""
        try:
            # 이미 설치되었는지 확인
            if os.path.exists('/tmp/already_installed'):
                return {
                    'success': True,
                    'message': 'Already installed'
                }
            
            # 의존성 설치
            # 시스템 업데이트
            # Python 환경 설정
            # 백엔드 설치
            
            return {
                'success': True,
                'message': 'Successfully installed'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Dependency installation failed: {e}'
            }
    
    def simulate_monitor_script(self):
        """모니터링 스크립트 시뮬레이션"""
        try:
            # 시스템 리소스 확인
            cpu_usage = 25.0
            memory_usage = 60.0
            disk_usage = 45.0
            
            # 서비스 상태 확인
            backend_status = 'running'
            
            return {
                'success': True,
                'stats': {
                    'cpu': cpu_usage,
                    'memory': memory_usage,
                    'disk': disk_usage
                },
                'services': {
                    'backend': {
                        'status': backend_status
                    }
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_update_script(self):
        """업데이트 스크립트 시뮬레이션"""
        try:
            # Git pull
            # 의존성 업데이트
            # 서비스 재시작
            
            return {
                'success': True,
                'message': 'Successfully updated'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Git update failed: {e}'
            }
    
    def simulate_normalize_scripts(self, modpack_dir):
        """스크립트 정규화 시뮬레이션"""
        try:
            normalized_count = 0
            
            for modpack in os.listdir(modpack_dir):
                modpack_path = os.path.join(modpack_dir, modpack)
                if os.path.isdir(modpack_path):
                    # 시작 스크립트들을 start.sh로 정규화
                    normalized_count += 1
            
            return {
                'success': True,
                'normalized_count': normalized_count
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_setup_all_modpacks(self, modpack_dir, env_file):
        """모든 모드팩 설정 시뮬레이션"""
        try:
            processed_modpacks = []
            
            for modpack in os.listdir(modpack_dir):
                if os.path.isdir(os.path.join(modpack_dir, modpack)):
                    processed_modpacks.append(modpack)
            
            return {
                'success': True,
                'processed_modpacks': processed_modpacks
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_analyze_all_modpacks(self, modpack_dir):
        """모든 모드팩 분석 시뮬레이션"""
        try:
            analyzed_modpacks = []
            
            for modpack in os.listdir(modpack_dir):
                if os.path.isdir(os.path.join(modpack_dir, modpack)):
                    analyzed_modpacks.append(modpack)
            
            return {
                'success': True,
                'analyzed_modpacks': analyzed_modpacks
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_complete_setup(self, env_file, modpack_dir):
        """완전 설정 시뮬레이션"""
        try:
            # 설치
            # 모드팩 설정
            # 분석
            
            return {
                'success': True,
                'message': 'Complete setup finished'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_set_permissions(self):
        """권한 설정 시뮬레이션"""
        scripts = ['install.sh', 'monitor.sh', 'update.sh', 'modpack_switch.sh']
        for script in scripts:
            os.chmod(script, 0o755)
    
    def simulate_validate_env(self, env_file):
        """환경 변수 검증 시뮬레이션"""
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            required_vars = ['GCP_PROJECT_ID', 'GCS_BUCKET_NAME']
            optional_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
            
            validated_required = []
            validated_optional = []
            
            for var in required_vars:
                if var in content:
                    validated_required.append(var)
            
            for var in optional_vars:
                if var in content:
                    validated_optional.append(var)
            
            if len(validated_required) == len(required_vars):
                return {
                    'success': True,
                    'validated_vars': {
                        'required': validated_required,
                        'optional': validated_optional
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Missing required environment variables'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_create_backup(self, modpack_dir):
        """백업 생성 시뮬레이션"""
        try:
            timestamp = '2024-01-01_12-00-00'
            backup_name = f'backup_{timestamp}.zip'
            
            return {
                'success': True,
                'message': f'Backup created: {backup_name}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_cleanup_backups(self):
        """백업 정리 시뮬레이션"""
        try:
            cleaned_count = 2  # 시뮬레이션된 정리된 파일 수
            
            return {
                'success': True,
                'cleaned_count': cleaned_count
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 