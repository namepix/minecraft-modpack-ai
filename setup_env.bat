@echo off
echo 환경 설정 도우미

REM .env 파일 생성
if not exist ".env" (
    if exist "env.example" (
        copy "env.example" ".env"
        echo ✅ .env 파일이 생성되었습니다.
    ) else (
        echo ❌ env.example 파일을 찾을 수 없습니다.
        pause
        exit /b 1
    )
) else (
    echo .env 파일이 이미 존재합니다.
)

echo.
echo 📝 .env 파일을 편집하여 API 키를 설정하세요:
echo.
echo 필수 설정:
echo - GOOGLE_API_KEY=your-google-api-key (Gemini 2.5 Pro용)
echo.
echo 선택 설정:
echo - OPENAI_API_KEY=your-openai-api-key (백업용)
echo - ANTHROPIC_API_KEY=your-anthropic-api-key (백업용)
echo.
echo 1. 메모장으로 열기
echo 2. VS Code로 열기 (설치되어 있는 경우)
echo 3. 수동으로 편집 (종료)

set /p choice="선택하세요 (1-3): "

if "%choice%"=="1" (
    notepad .env
) else if "%choice%"=="2" (
    where code >nul 2>nul
    if %errorlevel% equ 0 (
        code .env
    ) else (
        echo VS Code가 설치되어 있지 않습니다. 메모장으로 열겠습니다.
        notepad .env
    )
) else (
    echo .env 파일을 수동으로 편집하세요.
)

echo.
echo API 키 획득 방법:
echo - Google AI Studio: https://aistudio.google.com/app/apikey
echo - OpenAI: https://platform.openai.com/api-keys
echo - Anthropic: https://console.anthropic.com/
echo.
echo 설정 완료 후 start_backend.bat을 실행하여 백엔드를 시작하세요.
pause