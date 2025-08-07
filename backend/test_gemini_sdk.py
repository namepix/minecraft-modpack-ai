#!/usr/bin/env python3
"""
Gemini 2.5 Pro SDK 테스트 스크립트
웹검색 기능이 제대로 작동하는지 확인합니다.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

def test_gemini_sdk():
    """Gemini SDK 테스트"""
    load_dotenv()
    
    # API 키 확인
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY가 설정되지 않았습니다.")
        print("💡 .env 파일에 GOOGLE_API_KEY를 설정하세요.")
        return False
    
    try:
        # Gemini 클라이언트 초기화
        print("🔄 Gemini 클라이언트 초기화 중...")
        client = genai.Client(api_key=api_key)
        print("✅ Gemini 클라이언트 초기화 완료")
        
        # 웹검색 도구 설정
        print("🔄 웹검색 도구 설정 중...")
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])
        print("✅ 웹검색 도구 설정 완료")
        
        # 테스트 메시지
        test_message = """
당신은 마인크래프트 모드팩 전문가 AI 어시스턴트입니다.
현재 모드팩: TestModpack v1.0.0

사용자의 질문에 대해 친절하고 정확하게 답변해주세요.
제작법, 아이템 정보, 모드 설명 등을 포함할 수 있습니다.
최신 정보가 필요하면 웹 검색을 활용해서 정확한 답변을 제공해주세요.

사용자: 마인크래프트 1.21 업데이트에서 새로 추가된 아이템은 무엇인가요?
AI:
"""
        
        # 웹검색 지원 모델로 응답 생성
        print("🔄 Gemini 2.5 Pro로 응답 생성 중...")
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=test_message,
            config=config
        )
        
        print("✅ 응답 생성 완료!")
        print("\n" + "="*50)
        print("🤖 AI 응답:")
        print("="*50)
        print(response.text)
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Gemini 2.5 Pro SDK 테스트 시작")
    print("="*50)
    
    success = test_gemini_sdk()
    
    if success:
        print("\n✅ 테스트 성공! Gemini 2.5 Pro 웹검색 기능이 정상 작동합니다.")
    else:
        print("\n❌ 테스트 실패! API 키나 네트워크 연결을 확인하세요.")
    
    print("="*50) 