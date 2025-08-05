#!/usr/bin/env python3
"""
테스트 실행 스크립트
"""
import sys
import subprocess
import os
from pathlib import Path

def run_tests(test_type="all", coverage=True, verbose=True):
    """테스트를 실행합니다."""
    
    # 현재 디렉토리를 backend로 변경
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 기본 pytest 명령어 구성
    cmd = ["python", "-m", "pytest"]
    
    # 테스트 타입에 따른 필터링
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "web":
        cmd.extend(["-m", "web"])
    
    # 커버리지 설정
    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # 상세 출력
    if verbose:
        cmd.append("-v")
    
    # 테스트 디렉토리 추가
    cmd.append("tests/")
    
    print(f"실행 명령어: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("=" * 50)
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 50)
        print(f"❌ 테스트 실행 중 오류가 발생했습니다: {e}")
        return False

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python run_tests.py [test_type] [--no-coverage] [--quiet]")
        print("\n테스트 타입:")
        print("  all          - 모든 테스트 (기본값)")
        print("  unit         - 단위 테스트만")
        print("  integration  - 통합 테스트만")
        print("  fast         - 빠른 테스트 (slow 제외)")
        print("  web          - 웹 관련 테스트만")
        print("\n옵션:")
        print("  --no-coverage - 커버리지 보고서 비활성화")
        print("  --quiet       - 상세 출력 비활성화")
        return
    
    test_type = "all"
    coverage = True
    verbose = True
    
    # 인자 파싱
    for arg in sys.argv[1:]:
        if arg in ["unit", "integration", "fast", "web", "all"]:
            test_type = arg
        elif arg == "--no-coverage":
            coverage = False
        elif arg == "--quiet":
            verbose = False
    
    print(f"🧪 {test_type} 테스트를 실행합니다...")
    success = run_tests(test_type, coverage, verbose)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 