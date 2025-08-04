#!/usr/bin/env python3
"""
개발 및 디버깅 도구 스크립트
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

def run_tests():
    """테스트 실행"""
    print("🧪 테스트 실행 중...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("오류:", result.stderr)
    return result.returncode == 0

def check_code_quality():
    """코드 품질 검사"""
    print("🔍 코드 품질 검사 중...")
    
    # flake8 설치 확인 및 실행
    try:
        result = subprocess.run([sys.executable, "-m", "flake8", "backend/"], 
                              capture_output=True, text=True)
        if result.stdout:
            print("코드 스타일 문제:")
            print(result.stdout)
        else:
            print("✅ 코드 스타일 검사 통과")
    except FileNotFoundError:
        print("⚠️ flake8이 설치되지 않았습니다. 'pip install flake8'로 설치하세요.")

def generate_docs():
    """문서 생성"""
    print("📚 문서 생성 중...")
    
    # API 문서 생성
    try:
        from backend.app import app
        with app.test_client() as client:
            # API 엔드포인트 목록 생성
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'rule': str(rule)
                })
            
            # JSON 파일로 저장
            with open('api_documentation.json', 'w', encoding='utf-8') as f:
                json.dump(routes, f, indent=2, ensure_ascii=False)
            
            print("✅ API 문서가 api_documentation.json에 생성되었습니다.")
    except Exception as e:
        print(f"❌ 문서 생성 실패: {e}")

def check_dependencies():
    """의존성 검사"""
    print("📦 의존성 검사 중...")
    
    # requirements.txt 확인
    if os.path.exists('backend/requirements.txt'):
        print("✅ requirements.txt 존재")
        
        # 설치된 패키지와 비교
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                                  capture_output=True, text=True)
            installed_packages = result.stdout.lower()
            
            with open('backend/requirements.txt', 'r') as f:
                required_packages = f.read().lower()
            
            missing_packages = []
            for line in required_packages.split('\n'):
                if line.strip() and not line.startswith('#'):
                    package_name = line.split('==')[0].strip()
                    if package_name not in installed_packages:
                        missing_packages.append(package_name)
            
            if missing_packages:
                print(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
            else:
                print("✅ 모든 의존성이 설치되어 있습니다.")
        except Exception as e:
            print(f"⚠️ 의존성 검사 중 오류: {e}")
    else:
        print("❌ requirements.txt를 찾을 수 없습니다.")

def validate_config():
    """설정 유효성 검사"""
    print("⚙️ 설정 유효성 검사 중...")
    
    try:
        from backend.utils.config import config
        errors = config.validate()
        
        if errors:
            print("❌ 설정 오류:")
            for key, message in errors.items():
                print(f"  - {key}: {message}")
        else:
            print("✅ 설정이 유효합니다.")
        
        # 설정 정보 출력 (민감한 정보 제외)
        safe_config = config.to_dict()
        print("\n📋 현재 설정:")
        for key, value in safe_config.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ 설정 검사 실패: {e}")

def run_linter():
    """린터 실행"""
    print("🔧 린터 실행 중...")
    
    # Python 파일 검사
    python_files = list(Path('backend').rglob('*.py'))
    
    for file_path in python_files:
        print(f"검사 중: {file_path}")
        try:
            result = subprocess.run([sys.executable, "-m", "py_compile", str(file_path)], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {file_path}: 구문 오류")
                print(result.stderr)
            else:
                print(f"✅ {file_path}: 구문 검사 통과")
        except Exception as e:
            print(f"⚠️ {file_path} 검사 중 오류: {e}")

def create_debug_report():
    """디버그 리포트 생성"""
    print("📊 디버그 리포트 생성 중...")
    
    report = {
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform,
            'current_directory': os.getcwd()
        },
        'project_structure': {},
        'config_status': {},
        'dependencies': {}
    }
    
    # 프로젝트 구조 확인
    for root, dirs, files in os.walk('.'):
        if '.git' in root or '__pycache__' in root:
            continue
        rel_path = os.path.relpath(root, '.')
        report['project_structure'][rel_path] = {
            'directories': dirs,
            'files': [f for f in files if not f.startswith('.')]
        }
    
    # 설정 상태 확인
    try:
        from backend.utils.config import config
        report['config_status'] = config.to_dict()
    except Exception as e:
        report['config_status']['error'] = str(e)
    
    # 의존성 정보
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        report['dependencies']['installed'] = result.stdout
    except Exception as e:
        report['dependencies']['error'] = str(e)
    
    # 리포트 저장
    with open('debug_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✅ 디버그 리포트가 debug_report.json에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(description='개발 및 디버깅 도구')
    parser.add_argument('command', choices=[
        'test', 'quality', 'docs', 'deps', 'config', 'lint', 'report', 'all'
    ], help='실행할 명령어')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        run_tests()
    elif args.command == 'quality':
        check_code_quality()
    elif args.command == 'docs':
        generate_docs()
    elif args.command == 'deps':
        check_dependencies()
    elif args.command == 'config':
        validate_config()
    elif args.command == 'lint':
        run_linter()
    elif args.command == 'report':
        create_debug_report()
    elif args.command == 'all':
        print("🚀 전체 검사 실행 중...\n")
        run_tests()
        print()
        check_code_quality()
        print()
        generate_docs()
        print()
        check_dependencies()
        print()
        validate_config()
        print()
        run_linter()
        print()
        create_debug_report()
        print("\n✅ 전체 검사 완료!")

if __name__ == '__main__':
    main() 