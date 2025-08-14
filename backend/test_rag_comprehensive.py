#!/usr/bin/env python3
"""
종합 RAG 테스트 도구 - 모드팩 파싱 및 검색 품질 확인
특히 Enigmatica 10, Prominence 2 같은 대형 모드팩에 특화된 테스트
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter

# 현재 디렉토리에서 모듈 import
sys.path.insert(0, str(Path(__file__).parent))
from modpack_parser import scan_modpack

# 백엔드 URL
BASE_URL = "http://localhost:5000"

class RAGTester:
    """종합 RAG 테스트 클래스"""
    
    def __init__(self):
        self.results = {}
        
    def test_modpack_structure_analysis(self, modpack_path: str, modpack_name: str) -> Dict[str, Any]:
        """모드팩 구조 심층 분석"""
        print(f"\n🔍 모드팩 구조 분석: {modpack_name}")
        print(f"📁 경로: {modpack_path}")
        
        if not os.path.exists(modpack_path):
            print(f"❌ 경로가 존재하지 않습니다: {modpack_path}")
            return {}
        
        # 1. 기본 구조 확인
        expected_dirs = ['mods', 'data', 'kubejs', 'config', 'scripts']
        found_dirs = []
        
        for dir_name in expected_dirs:
            dir_path = os.path.join(modpack_path, dir_name)
            if os.path.exists(dir_path):
                found_dirs.append(dir_name)
                
        print(f"📂 발견된 디렉토리: {', '.join(found_dirs)}")
        
        # 2. 모드팩 파서 테스트
        print(f"\n🔬 모드팩 파싱 테스트...")
        scan_result = scan_modpack(modpack_path)
        stats = scan_result.get('stats', {})
        docs = scan_result.get('docs', [])
        
        print(f"📊 파싱 결과:")
        print(f"   - 총 문서: {len(docs)}개")
        print(f"   - 모드: {stats.get('mods', 0)}개")
        print(f"   - 레시피: {stats.get('recipes', 0)}개")
        print(f"   - KubeJS: {stats.get('kubejs', 0)}개")
        
        # 3. 문서 타입별 분석
        doc_types = Counter([doc.get('type', 'unknown') for doc in docs])
        print(f"\n📄 문서 타입 분포:")
        for doc_type, count in doc_types.items():
            print(f"   - {doc_type}: {count}개")
        
        # 4. 대형 모드팩 특화 검증
        analysis = self._analyze_large_modpack_features(modpack_path, docs)
        
        return {
            'path': modpack_path,
            'found_dirs': found_dirs,
            'stats': stats,
            'doc_count': len(docs),
            'doc_types': dict(doc_types),
            'analysis': analysis,
            'scan_result': scan_result
        }
    
    def _analyze_large_modpack_features(self, modpack_path: str, docs: List[Dict]) -> Dict[str, Any]:
        """대형 모드팩 특화 기능 분석"""
        analysis = {
            'thermal_expansion': False,
            'applied_energistics': False,
            'create': False,
            'mekanism': False,
            'tinkers_construct': False,
            'custom_recipes': 0,
            'complex_automation': False,
            'quest_integration': False
        }
        
        # 모드 검색
        mod_texts = [doc.get('text', '').lower() for doc in docs if doc.get('type') == 'mod']
        all_text = ' '.join(mod_texts)
        
        # 주요 모드 감지
        if 'thermal' in all_text:
            analysis['thermal_expansion'] = True
        if 'applied' in all_text and 'energistic' in all_text:
            analysis['applied_energistics'] = True
        if 'create' in all_text:
            analysis['create'] = True
        if 'mekanism' in all_text:
            analysis['mekanism'] = True
        if 'tinker' in all_text:
            analysis['tinkers_construct'] = True
        
        # 커스텀 레시피 수 계산
        recipe_docs = [doc for doc in docs if doc.get('type') == 'recipe']
        analysis['custom_recipes'] = len(recipe_docs)
        
        # KubeJS 스크립트 분석
        kubejs_docs = [doc for doc in docs if doc.get('type') == 'kubejs']
        kubejs_content = ' '.join([doc.get('text', '').lower() for doc in kubejs_docs])
        
        if any(keyword in kubejs_content for keyword in ['automation', 'machine', 'recipe']):
            analysis['complex_automation'] = True
        
        # 퀘스트 시스템 확인
        quest_files = ['ftbquests', 'questbook', 'quests']
        for quest_dir in quest_files:
            if os.path.exists(os.path.join(modpack_path, quest_dir)):
                analysis['quest_integration'] = True
                break
        
        return analysis
    
    def test_search_quality(self, modpack_name: str, modpack_version: str) -> Dict[str, Any]:
        """검색 품질 테스트"""
        print(f"\n🎯 검색 품질 테스트: {modpack_name} v{modpack_version}")
        
        # Enigmatica 10 특화 테스트 쿼리
        enigmatica_queries = [
            "thermal expansion machine",
            "create contraption",
            "mekanism reactor",
            "applied energistics storage",
            "diamond gear recipe",
            "automation setup",
            "power generation",
            "ore processing"
        ]
        
        # Prominence 2 특화 테스트 쿼리
        prominence_queries = [
            "tinkers construct",
            "blood magic",
            "botania flower",
            "thaumcraft research",
            "combat equipment",
            "magic progression",
            "ritual setup",
            "enchantment system"
        ]
        
        # 기본 쿼리
        basic_queries = [
            "iron ingot",
            "crafting recipe",
            "furnace",
            "chest recipe"
        ]
        
        # 모드팩별 쿼리 선택
        if 'enigmatica' in modpack_name.lower():
            test_queries = enigmatica_queries + basic_queries
        elif 'prominence' in modpack_name.lower():
            test_queries = prominence_queries + basic_queries
        else:
            test_queries = basic_queries
        
        search_results = {}
        total_score = 0
        
        for query in test_queries:
            print(f"   🔍 테스트: '{query}'")
            
            try:
                payload = {
                    "query": query,
                    "modpack_name": modpack_name,
                    "modpack_version": modpack_version,
                    "top_k": 5,
                    "min_score": 0.6
                }
                
                response = requests.post(f"{BASE_URL}/gcp-rag/search", json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    # 검색 품질 점수 계산
                    quality_score = self._calculate_search_quality(query, results)
                    total_score += quality_score
                    
                    search_results[query] = {
                        'result_count': len(results),
                        'quality_score': quality_score,
                        'top_similarity': results[0].get('similarity', 0) if results else 0,
                        'results': results[:2]  # 상위 2개 결과만 저장
                    }
                    
                    status = "✅" if quality_score > 0.7 else "⚠️" if quality_score > 0.4 else "❌"
                    print(f"      {status} {len(results)}개 결과, 품질: {quality_score:.2f}")
                    
                else:
                    print(f"      ❌ 검색 실패: {response.status_code}")
                    search_results[query] = {'error': f"HTTP {response.status_code}"}
                    
            except Exception as e:
                print(f"      ❌ 오류: {str(e)}")
                search_results[query] = {'error': str(e)}
                
            time.sleep(0.5)  # API 요청 간격
        
        average_score = total_score / len(test_queries) if test_queries else 0
        print(f"\n📊 전체 검색 품질: {average_score:.2f}/1.0")
        
        return {
            'modpack': f"{modpack_name} v{modpack_version}",
            'queries_tested': len(test_queries),
            'average_quality': average_score,
            'detailed_results': search_results
        }
    
    def _calculate_search_quality(self, query: str, results: List[Dict]) -> float:
        """검색 결과 품질 점수 계산"""
        if not results:
            return 0.0
        
        # 기본 점수: 결과 개수
        base_score = min(len(results) / 5.0, 1.0) * 0.3
        
        # 유사도 점수
        similarity_scores = [r.get('similarity', 0) for r in results]
        avg_similarity = sum(similarity_scores) / len(similarity_scores)
        similarity_score = avg_similarity * 0.4
        
        # 관련성 점수 (키워드 매칭)
        query_words = set(query.lower().split())
        relevance_scores = []
        
        for result in results[:3]:  # 상위 3개만 평가
            text = result.get('text', '').lower()
            doc_type = result.get('doc_type', '')
            
            # 키워드 매칭
            matched_words = len(query_words.intersection(set(text.split())))
            word_score = matched_words / len(query_words)
            
            # 문서 타입 보너스
            type_bonus = 0.1 if doc_type in ['recipe', 'mod'] else 0
            
            relevance_scores.append(word_score + type_bonus)
        
        relevance_score = (sum(relevance_scores) / len(relevance_scores)) * 0.3 if relevance_scores else 0
        
        return base_score + similarity_score + relevance_score
    
    def test_end_to_end_chat(self, modpack_name: str, modpack_version: str) -> Dict[str, Any]:
        """종단간 채팅 테스트"""
        print(f"\n💬 종단간 채팅 테스트: {modpack_name}")
        
        chat_tests = [
            "철 블록을 만드는 방법을 자세히 알려줘",
            "이 모드팩에서 가장 효율적인 전력 생산 방법은?",
            "automation 시스템을 구축하려면 어떤 모드를 사용해야 해?",
            "레드스톤과 기계를 연동하는 방법을 설명해줘"
        ]
        
        chat_results = {}
        
        for message in chat_tests:
            print(f"   💭 테스트: '{message[:40]}...'")
            
            try:
                payload = {
                    "message": message,
                    "player_uuid": "test-comprehensive",
                    "modpack_name": modpack_name,
                    "modpack_version": modpack_version
                }
                
                response = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        rag_info = data.get('rag', {})
                        
                        chat_results[message] = {
                            'success': True,
                            'model': data.get('model'),
                            'rag_used': rag_info.get('used', False),
                            'rag_hits': rag_info.get('hits', 0),
                            'rag_system': rag_info.get('system_used', 'none'),
                            'response_length': len(data.get('response', '')),
                            'rag_chars_used': rag_info.get('used_chars', 0)
                        }
                        
                        status = "✅" if rag_info.get('hits', 0) > 0 else "⚠️"
                        print(f"      {status} RAG: {rag_info.get('hits', 0)}개 히트, 모델: {data.get('model')}")
                        
                    else:
                        print(f"      ❌ 채팅 실패: {data.get('error')}")
                        chat_results[message] = {'success': False, 'error': data.get('error')}
                
                else:
                    print(f"      ❌ 요청 실패: {response.status_code}")
                    chat_results[message] = {'success': False, 'error': f"HTTP {response.status_code}"}
                    
            except Exception as e:
                print(f"      ❌ 오류: {str(e)}")
                chat_results[message] = {'success': False, 'error': str(e)}
                
            time.sleep(1)  # AI 요청 간격
        
        successful_chats = sum(1 for r in chat_results.values() if r.get('success'))
        rag_usage_rate = sum(1 for r in chat_results.values() if r.get('rag_used')) / len(chat_tests)
        
        return {
            'total_tests': len(chat_tests),
            'successful_chats': successful_chats,
            'success_rate': successful_chats / len(chat_tests),
            'rag_usage_rate': rag_usage_rate,
            'detailed_results': chat_results
        }
    
    def generate_comprehensive_report(self, modpack_results: Dict[str, Any]) -> str:
        """종합 테스트 보고서 생성"""
        report = []
        report.append("=" * 80)
        report.append("🔍 RAG 시스템 종합 테스트 보고서")
        report.append("=" * 80)
        
        for modpack_name, results in modpack_results.items():
            report.append(f"\n📦 모드팩: {modpack_name}")
            report.append("-" * 40)
            
            # 구조 분석
            if 'structure' in results:
                struct = results['structure']
                report.append(f"📊 파싱 통계:")
                report.append(f"   - 총 문서: {struct.get('doc_count', 0)}개")
                report.append(f"   - 모드: {struct.get('stats', {}).get('mods', 0)}개")
                report.append(f"   - 레시피: {struct.get('stats', {}).get('recipes', 0)}개")
                report.append(f"   - KubeJS: {struct.get('stats', {}).get('kubejs', 0)}개")
                
                analysis = struct.get('analysis', {})
                report.append(f"\n🎯 주요 기능:")
                for feature, detected in analysis.items():
                    if isinstance(detected, bool):
                        status = "✅" if detected else "❌"
                        report.append(f"   {status} {feature.replace('_', ' ').title()}")
            
            # 검색 품질
            if 'search_quality' in results:
                search = results['search_quality']
                quality_score = search.get('average_quality', 0)
                grade = "우수" if quality_score > 0.8 else "양호" if quality_score > 0.6 else "개선필요"
                
                report.append(f"\n🎯 검색 품질: {quality_score:.2f}/1.0 ({grade})")
                report.append(f"   - 테스트 쿼리: {search.get('queries_tested', 0)}개")
            
            # 채팅 테스트
            if 'chat_test' in results:
                chat = results['chat_test']
                success_rate = chat.get('success_rate', 0)
                rag_rate = chat.get('rag_usage_rate', 0)
                
                report.append(f"\n💬 채팅 테스트:")
                report.append(f"   - 성공률: {success_rate:.1%}")
                report.append(f"   - RAG 활용률: {rag_rate:.1%}")
        
        report.append(f"\n" + "=" * 80)
        report.append(f"보고서 생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)


def main():
    """메인 테스트 실행"""
    print("🚀 종합 RAG 테스트 시작")
    print("=" * 80)
    
    tester = RAGTester()
    
    # 테스트할 모드팩 입력 (실제 GCP VM 구조에 맞게 수정 필요)
    test_modpacks = []
    
    print("📝 테스트할 모드팩 정보를 입력하세요:")
    
    while True:
        modpack_name = input("\n모드팩 이름 (완료시 엔터): ").strip()
        if not modpack_name:
            break
            
        modpack_version = input("모드팩 버전 (기본: 1.0.0): ").strip() or "1.0.0"
        modpack_path = input("모드팩 경로: ").strip()
        
        if modpack_path and os.path.exists(modpack_path):
            test_modpacks.append({
                'name': modpack_name,
                'version': modpack_version,
                'path': modpack_path
            })
            print(f"✅ 추가됨: {modpack_name} v{modpack_version}")
        else:
            print(f"❌ 경로가 존재하지 않습니다: {modpack_path}")
    
    if not test_modpacks:
        print("❌ 테스트할 모드팩이 없습니다.")
        return
    
    # 종합 테스트 실행
    all_results = {}
    
    for modpack in test_modpacks:
        name = modpack['name']
        version = modpack['version']
        path = modpack['path']
        
        print(f"\n🎯 모드팩 테스트 시작: {name}")
        
        results = {}
        
        # 1. 구조 분석
        results['structure'] = tester.test_modpack_structure_analysis(path, name)
        
        # 2. 검색 품질 테스트
        results['search_quality'] = tester.test_search_quality(name, version)
        
        # 3. 채팅 테스트
        results['chat_test'] = tester.test_end_to_end_chat(name, version)
        
        all_results[name] = results
    
    # 보고서 생성
    report = tester.generate_comprehensive_report(all_results)
    print(f"\n{report}")
    
    # 보고서 파일 저장
    report_file = f"rag_test_report_{int(time.time())}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 상세 보고서 저장됨: {report_file}")
    print("🎉 종합 테스트 완료!")


if __name__ == "__main__":
    main()