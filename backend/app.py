from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any
from pathlib import Path

# 새로운 Gemini SDK
from google import genai
from google.genai import types

# 보안 및 모니터링 미들웨어
from middleware.security import SecurityMiddleware, require_valid_input, measure_performance
from middleware.monitoring import MonitoringMiddleware, track_model_usage, track_user_activity
from modpack_parser import scan_modpack
# GCP RAG 시스템
from gcp_rag_system import gcp_rag

# 표준 환경 파일 경로 로드
env_file = Path.home() / "minecraft-ai-backend" / ".env"
load_dotenv(env_file)

# ========= 🔧 개선된 모드팩 타겟팅 시스템 =========

def load_rag_config():
    """RAG 설정 파일 로드"""
    import json
    from pathlib import Path
    
    config_file = Path(__file__).parent / "rag_config.json"
    default_config = {
        "rag_mode": "auto",
        "current_modpack": {
            "name": "",
            "version": "1.0.0"
        },
        "manual_modpack_path": ""
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {**default_config, **config}
        except Exception as e:
            print(f"⚠️ RAG 설정 파일 로드 실패: {e}")
    
    return default_config

def get_target_modpack(request_data):
    """요청에서 타겟 모드팩 결정 (수동 설정 우선, 자동 감지 폴백)"""
    config = load_rag_config()
    
    # 1. 수동 모드: 설정된 모드팩 사용
    if config.get("rag_mode") == "manual":
        manual_name = config.get("current_modpack", {}).get("name", "")
        manual_version = config.get("current_modpack", {}).get("version", "1.0.0")
        
        if manual_name:
            print(f"🔧 수동 모드: {manual_name} v{manual_version}")
            return manual_name, manual_version
        else:
            print("⚠️ 수동 모드이지만 모드팩이 설정되지 않음, 자동 모드로 폴백")
    
    # 2. 자동 모드: 요청에서 추출 또는 환경변수 사용
    request_name = request_data.get('modpack_name', '')
    request_version = request_data.get('modpack_version', '1.0.0')
    
    if request_name and request_name != 'Unknown Modpack':
        print(f"🤖 자동 감지: {request_name} v{request_version}")
        return request_name, request_version
    
    # 3. 환경변수 폴백
    env_name = os.getenv('CURRENT_MODPACK_NAME', '')
    env_version = os.getenv('CURRENT_MODPACK_VERSION', '1.0.0')
    
    if env_name:
        print(f"🌍 환경변수 폴백: {env_name} v{env_version}")
        return env_name, env_version
    
    # 4. 기본값
    print("⚠️ 모드팩 정보 없음, 기본값 사용")
    return "Unknown Modpack", "1.0.0"

app = Flask(__name__)
CORS(app)

# 미들웨어 초기화
security_middleware = SecurityMiddleware(app)
monitoring_middleware = MonitoringMiddleware(app)

# API 키 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GEMINI_WEBSEARCH_ENABLED = os.getenv('GEMINI_WEBSEARCH_ENABLED', 'true').lower() == 'true'
GCP_RAG_ENABLED = os.getenv('GCP_RAG_ENABLED', 'true').lower() == 'true'

# 모델 설정 (환경변수로 설정 가능)
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
OPENAI_MODEL_PRIMARY = os.getenv('OPENAI_MODEL_PRIMARY', 'gpt-4o-mini')
OPENAI_MODEL_FALLBACK = os.getenv('OPENAI_MODEL_FALLBACK', 'gpt-3.5-turbo')
CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
# RAG 프롬프트 첨부 예산(환경변수로 조정 가능)
RAG_TOP_K = int(os.getenv('RAG_TOP_K', '5'))
RAG_SNIPPET_MAX_CHARS = int(os.getenv('RAG_SNIPPET_MAX_CHARS', '500'))
RAG_TOTAL_MAX_CHARS = int(os.getenv('RAG_TOTAL_MAX_CHARS', '1500'))

# AI 모델 초기화 (안전하게)
gemini_client = None
openai_client = None
claude_client = None

# Google AI 초기화 - 2025년 최신 SDK 및 웹검색 지원
if GOOGLE_API_KEY:
    try:
        gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
        print("✅ Gemini 2.5 Pro 클라이언트 초기화 완료 (웹검색 지원, google-genai SDK)")
    except Exception as e:
        print(f"⚠️ Gemini 클라이언트 초기화 실패: {e}")
        gemini_client = None

# OpenAI 초기화 - 2025년 업데이트된 방식, 안전한 처리
if OPENAI_API_KEY and OPENAI_API_KEY != "dummy" and len(OPENAI_API_KEY) > 10:
    try:
        # 새로운 OpenAI 클라이언트 방식
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # API 키 유효성 간단 테스트 (비용 최소화)
        test_response = openai_client.models.list()
        print("✅ OpenAI 클라이언트 초기화 완료 (무료 티어)")
    except Exception as e:
        print(f"⚠️ OpenAI API 키가 유효하지 않거나 초기화 실패: {e}")
        openai_client = None
elif OPENAI_API_KEY:
    print("⚠️ OpenAI API 키가 더미 값이거나 너무 짧아서 비활성화됨")

# Anthropic 초기화 - 안전한 처리 (무료 티어 없음)
if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "dummy" and len(ANTHROPIC_API_KEY) > 10:
    try:
        import anthropic
        claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # API 키 유효성 간단 테스트
        claude_client.models.list()
        print("✅ Claude 클라이언트 초기화 완료 (유료 API)")
    except Exception as e:
        print(f"⚠️ Claude API 키가 유효하지 않거나 초기화 실패: {e}")
        claude_client = None
elif ANTHROPIC_API_KEY:
    print("⚠️ Anthropic API 키가 더미 값이거나 너무 짧아서 비활성화됨")

# 현재 사용 중인 모델 (사용 가능한 첫 번째 모델 선택, Gemini 우선)
current_model = "gemini" if gemini_client else "openai" if openai_client else "claude" if claude_client else None

# ========= 간단 RAG 컴포넌트 (FAISS + SentenceTransformer) =========
rag_enabled = False
rag_index = None
rag_documents: List[Dict[str, Any]] = []
rag_model = None

RAG_DIR = os.path.join(os.path.expanduser('~'), 'minecraft-ai-backend', 'rag')

def init_rag():
    global rag_enabled, rag_index, rag_model
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        rag_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        # 빈 인덱스 초기화 (384차원)
        rag_index = faiss.IndexFlatIP(384)
        rag_enabled = True
        print("✅ RAG 초기화 완료 (FAISS + SentenceTransformer)")
        # 디스크에 저장된 인덱스/문서 자동 로드 시도
        try:
            rag_load_from_disk()
        except Exception as e:
            print(f"RAG 자동 로드 건너뜀: {e}")
    except Exception as e:
        rag_enabled = False
        print(f"⚠️ RAG 초기화 비활성화: {e}")

def build_rag(docs: List[Dict[str, Any]]):
    """문서 리스트를 받아 임베딩 → 인덱스 구축"""
    global rag_index, rag_documents
    if not rag_enabled or rag_model is None:
        return False
    try:
        import numpy as np
        texts = [d.get('text', '') for d in docs]
        emb = rag_model.encode(texts, normalize_embeddings=True)
        # 새 인덱스 생성 후 교체
        import faiss
        index = faiss.IndexFlatIP(emb.shape[1])
        index.add(emb.astype('float32'))
        rag_index = index
        rag_documents = docs
        return True
    except Exception as e:
        print(f"RAG 인덱스 구축 실패: {e}")
        return False

def rag_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    if not rag_enabled or rag_model is None or rag_index is None:
        return []
    try:
        import numpy as np
        q = rag_model.encode([query], normalize_embeddings=True).astype('float32')
        D, I = rag_index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for idx, score in zip(I[0], D[0]):
            if 0 <= idx < len(rag_documents):
                doc = rag_documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)
        return results
    except Exception as e:
        print(f"RAG 검색 실패: {e}")
        return []

def rag_save_to_disk() -> bool:
    """rag_index와 rag_documents를 디스크에 저장"""
    if not rag_enabled or rag_index is None:
        return False
    try:
        os.makedirs(RAG_DIR, exist_ok=True)
        # 문서 저장
        docs_path = os.path.join(RAG_DIR, 'rag_docs.json')
        with open(docs_path, 'w', encoding='utf-8') as f:
            json.dump(rag_documents, f, ensure_ascii=False)
        # 인덱스 저장
        import faiss
        index_path = os.path.join(RAG_DIR, 'rag.index')
        faiss.write_index(rag_index, index_path)
        return True
    except Exception as e:
        print(f"RAG 저장 실패: {e}")
        return False

def rag_load_from_disk() -> bool:
    """rag_index와 rag_documents를 디스크에서 로드"""
    global rag_documents, rag_index
    try:
        docs_path = os.path.join(RAG_DIR, 'rag_docs.json')
        index_path = os.path.join(RAG_DIR, 'rag.index')
        if not (os.path.isfile(docs_path) and os.path.isfile(index_path)):
            return False
        with open(docs_path, 'r', encoding='utf-8') as f:
            rag_documents = json.load(f)
        import faiss
        rag_index = faiss.read_index(index_path)
        return True
    except Exception as e:
        print(f"RAG 로드 실패: {e}")
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "current_model": current_model,
        "available_models": {
            "gemini": gemini_client is not None,
            "openai": openai_client is not None,
            "claude": claude_client is not None
        }
    })

@app.route('/chat', methods=['POST'])
@require_valid_input
@track_user_activity
@measure_performance("Chat API")
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        player_uuid = data.get('player_uuid', '')
        
        # 🔧 개선된 모드팩 타겟팅: 수동 설정 우선, 자동 감지 폴백
        modpack_name, modpack_version = get_target_modpack(data)
        
        print(f"🎯 타겟 모드팩: {modpack_name} v{modpack_version}")
        print(f"📝 질문: {message[:100]}{'...' if len(message) > 100 else ''}")

        # 마인크래프트 모드팩 컨텍스트 + RAG 첨부 (RAG 우선 사용)
        rag_snippets = []
        rag_hits_count = 0
        rag_used_chars = 0
        gcp_rag_results = []
        rag_debug_info = {
            'rag_attempted': True,
            'rag_priority': 'gcp_first',
            'fallback_reason': None
        }
        rag_system_used = "none"
        
        # 1. GCP RAG 시스템 우선 시도 (기본값)
        if GCP_RAG_ENABLED and gcp_rag.is_enabled():
            try:
                print(f"🔍 GCP RAG 검색 시도: '{message[:50]}...' for {modpack_name} v{modpack_version}")
                
                gcp_results = gcp_rag.search_documents(
                    query=message,
                    modpack_name=modpack_name,
                    modpack_version=modpack_version,
                    top_k=RAG_TOP_K,
                    min_score=0.6  # 임계값 낮춤 (더 많은 결과)
                )
                
                if gcp_results:
                    gcp_rag_results = gcp_results
                    rag_system_used = "gcp_rag"
                    
                    for result in gcp_results:
                        if rag_used_chars >= RAG_TOTAL_MAX_CHARS:
                            break
                        
                        src = result.get('doc_source', 'unknown')
                        txt = result.get('text', '').replace('\n', ' ').strip()
                        similarity = result.get('similarity', 0.0)
                        
                        if len(txt) > RAG_SNIPPET_MAX_CHARS:
                            txt = txt[:RAG_SNIPPET_MAX_CHARS] + ' …'
                        
                        remaining = RAG_TOTAL_MAX_CHARS - rag_used_chars
                        if len(txt) > remaining:
                            if remaining < 50:
                                break
                            txt = txt[:remaining] + ' …'
                        
                        rag_snippets.append(f"- [GCP-RAG:{similarity:.2f}] [출처:{src}] {txt}")
                        rag_used_chars += len(txt)
                    
                    rag_hits_count = len(gcp_results)
                    rag_debug_info['gcp_rag'] = {
                        'used': True,
                        'results_count': len(gcp_results),
                        'results': gcp_results[:3],  # 상위 3개만 디버그용으로 저장
                        'total_chars': rag_used_chars
                    }
                    
                    print(f"✅ GCP RAG 성공: {len(gcp_results)}개 문서 검색됨")
                    
                else:
                    # GCP RAG에서 결과 없음
                    rag_debug_info['fallback_reason'] = f"GCP RAG에서 '{modpack_name} v{modpack_version}' 모드팩 데이터 없음 또는 관련성 낮음"
                    rag_debug_info['gcp_rag'] = {
                        'used': True,
                        'results_count': 0,
                        'no_results_reason': 'No matching documents or low similarity scores'
                    }
                    print(f"⚠️ GCP RAG: '{modpack_name} v{modpack_version}' 관련 문서 없음")
                
            except Exception as e:
                error_msg = f"GCP RAG 검색 오류: {str(e)}"
                print(f"❌ {error_msg}")
                rag_debug_info['fallback_reason'] = error_msg
                rag_debug_info['gcp_rag'] = {
                    'used': False, 
                    'error': str(e),
                    'error_type': type(e).__name__
                }
        else:
            # GCP RAG 비활성화됨
            rag_debug_info['fallback_reason'] = "GCP RAG 시스템 비활성화됨"
            rag_debug_info['gcp_rag'] = {
                'used': False,
                'disabled_reason': 'GCP_RAG_ENABLED=false or gcp_rag not initialized'
            }
            print("⚠️ GCP RAG 비활성화 상태")
        
        # 2. GCP RAG 실패/결과 없음 시 로컬 RAG 폴백
        if not rag_snippets and rag_enabled:
            try:
                print("🔄 로컬 RAG 폴백 시도...")
                hits = rag_search(message, top_k=RAG_TOP_K)
                
                if hits:
                    rag_hits_count = len(hits)
                    rag_system_used = "local_rag"
                    
                    for h in hits:
                        if rag_used_chars >= RAG_TOTAL_MAX_CHARS:
                            break
                        src = h.get('source', '') or 'unknown'
                        txt = (h.get('text', '') or '').replace('\n', ' ').strip()
                        score = h.get('score', 0.0)
                        
                        if len(txt) > RAG_SNIPPET_MAX_CHARS:
                            txt = txt[:RAG_SNIPPET_MAX_CHARS] + ' …'
                        remaining = RAG_TOTAL_MAX_CHARS - rag_used_chars
                        if len(txt) > remaining:
                            if remaining < 50:
                                break
                            txt = txt[:remaining] + ' …'
                        rag_snippets.append(f"- [로컬-RAG:{score:.2f}] [출처:{src}] {txt}")
                        rag_used_chars += len(txt)
                    
                    rag_debug_info['local_rag'] = {
                        'used': True,
                        'results_count': len(hits),
                        'fallback_from': 'gcp_rag',
                        'total_chars': rag_used_chars
                    }
                    
                    print(f"✅ 로컬 RAG 폴백 성공: {len(hits)}개 문서 검색됨")
                    
                else:
                    rag_debug_info['local_rag'] = {
                        'used': True,
                        'results_count': 0,
                        'no_results_reason': 'No matching documents in local index'
                    }
                    print("⚠️ 로컬 RAG에서도 관련 문서 없음")
                    
            except Exception as e:
                error_msg = f"로컬 RAG 폴백 오류: {str(e)}"
                print(f"❌ {error_msg}")
                rag_debug_info['local_rag'] = {
                    'used': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
        
        # 3. RAG 결과 없으면 웹검색만 사용한다는 알림
        if not rag_snippets:
            rag_system_used = "web_search_only"
            if not rag_debug_info.get('fallback_reason'):
                rag_debug_info['fallback_reason'] = "모든 RAG 시스템에서 관련 문서를 찾을 수 없음"
            print("⚠️ RAG 시스템 결과 없음 - 웹검색만 사용")
        
        rag_block = "\n".join(rag_snippets) if rag_snippets else "(모드팩 관련 문서를 찾을 수 없어서 웹검색만 사용합니다)"

        context = f"""
당신은 마인크래프트 모드팩 전문가 AI 어시스턴트입니다.
현재 모드팩: {modpack_name} v{modpack_version}

아래는 관련 문서 검색 결과 일부입니다(필요 시만 참고):
{rag_block}

사용자의 질문에 대해 친절하고 정확하게 답변해주세요.
제작법, 아이템 정보, 모드 설명 등을 포함할 수 있습니다.
"""

        # 선택된 모델로 응답 생성
        if current_model == "gemini" and gemini_client:
            try:
                # 웹검색 도구 설정
                config = None
                if GEMINI_WEBSEARCH_ENABLED:
                    grounding_tool = types.Tool(google_search=types.GoogleSearch())
                    config = types.GenerateContentConfig(tools=[grounding_tool])
                
                full_message = context + "\n\n사용자: " + message + "\n\n최신 정보가 필요하다면 웹 검색을 활용해서 정확한 답변을 제공해주세요."
                
                # 웹검색 지원 모델로 응답 생성
                with track_model_usage("gemini-2.5-pro-web"):
                    if config is not None:
                        response = gemini_client.models.generate_content(
                            model=GEMINI_MODEL,
                            contents=full_message,
                            config=config
                        )
                    else:
                        response = gemini_client.models.generate_content(
                            model=GEMINI_MODEL,
                            contents=full_message
                        )
                    ai_response = response.text
            except Exception as e:
                print(f"Gemini 웹검색 모드 실패, 기본 모드로 폴백: {e}")
                # 웹검색 실패시 기본 모드로 폴백
                try:
                    full_message = context + "\n\n사용자: " + message + "\n\nAI:"
                    response = gemini_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=full_message
                    )
                    ai_response = response.text
                except Exception as e2:
                    ai_response = f"Gemini API 오류가 발생했습니다: {str(e2)}"

        elif current_model == "openai" and openai_client:
            try:
                # 2025년 최신 OpenAI API 방식
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL_PRIMARY,  # 환경변수로 설정 가능
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI GPT-4o-mini 실패, GPT-3.5-turbo로 폴백: {e}")
                # 폴백 시도
                try:
                    response = openai_client.chat.completions.create(
                        model=OPENAI_MODEL_FALLBACK,
                        messages=[
                            {"role": "system", "content": context},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=1000,
                        temperature=0.7
                    )
                    ai_response = response.choices[0].message.content
                except Exception as e2:
                    ai_response = "OpenAI API 오류가 발생했습니다. 할당량이나 API 키를 확인해주세요."

        elif current_model == "claude" and claude_client:
            try:
                response = claude_client.messages.create(
                    model=CLAUDE_MODEL,  # 환경변수로 설정 가능
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": context + "\n\n" + message}
                    ]
                )
                ai_response = response.content[0].text
            except Exception as e:
                if "credit" in str(e).lower() or "billing" in str(e).lower():
                    ai_response = "Claude API는 유료 서비스입니다. 크레딧을 충전해주세요."
                else:
                    ai_response = "Claude API 오류가 발생했습니다. API 키를 확인해주세요."

        else:
            ai_response = "현재 사용 가능한 AI 모델이 없습니다. Gemini API 키를 설정해주세요."

        return jsonify({
            "success": True,
            "response": ai_response,
            "model": current_model,
            "timestamp": datetime.now().isoformat(),
            "rag": {
                "enabled": rag_enabled,
                "gcp_enabled": GCP_RAG_ENABLED and gcp_rag.is_enabled(),
                "system_used": rag_system_used,  # 실제 사용된 RAG 시스템
                "hits": rag_hits_count,
                "used": rag_hits_count > 0,
                "success": rag_hits_count > 0,  # RAG 성공 여부
                "fallback_reason": rag_debug_info.get('fallback_reason'),  # 폴백 이유
                "top_k": RAG_TOP_K,
                "snippet_max_chars": RAG_SNIPPET_MAX_CHARS,
                "total_max_chars": RAG_TOTAL_MAX_CHARS,
                "used_chars": rag_used_chars,
                "debug_info": rag_debug_info,
                "user_message": rag_debug_info.get('fallback_reason') if rag_hits_count == 0 else None
            },
            "websearch_enabled": GEMINI_WEBSEARCH_ENABLED
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/models', methods=['GET'])
def get_models():
    models = []
    
    if gemini_client:
        models.append({
            "id": "gemini",
            "name": "Gemini 2.5 Pro (웹검색 지원)",
            "provider": "Google",
            "available": True,
            "current": current_model == "gemini"
        })
    
    if openai_client:
        models.append({
            "id": "openai",
            "name": "GPT-4o Mini / GPT-3.5 Turbo",
            "provider": "OpenAI",
            "available": True,
            "current": current_model == "openai"
        })
    
    if claude_client:
        models.append({
            "id": "claude",
            "name": "Claude 3.5 Sonnet",
            "provider": "Anthropic",
            "available": True,
            "current": current_model == "claude"
        })
    
    return jsonify({"models": models})

# ---------------- RAG 관리 엔드포인트 ----------------
@app.route('/rag/build', methods=['POST'])
def rag_build():
    """간단한 RAG 인덱스 구축 API
    - 입력 형식 1: {"docs": [{"text": "...", "source": "..."}, ...]}
    - 입력 형식 2: {"modpack_name": "...", "modpack_version": "...", "docs": [...]} (메타 포함)
    """
    try:
        data = request.get_json(force=True) or {}
        docs = data.get('docs', [])
        if not isinstance(docs, list) or not docs:
            return jsonify({"success": False, "error": "docs 리스트가 필요합니다"}), 400
        # 최소 필드 보정
        normalized = []
        for d in docs:
            if isinstance(d, dict) and d.get('text'):
                normalized.append({
                    'text': d.get('text', ''),
                    'source': d.get('source', 'manual')
                })
        if not normalized:
            return jsonify({"success": False, "error": "유효한 문서가 없습니다"}), 400
        ok = build_rag(normalized)
        return jsonify({"success": ok, "count": len(normalized)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/rag/status', methods=['GET'])
def rag_status():
    return jsonify({
        "enabled": rag_enabled,
        "documents": len(rag_documents),
        "model": bool(rag_model)
    })

@app.route('/rag/save', methods=['POST'])
def rag_save():
    ok = rag_save_to_disk()
    return jsonify({"success": ok})

@app.route('/rag/load', methods=['POST'])
def rag_load():
    ok = rag_load_from_disk()
    return jsonify({"success": ok})

@app.route('/models/switch', methods=['POST'])
def switch_model():
    global current_model
    try:
        data = request.json
        model_id = data.get('model_id', 'gemini')

        # 사용 가능한 모델인지 확인
        available_models = []
        if gemini_client:
            available_models.append('gemini')
        if openai_client:
            available_models.append('openai')
        if claude_client:
            available_models.append('claude')

        if model_id in available_models:
            current_model = model_id
            return jsonify({
                "success": True,
                "message": f"모델이 {model_id}로 변경되었습니다."
            })
        else:
            return jsonify({
                "success": False,
                "error": "지원하지 않는 모델이거나 API 키가 유효하지 않습니다."
            }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/modpack/switch', methods=['POST'])
def api_modpack_switch():
    """간소화된 모드팩 분석 엔드포인트.
    현재는 실제 분석 대신 입력값을 검증하고 기본 메트릭을 반환합니다.
    modpack_switch.sh가 기대하는 필드를 포함해 성공적으로 동작하도록 맞춥니다.
    """
    try:
        data = request.get_json(force=True) or {}
        modpack_path = data.get('modpack_path', '')
        modpack_name = data.get('modpack_name', 'unknown')
        modpack_version = data.get('modpack_version', '1.0')

        # 간단한 유효성 검사
        if not modpack_name:
            return jsonify({"success": False, "error": "modpack_name is required"}), 400

        # 간단 스캔 + RAG 자동 구축
        stats = {}
        built = False
        if modpack_path and os.path.isdir(modpack_path):
            scan = scan_modpack(modpack_path)
            docs = scan.get('docs', [])
            stats = scan.get('stats', {})
            if docs:
                built = build_rag(docs)

        # 반환 포맷은 스크립트가 파싱하는 키와 일치해야 함
        result = {
            "success": True,
            "modpack": {
                "name": modpack_name,
                "version": modpack_version,
                "path": modpack_path,
            },
            "mods_count": stats.get('mods', 0),
            "recipes_count": stats.get('recipes', 0),
            "items_count": stats.get('kubejs', 0),
            "rag_built": built,
            "language_mappings_added": 0,
            "timestamp": datetime.now().isoformat()
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/recipe/<item_name>', methods=['GET'])
def get_recipe(item_name):
    try:
        # 현재 활성 모델을 사용해서 레시피 검색
        if current_model == "gemini" and gemini_client:
            try:
                # 웹검색 도구 설정으로 최신 레시피 정보 검색
                grounding_tool = types.Tool(google_search=types.GoogleSearch())
                config = types.GenerateContentConfig(tools=[grounding_tool])
                
                query = f"마인크래프트에서 {item_name}의 제작법을 알려주세요. 재료와 제작 방법을 포함해서 답변해주세요. 최신 정보를 검색해서 정확한 답변을 제공해주세요."
                
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=query,
                    config=config
                )
                recipe_text = response.text
            except Exception as e:
                print(f"Gemini 웹검색 레시피 검색 실패, 기본 모드로 폴백: {e}")
                # 폴백: 검색 없이 레시피 생성
                try:
                    query = f"마인크래프트에서 {item_name}의 제작법을 알려주세요. 재료와 제작 방법을 포함해서 답변해주세요."
                    response = gemini_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=query
                    )
                    recipe_text = response.text
                except:
                    recipe_text = f"{item_name}의 제작법을 찾을 수 없습니다. 게임 내 제작법 책을 확인해보세요."
        
        elif current_model == "openai" and openai_client:
            try:
                query = f"마인크래프트에서 {item_name}의 제작법을 알려주세요. 재료와 제작 방법을 포함해서 답변해주세요."
                response = openai_client.chat.completions.create(
                    model=OPENAI_MODEL_PRIMARY,
                    messages=[{"role": "user", "content": query}],
                    max_tokens=500,
                    temperature=0.7
                )
                recipe_text = response.choices[0].message.content
            except:
                recipe_text = f"{item_name}의 제작법을 찾을 수 없습니다. 게임 내 제작법 책을 확인해보세요."
        
        elif current_model == "claude" and claude_client:
            try:
                query = f"마인크래프트에서 {item_name}의 제작법을 알려주세요. 재료와 제작 방법을 포함해서 답변해주세요."
                response = claude_client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=500,
                    messages=[{"role": "user", "content": query}]
                )
                recipe_text = response.content[0].text
            except:
                recipe_text = f"{item_name}의 제작법을 찾을 수 없습니다. 게임 내 제작법 책을 확인해보세요."
        else:
            recipe_text = f"{item_name}의 제작법을 찾을 수 없습니다. 게임 내 제작법 책을 확인해보세요."

        # 3x3 레시피 구조(있으면 AI 응답 파싱, 기본은 텍스트만)
        recipe_info = {
            "item": item_name,
            "recipe": recipe_text,
            "grid": [[None, None, None], [None, None, None], [None, None, None]],
            "materials": [],
            "crafting_type": "crafting_table"
        }

        return jsonify({
            "success": True,
            "recipe": recipe_info
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# =============== GCP RAG 관리 엔드포인트 ===============

@app.route('/gcp-rag/build', methods=['POST'])
def gcp_rag_build():
    """GCP RAG 인덱스 구축"""
    try:
        data = request.get_json(force=True) or {}
        modpack_name = data.get('modpack_name', '').strip()
        modpack_version = data.get('modpack_version', '1.0.0').strip()
        modpack_path = data.get('modpack_path', '').strip()
        
        if not all([modpack_name, modpack_version, modpack_path]):
            return jsonify({
                "success": False, 
                "error": "modpack_name, modpack_version, modpack_path 모두 필요"
            }), 400
        
        if not gcp_rag.is_enabled():
            return jsonify({
                "success": False,
                "error": "GCP RAG 시스템이 비활성화되어 있습니다. GCP_PROJECT_ID 환경변수와 인증 설정을 확인하세요."
            }), 503
        
        # 비동기적으로 인덱스 구축 (실제 환경에서는 Celery 등 사용 권장)
        result = gcp_rag.build_modpack_index(modpack_name, modpack_version, modpack_path)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/gcp-rag/search', methods=['POST'])
def gcp_rag_search():
    """GCP RAG 검색 (디버그용 - 실제 검색 결과 확인)"""
    try:
        data = request.get_json(force=True) or {}
        query = data.get('query', '').strip()
        modpack_name = data.get('modpack_name', '').strip()
        modpack_version = data.get('modpack_version', '1.0.0').strip()
        top_k = min(data.get('top_k', 5), 20)  # 최대 20개
        min_score = max(0.0, min(1.0, data.get('min_score', 0.7)))
        
        if not all([query, modpack_name, modpack_version]):
            return jsonify({
                "success": False,
                "error": "query, modpack_name, modpack_version 모두 필요"
            }), 400
        
        if not gcp_rag.is_enabled():
            return jsonify({
                "success": False,
                "error": "GCP RAG 시스템이 비활성화되어 있습니다."
            }), 503
        
        results = gcp_rag.search_documents(
            query=query,
            modpack_name=modpack_name,
            modpack_version=modpack_version,
            top_k=top_k,
            min_score=min_score
        )
        
        return jsonify({
            "success": True,
            "query": query,
            "modpack": f"{modpack_name} v{modpack_version}",
            "results_count": len(results),
            "results": results,
            "search_params": {
                "top_k": top_k,
                "min_score": min_score
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/gcp-rag/modpacks', methods=['GET'])
def gcp_rag_modpacks():
    """등록된 모드팩 목록"""
    try:
        if not gcp_rag.is_enabled():
            return jsonify({
                "success": False,
                "error": "GCP RAG 시스템이 비활성화되어 있습니다."
            }), 503
        
        modpacks = gcp_rag.get_modpack_list()
        return jsonify({
            "success": True,
            "modpacks": modpacks,
            "count": len(modpacks)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/gcp-rag/delete', methods=['DELETE'])
def gcp_rag_delete():
    """GCP RAG 인덱스 삭제"""
    try:
        data = request.get_json(force=True) or {}
        modpack_name = data.get('modpack_name', '').strip()
        modpack_version = data.get('modpack_version', '1.0.0').strip()
        
        if not all([modpack_name, modpack_version]):
            return jsonify({
                "success": False,
                "error": "modpack_name, modpack_version 모두 필요"
            }), 400
        
        if not gcp_rag.is_enabled():
            return jsonify({
                "success": False,
                "error": "GCP RAG 시스템이 비활성화되어 있습니다."
            }), 503
        
        success = gcp_rag.delete_modpack_index(modpack_name, modpack_version)
        return jsonify({
            "success": success,
            "message": f"{modpack_name} v{modpack_version} 인덱스 삭제 {'완료' if success else '실패'}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/gcp-rag/status', methods=['GET'])
def gcp_rag_status():
    """GCP RAG 시스템 상태"""
    try:
        return jsonify({
            "success": True,
            "gcp_rag_enabled": GCP_RAG_ENABLED,
            "gcp_rag_available": gcp_rag.is_enabled(),
            "project_id": gcp_rag.project_id if gcp_rag.is_enabled() else None,
            "location": gcp_rag.location if gcp_rag.is_enabled() else None,
            "local_rag_enabled": rag_enabled
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 마인크래프트 AI 백엔드 시작 중...")
    print(f"📊 현재 활성 모델: {current_model if current_model else '없음'}")
    print(f"🔑 Google API (Gemini): {'✅' if gemini_client else '❌'}")
    print(f"🔑 OpenAI API: {'✅' if openai_client else '❌'}")  
    print(f"🔑 Anthropic API (Claude): {'✅' if claude_client else '❌'}")
    print(f"🔗 GCP RAG: {'✅' if GCP_RAG_ENABLED and gcp_rag.is_enabled() else '❌'}")
    
    if current_model:
        print(f"🎯 주 사용 모델: {current_model}")
        if current_model == "gemini":
            print("🌐 Gemini 웹검색 기능 활성화됨")
    else:
        print("⚠️ 경고: 사용 가능한 AI 모델이 없습니다!")
        print("💡 최소한 Google API 키(Gemini)를 설정하는 것을 권장합니다.")
    
    if GCP_RAG_ENABLED and gcp_rag.is_enabled():
        print("🎯 GCP RAG 활성화됨 - 모드팩별 벡터 검색 가능")
        modpack_count = len(gcp_rag.get_modpack_list())
        print(f"📦 등록된 모드팩: {modpack_count}개")
    elif GCP_RAG_ENABLED:
        print("⚠️ GCP RAG 설정 불완전 - GCP_PROJECT_ID와 인증 확인 필요")
    else:
        print("📝 GCP RAG 비활성화 - 로컬 RAG만 사용")
    
    print("=" * 60)
    init_rag()
    app.run(host='0.0.0.0', port=5000, debug=False)