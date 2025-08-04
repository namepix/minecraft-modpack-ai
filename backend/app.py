from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import re
from functools import wraps
import time
from collections import defaultdict

from models.hybrid_ai_model import HybridAIModel
from database.chat_manager import ChatManager
from database.recipe_manager import RecipeManager
from modpack_parser.modpack_analyzer import ModpackAnalyzer
from utils.language_mapper import LanguageMapper
from utils.rag_manager import RAGManager

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting을 위한 전역 변수
request_counts = defaultdict(list)
RATE_LIMIT = 10  # 1분당 10회 요청
RATE_WINDOW = 60  # 60초

def rate_limit(f):
    """Rate limiting 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 클라이언트 IP 또는 UUID로 식별
        client_id = request.headers.get('X-Client-ID') or request.remote_addr
        
        now = time.time()
        # 오래된 요청 기록 제거
        request_counts[client_id] = [req_time for req_time in request_counts[client_id] 
                                   if now - req_time < RATE_WINDOW]
        
        # 요청 횟수 확인
        if len(request_counts[client_id]) >= RATE_LIMIT:
            return jsonify({'error': '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.'}), 429
        
        # 현재 요청 기록
        request_counts[client_id].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

# 전역 객체들
ai_model = None
chat_manager = None
recipe_manager = None
modpack_analyzer = None
language_mapper = None
rag_manager = None

def initialize_services():
    """서비스들을 초기화합니다."""
    global ai_model, chat_manager, recipe_manager, modpack_analyzer, language_mapper, rag_manager
    
    try:
        # 데이터베이스 매니저들 초기화
        chat_manager = ChatManager()
        recipe_manager = RecipeManager()
        
        # 언어 매퍼 초기화
        language_mapper = LanguageMapper()
        
        # RAG 매니저 초기화 (필수)
        gcp_project_id = os.getenv('GCP_PROJECT_ID')
        gcs_bucket_name = os.getenv('GCS_BUCKET_NAME')
        
        if not gcp_project_id or not gcs_bucket_name:
            logger.error("❌ RAG 필수 설정 누락!")
            logger.error("GCP_PROJECT_ID와 GCS_BUCKET_NAME이 필요합니다.")
            logger.error("env.example을 참고하여 .env 파일을 설정하세요.")
            raise ValueError("RAG 필수 설정이 누락되었습니다.")
        
        try:
            rag_manager = RAGManager(gcp_project_id, gcs_bucket_name)
            logger.info("✅ RAG 매니저 초기화 완료")
        except Exception as e:
            logger.error(f"❌ RAG 매니저 초기화 실패: {e}")
            logger.error("GCP 프로젝트 ID와 버킷 이름을 확인하세요.")
            raise
        
        # AI 모델 초기화 (recipe_manager, language_mapper, rag_manager 전달)
        ai_model = HybridAIModel(recipe_manager=recipe_manager, language_mapper=language_mapper, rag_manager=rag_manager)
        
        # 모드팩 분석기 초기화
        modpack_analyzer = ModpackAnalyzer()
        
        logger.info("✅ 모든 서비스가 성공적으로 초기화되었습니다.")
        
    except Exception as e:
        logger.error(f"❌ 서비스 초기화 중 오류 발생: {e}")
        
        # 필수 서비스 확인
        if not chat_manager:
            logger.error("❌ ChatManager 초기화 실패 - 시스템 시작 불가")
        if not recipe_manager:
            logger.error("❌ RecipeManager 초기화 실패 - 시스템 시작 불가")
        if not language_mapper:
            logger.error("❌ LanguageMapper 초기화 실패 - 시스템 시작 불가")
        if not rag_manager:
            logger.error("❌ RAGManager 초기화 실패 - 시스템 시작 불가")
        if not ai_model:
            logger.error("❌ AIModel 초기화 실패 - 시스템 시작 불가")
        if not modpack_analyzer:
            logger.error("❌ ModpackAnalyzer 초기화 실패 - 시스템 시작 불가")
        
        # 필수 서비스 중 하나라도 실패하면 시스템 중단
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ai_model': ai_model is not None,
            'chat_manager': chat_manager is not None,
            'recipe_manager': recipe_manager is not None,
            'modpack_analyzer': modpack_analyzer is not None,
            'language_mapper': language_mapper is not None,
            'rag_manager': rag_manager is not None
        }
    })

@app.route('/api/chat', methods=['POST'])
@rate_limit
def chat():
    """AI와의 채팅 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다.'}), 400
        
        player_uuid = data.get('player_uuid')
        message = data.get('message')
        modpack_name = data.get('modpack_name', 'unknown')
        modpack_version = data.get('modpack_version', '1.0')
        
        # 입력 검증
        if not player_uuid or not message:
            return jsonify({'error': 'player_uuid와 message는 필수입니다.'}), 400
        
        # UUID 형식 검증
        if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', player_uuid):
            return jsonify({'error': '올바른 UUID 형식이 아닙니다.'}), 400
        
        # 메시지 길이 제한
        if len(message) > 1000:
            return jsonify({'error': '메시지는 1000자를 초과할 수 없습니다.'}), 400
        
        # 특수 문자 필터링 (XSS 방지)
        message = re.sub(r'[<>"\']', '', message)
        
        # 이전 대화 기록 가져오기
        chat_history = chat_manager.get_chat_history(player_uuid, limit=10)
        
        # AI 응답 생성
        response = ai_model.generate_response(
            message=message,
            chat_history=chat_history,
            modpack_name=modpack_name,
            modpack_version=modpack_version,
            user_uuid=player_uuid
        )
        
        # 대화 기록 저장
        chat_manager.save_message(player_uuid, message, response, modpack_name)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        return jsonify({'error': '서버 오류가 발생했습니다.'}), 500

@app.route('/api/recipe/<item_name>', methods=['GET'])
def get_recipe(item_name):
    """아이템 제작법 조회 API"""
    try:
        modpack_name = request.args.get('modpack_name', 'unknown')
        modpack_version = request.args.get('modpack_version', '1.0')
        
        recipe = recipe_manager.get_recipe_with_version_fallback(item_name, modpack_name, modpack_version)
        
        if recipe:
            return jsonify(recipe)
        else:
            return jsonify({'error': '제작법을 찾을 수 없습니다.'}), 404
            
    except Exception as e:
        logger.error(f"제작법 조회 API 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/modpack/analyze', methods=['POST'])
@rate_limit
def analyze_modpack():
    """모드팩 분석 API"""
    try:
        data = request.get_json()
        modpack_path = data.get('modpack_path')
        
        if not modpack_path:
            return jsonify({'error': 'modpack_path는 필수입니다.'}), 400
        
        # 모드팩 분석
        analysis_result = modpack_analyzer.analyze_modpack(modpack_path)
        
        # 언어 매핑 자동 생성
        if analysis_result.get('analysis_status') == 'completed':
            mappings_added = language_mapper.analyze_modpack_for_mappings(analysis_result)
            analysis_result['language_mappings_added'] = mappings_added
        
        return jsonify(analysis_result)
        
    except Exception as e:
        logger.error(f"모드팩 분석 API 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history/<player_uuid>', methods=['GET'])
def get_chat_history(player_uuid):
    """플레이어의 채팅 기록 조회"""
    try:
        limit = request.args.get('limit', 20, type=int)
        history = chat_manager.get_chat_history(player_uuid, limit=limit)
        
        return jsonify({
            'player_uuid': player_uuid,
            'history': history
        })
        
    except Exception as e:
        logger.error(f"채팅 기록 조회 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/language/mapping', methods=['POST'])
@rate_limit
def add_custom_mapping():
    """사용자 정의 언어 매핑 추가"""
    try:
        data = request.get_json()
        korean_name = data.get('korean_name')
        english_name = data.get('english_name')
        modpack_name = data.get('modpack_name', 'unknown')
        user_uuid = data.get('user_uuid')
        
        if not all([korean_name, english_name, user_uuid]):
            return jsonify({'error': 'korean_name, english_name, user_uuid는 필수입니다.'}), 400
        
        language_mapper.add_custom_mapping(korean_name, english_name, modpack_name, user_uuid)
        
        return jsonify({
            'message': '매핑이 성공적으로 추가되었습니다.',
            'mapping': {
                'korean_name': korean_name,
                'english_name': english_name,
                'modpack_name': modpack_name,
                'user_uuid': user_uuid
            }
        })
        
    except Exception as e:
        logger.error(f"언어 매핑 추가 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/language/translate/<korean_name>', methods=['GET'])
@rate_limit
def translate_item_name(korean_name):
    """한글 아이템명을 영어로 변환"""
    try:
        modpack_name = request.args.get('modpack_name', 'unknown')
        user_uuid = request.args.get('user_uuid')
        
        english_name, confidence, source = language_mapper.find_english_name(
            korean_name, modpack_name, user_uuid
        )
        
        return jsonify({
            'korean_name': korean_name,
            'english_name': english_name,
            'confidence': confidence,
            'source': source
        })
        
    except Exception as e:
        logger.error(f"언어 변환 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/modpack/switch', methods=['POST'])
@rate_limit
def switch_modpack():
    """모드팩 변경 및 자동 설정"""
    try:
        data = request.get_json()
        modpack_path = data.get('modpack_path')
        modpack_name = data.get('modpack_name')
        modpack_version = data.get('modpack_version', '1.0')
        
        if not modpack_path or not modpack_name:
            return jsonify({'error': 'modpack_path와 modpack_name은 필수입니다.'}), 400
        
        # 1. 모드팩 분석
        logger.info(f"모드팩 분석 시작: {modpack_name} v{modpack_version}")
        analysis_result = modpack_analyzer.analyze_modpack(modpack_path)
        
        if analysis_result.get('analysis_status') != 'completed':
            return jsonify({'error': '모드팩 분석에 실패했습니다.'}), 500
        
        # 2. 언어 매핑 자동 생성
        logger.info("언어 매핑 자동 생성 중...")
        mappings_added = language_mapper.analyze_modpack_for_mappings(analysis_result)
        
        # 3. RAG 데이터 업데이트
        if rag_manager and analysis_result.get('mods'):
            logger.info("RAG 데이터 업데이트 중...")
            rag_manager.update_modpack_knowledge(modpack_name, analysis_result)
        
        # 4. 환경 변수 업데이트 (선택적)
        update_env = data.get('update_environment', False)
        if update_env:
            # 환경 변수 파일 업데이트 로직
            pass
        
        return jsonify({
            'message': f'모드팩 {modpack_name} v{modpack_version}로 성공적으로 변경되었습니다.',
            'analysis_result': analysis_result,
            'language_mappings_added': mappings_added,
            'rag_updated': rag_manager is not None
        })
        
    except Exception as e:
        logger.error(f"모드팩 변경 오류: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """사용 가능한 AI 모델 목록을 반환합니다."""
    try:
        if not ai_model:
            return jsonify({'error': 'AI 모델이 초기화되지 않았습니다.'}), 500
        
        models_info = ai_model.get_available_models_info()
        return jsonify({
            'models': models_info,
            'current_model': ai_model.current_model
        })
    except Exception as e:
        logger.error(f"모델 정보 조회 오류: {e}")
        return jsonify({'error': '모델 정보를 가져올 수 없습니다.'}), 500

@app.route('/api/models/switch', methods=['POST'])
@rate_limit
def switch_model():
    """AI 모델을 전환합니다."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON 데이터가 필요합니다.'}), 400
        
        model_id = data.get('model_id')
        if not model_id:
            return jsonify({'error': 'model_id가 필요합니다.'}), 400
        
        if not ai_model:
            return jsonify({'error': 'AI 모델이 초기화되지 않았습니다.'}), 500
        
        success = ai_model.switch_model(model_id)
        if success:
            return jsonify({
                'success': True,
                'current_model': ai_model.current_model,
                'message': f'모델이 {model_id}로 전환되었습니다.'
            })
        else:
            return jsonify({'error': f'모델 {model_id}로 전환할 수 없습니다.'}), 400
            
    except Exception as e:
        logger.error(f"모델 전환 오류: {e}")
        return jsonify({'error': '모델 전환 중 오류가 발생했습니다.'}), 500

@app.route('/api/models/current', methods=['GET'])
def get_current_model():
    """현재 사용 중인 AI 모델 정보를 반환합니다."""
    try:
        if not ai_model:
            return jsonify({'error': 'AI 모델이 초기화되지 않았습니다.'}), 500
        
        current_model_info = ai_model.available_models.get(ai_model.current_model, {})
        return jsonify({
            'current_model': ai_model.current_model,
            'model_info': current_model_info
        })
    except Exception as e:
        logger.error(f"현재 모델 정보 조회 오류: {e}")
        return jsonify({'error': '현재 모델 정보를 가져올 수 없습니다.'}), 500

if __name__ == '__main__':
    # 서비스 초기화
    initialize_services()
    
    # 서버 실행
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.run(host='0.0.0.0', port=port, debug=debug) 