#!/usr/bin/env python3
"""
RAG 관리 도구 - 수동 모드팩 인덱싱 및 관리

사용법:
    python rag_manager.py build <모드팩_이름> <모드팩_버전> <모드팩_경로>
    python rag_manager.py list
    python rag_manager.py delete <모드팩_이름> <모드팩_버전>
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# 현재 스크립트와 같은 디렉토리에서 모듈 import
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from gcp_rag_system import gcp_rag
from modpack_parser import scan_modpack


def build_single_modpack(name: str, version: str, path: str) -> bool:
    """단일 모드팩 RAG 인덱스 구축"""
    print(f"\n🔨 RAG 인덱스 구축 시작: {name} v{version}")
    print(f"📁 경로: {path}")
    
    if not os.path.exists(path):
        print(f"❌ 오류: 모드팩 경로를 찾을 수 없습니다: {path}")
        return False
    
    if not gcp_rag.is_enabled():
        print("❌ 오류: GCP RAG 시스템이 비활성화되어 있습니다.")
        print("💡 해결 방법:")
        print("   1. .env 파일에 GCP_PROJECT_ID 설정")
        print("   2. Google Cloud 인증 설정 (gcloud auth application-default login)")
        return False
    
    try:
        result = gcp_rag.build_modpack_index(name, version, path)
        
        if result.get('success'):
            print(f"✅ 인덱스 구축 성공!")
            print(f"   📄 문서 수: {result.get('document_count', 0)}")
            print(f"   📊 통계: {result.get('stats', {})}")
            return True
        else:
            print(f"❌ 인덱스 구축 실패: {result.get('error', '알 수 없는 오류')}")
            return False
            
    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")
        return False


def list_modpacks() -> None:
    """등록된 모드팩 목록 표시"""
    print("\n📦 등록된 모드팩 목록:")
    
    if not gcp_rag.is_enabled():
        print("❌ GCP RAG 시스템이 비활성화되어 있습니다.")
        return
    
    try:
        modpacks = gcp_rag.get_modpack_list()
        
        if not modpacks:
            print("   (등록된 모드팩이 없습니다)")
            return
        
        for i, modpack in enumerate(modpacks, 1):
            name = modpack.get('modpack_name', 'Unknown')
            version = modpack.get('modpack_version', '1.0.0')
            doc_count = modpack.get('document_count', 0)
            created = modpack.get('created_at', 'Unknown')
            
            print(f"\n   {i}. {name} v{version}")
            print(f"      📄 문서: {doc_count}개")
            print(f"      📅 생성: {created}")
    
    except Exception as e:
        print(f"❌ 모드팩 목록 조회 실패: {str(e)}")


def delete_modpack(name: str, version: str) -> bool:
    """모드팩 RAG 인덱스 삭제"""
    print(f"\n🗑️ RAG 인덱스 삭제: {name} v{version}")
    
    if not gcp_rag.is_enabled():
        print("❌ GCP RAG 시스템이 비활성화되어 있습니다.")
        return False
    
    try:
        # 확인 메시지
        response = input(f"정말로 '{name} v{version}' 인덱스를 삭제하시겠습니까? (yes/no): ")
        if response.lower() not in ['yes', 'y', '예']:
            print("삭제가 취소되었습니다.")
            return False
        
        success = gcp_rag.delete_modpack_index(name, version)
        
        if success:
            print("✅ 인덱스 삭제 완료!")
            return True
        else:
            print("❌ 인덱스 삭제 실패")
            return False
            
    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")
        return False


def preview_modpack(path: str) -> None:
    """모드팩 구조 미리보기"""
    print(f"\n👁️ 모드팩 구조 미리보기: {path}")
    
    if not os.path.exists(path):
        print(f"❌ 경로를 찾을 수 없습니다: {path}")
        return
    
    try:
        result = scan_modpack(path)
        docs = result.get('docs', [])
        stats = result.get('stats', {})
        
        print(f"📊 스캔 결과:")
        print(f"   📄 총 문서: {len(docs)}개")
        print(f"   🧩 모드: {stats.get('mods', 0)}개")
        print(f"   📜 레시피: {stats.get('recipes', 0)}개")
        print(f"   📝 KubeJS: {stats.get('kubejs', 0)}개")
        
        if docs:
            print(f"\n📋 문서 미리보기 (상위 5개):")
            for i, doc in enumerate(docs[:5], 1):
                doc_type = doc.get('type', 'unknown')
                source = doc.get('source', 'unknown')
                text_preview = doc.get('text', '')[:100] + '...' if len(doc.get('text', '')) > 100 else doc.get('text', '')
                
                print(f"   {i}. [{doc_type}] {os.path.basename(source)}")
                print(f"      {text_preview}")
        
    except Exception as e:
        print(f"❌ 미리보기 실패: {str(e)}")


def main():
    parser = argparse.ArgumentParser(
        description="RAG 관리 도구 - 모드팩 인덱싱 및 관리",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python rag_manager.py build "pixelmon_reforged" "9.1.12" "/home/user/pixelmon_reforged"
  python rag_manager.py list
  python rag_manager.py preview "/home/user/pixelmon_reforged"
  python rag_manager.py delete "pixelmon_reforged" "9.1.12"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # build 명령어
    build_parser = subparsers.add_parser('build', help='모드팩 RAG 인덱스 구축')
    build_parser.add_argument('name', help='모드팩 이름')
    build_parser.add_argument('version', help='모드팩 버전')
    build_parser.add_argument('path', help='모드팩 디렉토리 경로')
    
    # list 명령어
    subparsers.add_parser('list', help='등록된 모드팩 목록 표시')
    
    # delete 명령어
    delete_parser = subparsers.add_parser('delete', help='모드팩 RAG 인덱스 삭제')
    delete_parser.add_argument('name', help='모드팩 이름')
    delete_parser.add_argument('version', help='모드팩 버전')
    
    # preview 명령어
    preview_parser = subparsers.add_parser('preview', help='모드팩 구조 미리보기')
    preview_parser.add_argument('path', help='모드팩 디렉토리 경로')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🤖 RAG 관리 도구")
    print("=" * 50)
    
    if args.command == 'build':
        success = build_single_modpack(args.name, args.version, args.path)
        sys.exit(0 if success else 1)
        
    elif args.command == 'list':
        list_modpacks()
        
    elif args.command == 'delete':
        success = delete_modpack(args.name, args.version)
        sys.exit(0 if success else 1)
        
    elif args.command == 'preview':
        preview_modpack(args.path)
    
    print("\n" + "=" * 50)
    print("완료!")


if __name__ == "__main__":
    main()