#!/usr/bin/env python3
"""
모드팩 관리 도구
GCP VM의 모든 모드팩을 스캔하고 사용자가 수동으로 선택하여 분석할 수 있게 해주는 도구
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path

# 백엔드 URL
BASE_URL = "http://localhost:5000"

def scan_vm_modpacks(base_paths: List[str] = None) -> List[Dict[str, Any]]:
    """VM에서 모드팩 디렉토리들을 스캔"""
    if base_paths is None:
        # 일반적인 모드팩 경로들
        base_paths = [
            "/home/user",
            os.path.expanduser("~"),
            "/opt/minecraft",
            "/var/minecraft",
            "."
        ]
    
    modpacks = []
    
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
            
        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # 모드팩 디렉토리인지 확인
                modpack_info = detect_modpack(item_path)
                if modpack_info:
                    modpacks.append(modpack_info)
                    
        except PermissionError:
            continue
    
    return modpacks

def detect_modpack(dir_path: str) -> Optional[Dict[str, Any]]:
    """디렉토리가 모드팩인지 확인하고 정보 추출"""
    dir_path = os.path.abspath(dir_path)
    dir_name = os.path.basename(dir_path)
    
    # 모드팩 식별 조건들
    modpack_indicators = [
        "mods",           # mods 폴더
        "config",         # config 폴더
        "kubejs",         # kubejs 폴더
        "data",           # data 폴더 (레시피)
        "server.properties", # 서버 설정
        "forge-installer", # 포지 설치 파일
        "start.sh",       # 시작 스크립트
        "run.sh"          # 실행 스크립트
    ]
    
    found_indicators = []
    for indicator in modpack_indicators:
        indicator_path = os.path.join(dir_path, indicator)
        if os.path.exists(indicator_path):
            found_indicators.append(indicator)
    
    # 최소 2개 이상의 지표가 있어야 모드팩으로 인식
    if len(found_indicators) < 2:
        return None
    
    # 모드 개수 확인
    mods_dir = os.path.join(dir_path, "mods")
    mod_count = 0
    if os.path.exists(mods_dir):
        try:
            mod_count = len([f for f in os.listdir(mods_dir) if f.endswith('.jar')])
        except:
            pass
    
    # 모드팩 버전 추정
    version = estimate_version(dir_path, dir_name)
    
    # 크기 계산
    try:
        size_mb = get_directory_size(dir_path) / (1024 * 1024)
    except:
        size_mb = 0
    
    return {
        "name": dir_name,
        "path": dir_path,
        "version": version,
        "mod_count": mod_count,
        "size_mb": int(size_mb),
        "indicators": found_indicators,
        "analyzable": mod_count > 0  # 모드가 있어야 분석 가능
    }

def estimate_version(dir_path: str, dir_name: str) -> str:
    """모드팩 버전 추정"""
    # 1. 디렉토리 이름에서 버전 추출 시도
    import re
    version_patterns = [
        r'v?(\d+\.\d+\.\d+)',  # v1.2.3 또는 1.2.3
        r'v?(\d+\.\d+)',       # v1.2 또는 1.2
        r'(\d+)$'              # 끝에 숫자
    ]
    
    for pattern in version_patterns:
        match = re.search(pattern, dir_name)
        if match:
            return match.group(1)
    
    # 2. manifest.json에서 추출 시도
    manifest_files = [
        "manifest.json",
        "modpack.json",
        "pack.json"
    ]
    
    for manifest_file in manifest_files:
        manifest_path = os.path.join(dir_path, manifest_file)
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'version' in data:
                        return str(data['version'])
                    if 'modpackVersion' in data:
                        return str(data['modpackVersion'])
            except:
                continue
    
    # 3. 기본값
    return "1.0.0"

def get_directory_size(dir_path: str) -> int:
    """디렉토리 크기 계산 (바이트)"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except:
        pass
    return total_size

def display_modpacks(modpacks: List[Dict[str, Any]]) -> None:
    """모드팩 목록을 표 형태로 출력"""
    if not modpacks:
        print("❌ 발견된 모드팩이 없습니다.")
        return
    
    print(f"\n📦 발견된 모드팩 목록 ({len(modpacks)}개):")
    print("=" * 80)
    print(f"{'번호':<4} {'모드팩 이름':<25} {'버전':<10} {'모드수':<8} {'크기(MB)':<10} {'분석가능'}")
    print("-" * 80)
    
    for i, modpack in enumerate(modpacks, 1):
        name = modpack['name'][:24]  # 길이 제한
        version = modpack['version'][:9]
        mod_count = modpack['mod_count']
        size_mb = modpack['size_mb']
        analyzable = "✅" if modpack['analyzable'] else "❌"
        
        print(f"{i:<4} {name:<25} {version:<10} {mod_count:<8} {size_mb:<10} {analyzable}")
    
    print("-" * 80)

def select_modpack(modpacks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """사용자가 모드팩을 선택하도록 함"""
    while True:
        try:
            choice = input(f"\n분석할 모드팩 번호를 선택하세요 (1-{len(modpacks)}, 0=취소): ")
            
            if choice == '0':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(modpacks):
                selected = modpacks[index]
                
                if not selected['analyzable']:
                    print("❌ 이 모드팩은 모드가 없어서 분석할 수 없습니다.")
                    continue
                
                return selected
            else:
                print("❌ 잘못된 번호입니다. 다시 입력해주세요.")
                
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n👋 취소되었습니다.")
            return None

def build_modpack_index(modpack: Dict[str, Any]) -> bool:
    """선택된 모드팩의 인덱스 구축"""
    print(f"\n🔨 모드팩 분석 시작: {modpack['name']}")
    print(f"📂 경로: {modpack['path']}")
    print(f"📊 모드 수: {modpack['mod_count']}개")
    print(f"💾 크기: {modpack['size_mb']}MB")
    
    # 예상 시간 및 비용 계산
    estimated_time = max(1, modpack['mod_count'] * 2 / 60)  # 모드당 2초 추정
    estimated_cost = modpack['size_mb'] * 0.0001  # 대략적 추정
    
    print(f"⏱️  예상 소요 시간: {estimated_time:.1f}분")
    print(f"💰 예상 비용: ~${estimated_cost:.3f}")
    
    # 사용자 확인
    confirm = input("계속 진행하시겠습니까? (y/N): ")
    if confirm.lower() != 'y':
        print("👋 취소되었습니다.")
        return False
    
    try:
        payload = {
            "modpack_name": modpack['name'],
            "modpack_version": modpack['version'],
            "modpack_path": modpack['path']
        }
        
        print("🚀 GCP RAG 인덱스 구축 중... (시간이 걸릴 수 있습니다)")
        response = requests.post(f"{BASE_URL}/gcp-rag/build", json=payload, timeout=600)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 인덱스 구축 성공!")
                print(f"📊 처리된 문서 수: {data.get('document_count')}")
                print(f"📈 통계: {data.get('stats')}")
                return True
            else:
                print(f"❌ 인덱스 구축 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 서버 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과 (10분). 모드팩이 너무 클 수 있습니다.")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def list_indexed_modpacks() -> List[Dict[str, Any]]:
    """이미 인덱싱된 모드팩 목록 조회"""
    try:
        response = requests.get(f"{BASE_URL}/gcp-rag/modpacks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('modpacks', [])
        else:
            print(f"❌ 인덱싱된 모드팩 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return []

def delete_modpack_index(modpack_name: str, modpack_version: str) -> bool:
    """모드팩 인덱스 삭제"""
    try:
        payload = {
            "modpack_name": modpack_name,
            "modpack_version": modpack_version
        }
        
        response = requests.delete(f"{BASE_URL}/gcp-rag/delete", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('success', False)
        else:
            print(f"❌ 삭제 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    print("🎮 모드팩 관리 도구")
    print("=" * 50)
    
    while True:
        print("\n📋 메뉴:")
        print("1. VM에서 모드팩 스캔 및 분석")
        print("2. 인덱싱된 모드팩 목록 보기") 
        print("3. 모드팩 인덱스 삭제")
        print("4. GCP RAG 시스템 상태 확인")
        print("0. 종료")
        
        try:
            choice = input("\n선택하세요 (0-4): ")
            
            if choice == '0':
                print("👋 안녕히 가세요!")
                break
                
            elif choice == '1':
                print("\n🔍 VM에서 모드팩 스캔 중...")
                
                # 사용자 정의 경로 입력받기
                custom_paths = input("추가 검색 경로가 있으면 입력하세요 (쉼표로 구분, Enter=기본 경로): ").strip()
                base_paths = None
                if custom_paths:
                    base_paths = [path.strip() for path in custom_paths.split(',')]
                
                modpacks = scan_vm_modpacks(base_paths)
                
                if not modpacks:
                    print("❌ 모드팩을 찾을 수 없습니다.")
                    print("💡 팁: 모드팩 디렉토리에는 'mods', 'config' 폴더가 있어야 합니다.")
                    continue
                
                display_modpacks(modpacks)
                selected = select_modpack(modpacks)
                
                if selected:
                    build_modpack_index(selected)
                    
            elif choice == '2':
                print("\n📦 인덱싱된 모드팩 조회 중...")
                indexed = list_indexed_modpacks()
                
                if not indexed:
                    print("❌ 인덱싱된 모드팩이 없습니다.")
                else:
                    print(f"\n📊 인덱싱된 모드팩 ({len(indexed)}개):")
                    print("-" * 60)
                    for i, modpack in enumerate(indexed, 1):
                        name = modpack.get('modpack_name', 'Unknown')
                        version = modpack.get('modpack_version', '1.0.0')
                        count = modpack.get('document_count', 0)
                        print(f"{i}. {name} v{version} ({count}개 문서)")
                    print("-" * 60)
                    
            elif choice == '3':
                print("\n🗑️  모드팩 인덱스 삭제")
                indexed = list_indexed_modpacks()
                
                if not indexed:
                    print("❌ 삭제할 인덱싱된 모드팩이 없습니다.")
                    continue
                
                print("\n삭제할 모드팩을 선택하세요:")
                for i, modpack in enumerate(indexed, 1):
                    name = modpack.get('modpack_name', 'Unknown')
                    version = modpack.get('modpack_version', '1.0.0')
                    count = modpack.get('document_count', 0)
                    print(f"{i}. {name} v{version} ({count}개 문서)")
                
                try:
                    delete_choice = input(f"삭제할 번호 (1-{len(indexed)}, 0=취소): ")
                    if delete_choice == '0':
                        continue
                        
                    index = int(delete_choice) - 1
                    if 0 <= index < len(indexed):
                        selected = indexed[index]
                        name = selected['modpack_name']
                        version = selected['modpack_version']
                        
                        confirm = input(f"'{name} v{version}'을(를) 정말 삭제하시겠습니까? (y/N): ")
                        if confirm.lower() == 'y':
                            if delete_modpack_index(name, version):
                                print(f"✅ '{name} v{version}' 삭제 완료")
                            else:
                                print("❌ 삭제 실패")
                        else:
                            print("👋 취소되었습니다.")
                    else:
                        print("❌ 잘못된 번호입니다.")
                        
                except ValueError:
                    print("❌ 숫자를 입력해주세요.")
                    
            elif choice == '4':
                print("\n🔍 GCP RAG 시스템 상태 확인 중...")
                try:
                    response = requests.get(f"{BASE_URL}/gcp-rag/status", timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        print("✅ 상태 조회 성공:")
                        print(f"   - GCP RAG 활성화: {data.get('gcp_rag_enabled')}")
                        print(f"   - GCP RAG 사용 가능: {data.get('gcp_rag_available')}")
                        print(f"   - 프로젝트 ID: {data.get('project_id')}")
                        print(f"   - 리전: {data.get('location')}")
                        print(f"   - 로컬 RAG 활성화: {data.get('local_rag_enabled')}")
                    else:
                        print(f"❌ 상태 확인 실패: {response.status_code}")
                except Exception as e:
                    print(f"❌ 연결 실패: {e}")
                    print("💡 백엔드 서버가 실행 중인지 확인하세요 (python app.py)")
                    
            else:
                print("❌ 잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()