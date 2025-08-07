@echo off
echo 마인크래프트 AI API 테스트 중...

REM curl이 설치되어 있는지 확인
where curl >nul 2>nul
if %errorlevel% neq 0 (
    echo curl이 설치되어 있지 않습니다.
    echo Windows 10 1803 이상에서는 기본 설치되어 있어야 합니다.
    pause
    exit /b 1
)

echo.
echo 1. Health Check 테스트...
curl -X GET http://localhost:5000/health
echo.

echo.
echo 2. 모델 목록 확인...
curl -X GET http://localhost:5000/models
echo.

echo.
echo 3. 간단한 채팅 테스트...
curl -X POST http://localhost:5000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"안녕하세요\",\"player_uuid\":\"test-uuid\",\"modpack_name\":\"test\",\"modpack_version\":\"1.0\"}"
echo.

echo.
echo 4. 제작법 조회 테스트...
curl -X GET http://localhost:5000/recipe/diamond
echo.

echo.
echo API 테스트 완료!
pause