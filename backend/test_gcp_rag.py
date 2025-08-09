#!/usr/bin/env python3
"""
GCP RAG 시스템 테스트 스크립트
실제 모드팩 데이터로 RAG 검색 결과를 확인하는 도구
"""

import os
import json
import requests
from typing import Dict, Any

# 백엔드 URL
BASE_URL = "http://localhost:5000"

def test_gcp_rag_status():
    """GCP RAG 시스템 상태 확인"""
    print("🔍 GCP RAG 시스템 상태 확인 중...")
    
    try:
        response = requests.get(f"{BASE_URL}/gcp-rag/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 상태 조회 성공:")
            print(f"   - GCP RAG 활성화: {data.get('gcp_rag_enabled')}")
            print(f"   - GCP RAG 사용 가능: {data.get('gcp_rag_available')}")
            print(f"   - 프로젝트 ID: {data.get('project_id')}")
            print(f"   - 로컬 RAG 활성화: {data.get('local_rag_enabled')}")
            return data.get('gcp_rag_available', False)
        else:
            print(f"❌ 상태 조회 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def test_modpack_list():
    """등록된 모드팩 목록 확인"""
    print("\n📦 등록된 모드팩 목록 확인 중...")
    
    try:
        response = requests.get(f"{BASE_URL}/gcp-rag/modpacks")
        if response.status_code == 200:
            data = response.json()
            modpacks = data.get('modpacks', [])
            print(f"✅ 모드팩 {len(modpacks)}개 등록됨:")
            for modpack in modpacks:
                name = modpack.get('modpack_name')
                version = modpack.get('modpack_version')
                count = modpack.get('document_count')
                print(f"   - {name} v{version} ({count}개 문서)")
            return modpacks
        else:
            print(f"❌ 목록 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return []

def test_build_index(modpack_name: str, modpack_version: str, modpack_path: str):
    """모드팩 인덱스 구축 테스트"""
    print(f"\n🔨 모드팩 인덱스 구축 테스트: {modpack_name} v{modpack_version}")
    
    if not os.path.exists(modpack_path):
        print(f"❌ 모드팩 경로가 존재하지 않음: {modpack_path}")
        return False
    
    try:
        payload = {
            "modpack_name": modpack_name,
            "modpack_version": modpack_version,
            "modpack_path": modpack_path
        }
        
        response = requests.post(f"{BASE_URL}/gcp-rag/build", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 인덱스 구축 성공:")
                print(f"   - 문서 수: {data.get('document_count')}")
                print(f"   - 컬렉션: {data.get('collection_name')}")
                print(f"   - 통계: {data.get('stats')}")
                return True
            else:
                print(f"❌ 인덱스 구축 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return False

def test_search(query: str, modpack_name: str, modpack_version: str, top_k: int = 5):
    """검색 테스트 및 결과 확인"""
    print(f"\n🔍 검색 테스트: '{query}'")
    
    try:
        payload = {
            "query": query,
            "modpack_name": modpack_name,
            "modpack_version": modpack_version,
            "top_k": top_k,
            "min_score": 0.7
        }
        
        response = requests.post(f"{BASE_URL}/gcp-rag/search", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', [])
                print(f"✅ 검색 성공: {len(results)}개 결과")
                
                for i, result in enumerate(results[:3], 1):
                    print(f"\n📄 결과 {i}:")
                    print(f"   - 유사도: {result.get('similarity', 0):.3f}")
                    print(f"   - 문서 타입: {result.get('doc_type')}")
                    print(f"   - 출처: {result.get('doc_source', 'unknown')}")
                    print(f"   - 내용: {result.get('text', '')[:200]}...")
                
                return results
            else:
                print(f"❌ 검색 실패: {data.get('error')}")
                return []
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return []

def test_chat_with_rag(message: str, modpack_name: str, modpack_version: str):
    """RAG가 적용된 채팅 테스트"""
    print(f"\n💬 RAG 적용 채팅 테스트: '{message}'")
    
    try:
        payload = {
            "message": message,
            "player_uuid": "test-player",
            "modpack_name": modpack_name,
            "modpack_version": modpack_version
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 채팅 성공:")
                print(f"   - AI 모델: {data.get('model')}")
                print(f"   - RAG 사용: {data.get('rag', {}).get('used', False)}")
                print(f"   - RAG 히트: {data.get('rag', {}).get('hits', 0)}")
                print(f"   - 사용된 문자수: {data.get('rag', {}).get('used_chars', 0)}")
                print(f"\n🤖 AI 응답:")
                print(f"   {data.get('response', '')[:300]}...")
                
                # RAG 디버그 정보
                rag_info = data.get('rag', {}).get('debug_info', {})
                if rag_info:
                    print(f"\n🔍 RAG 디버그 정보:")
                    print(json.dumps(rag_info, indent=2, ensure_ascii=False))
                
                return data
            else:
                print(f"❌ 채팅 실패: {data.get('error')}")
                return None
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 GCP RAG 시스템 종합 테스트 시작")
    print("=" * 60)
    
    # 1. 시스템 상태 확인
    if not test_gcp_rag_status():
        print("\n❌ GCP RAG 시스템이 비활성화되어 있습니다.")
        print("💡 다음 단계를 확인하세요:")
        print("   1. ./install_gcp_rag.sh 실행")
        print("   2. .env 파일에 GCP_PROJECT_ID 설정")
        print("   3. GCP 인증 설정 (서비스 계정 키 또는 gcloud auth)")
        return
    
    # 2. 모드팩 목록 확인
    modpacks = test_modpack_list()
    
    # 3. 테스트 모드팩 설정 (실제 환경에 맞게 수정)
    test_modpack_name = input("\n📝 테스트할 모드팩 이름을 입력하세요 (예: enigmatica_6): ")
    test_modpack_version = input("📝 모드팩 버전을 입력하세요 (예: 1.0.0): ")
    
    # 인덱스가 없다면 구축할지 물어보기
    existing_modpack = None
    for modpack in modpacks:
        if (modpack.get('modpack_name') == test_modpack_name and 
            modpack.get('modpack_version') == test_modpack_version):
            existing_modpack = modpack
            break
    
    if not existing_modpack:
        print(f"\n📦 '{test_modpack_name} v{test_modpack_version}' 인덱스가 없습니다.")
        should_build = input("인덱스를 구축하시겠습니까? (y/N): ")
        if should_build.lower() == 'y':
            modpack_path = input("모드팩 경로를 입력하세요: ")
            if not test_build_index(test_modpack_name, test_modpack_version, modpack_path):
                return
    
    # 4. 검색 테스트
    test_queries = [
        "iron block recipe",
        "다이아몬드 검 만들기",
        "thermal expansion",
        "applied energistics 2"
    ]
    
    print(f"\n🔍 검색 테스트 시작...")
    for query in test_queries:
        results = test_search(query, test_modpack_name, test_modpack_version)
        if results:
            print(f"   ✅ '{query}': {len(results)}개 결과")
        else:
            print(f"   ❌ '{query}': 결과 없음")
    
    # 5. 통합 채팅 테스트
    chat_messages = [
        "철 블록을 만드는 방법을 알려줘",
        "thermal expansion 모드에 대해 설명해줘",
        "가장 유용한 아이템 5개를 추천해줘"
    ]
    
    print(f"\n💬 통합 채팅 테스트 시작...")
    for message in chat_messages:
        result = test_chat_with_rag(message, test_modpack_name, test_modpack_version)
        if result:
            print(f"   ✅ 채팅 성공")
        else:
            print(f"   ❌ 채팅 실패")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    main()