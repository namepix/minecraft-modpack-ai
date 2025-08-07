@echo off
echo 마인크래프트 AI 백엔드 시작 중...

REM 가상환경 활성화
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo 가상환경이 설치되어 있지 않습니다.
    echo 먼저 install.ps1을 실행하여 설치하세요.
    pause
    exit /b 1
)

REM .env 파일 확인
if not exist ".env" (
    echo .env 파일이 없습니다. env.example을 복사하여 .env를 만들고 API 키를 설정하세요.
    pause
    exit /b 1
)

REM 백엔드 디렉토리로 이동 후 서버 시작
cd backend
python app.py

pause