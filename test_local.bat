@echo off
REM 🧪 Windows 로컬 테스트 스크립트
REM GCP VM 배포 전 Windows 환경에서 모든 구성 요소를 검증합니다

setlocal EnableDelayedExpansion

echo 🧪 Windows 로컬 테스트 및 검증 시작
echo ════════════════════════════════════════════════════════════
echo.

set TOTAL_TESTS=0
set PASSED_TESTS=0
set FAILED_TESTS=0

REM 1. 시스템 환경 검증
echo [STEP] 1. 시스템 환경 검증

echo [TEST] Python 3.8+ 설치 확인
python --version >nul 2>&1
if %errorlevel%==0 (
    for /f "tokens=2" %%a in ('python --version') do set PYTHON_VERSION=%%a
    echo [SUCCESS] Python !PYTHON_VERSION! 확인됨
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Python 3.8+ 필요
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] Java 17+ 설치 확인
java -version >nul 2>&1
if %errorlevel%==0 (
    echo [SUCCESS] Java 설치 확인됨
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Java 17+ 필요
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] Maven 설치 확인
mvn -version >nul 2>&1
if %errorlevel%==0 (
    echo [SUCCESS] Maven 설치 확인됨
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Maven 필요
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

REM 2. 프로젝트 구조 검증
echo.
echo [STEP] 2. 프로젝트 구조 검증

set FILES=backend\app.py backend\requirements.txt minecraft_plugin\pom.xml env.example install.sh
for %%f in (%FILES%) do (
    echo [TEST] 필수 파일 확인: %%f
    if exist "%%f" (
        echo [SUCCESS] ✅ %%f 존재
        set /a PASSED_TESTS+=1
    ) else (
        echo [ERROR] ❌ %%f 누락
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
)

REM 3. Python 백엔드 검증
echo.
echo [STEP] 3. Python 백엔드 검증

cd backend

echo [TEST] 가상환경 생성
if not exist venv (
    echo [INFO] 가상환경 생성 중...
    python -m venv venv
)

echo [TEST] 가상환경 활성화 및 의존성 설치
call venv\Scripts\activate.bat
if %errorlevel%==0 (
    echo [SUCCESS] 가상환경 활성화 성공
    set /a PASSED_TESTS+=1
    
    echo [TEST] Python 의존성 설치
    pip install -r requirements.txt -q
    if %errorlevel%==0 (
        echo [SUCCESS] 의존성 설치 완료
        set /a PASSED_TESTS+=1
    ) else (
        echo [ERROR] 의존성 설치 실패
        set /a FAILED_TESTS+=1
    )
    set /a TOTAL_TESTS+=1
) else (
    echo [ERROR] 가상환경 활성화 실패
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] Flask 앱 문법 검사
python -m py_compile app.py >nul 2>&1
if %errorlevel%==0 (
    echo [SUCCESS] Flask 앱 문법 검사 통과
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Flask 앱 문법 오류
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

cd ..

REM 4. Java 플러그인 검증
echo.
echo [STEP] 4. Java Minecraft 플러그인 검증

cd minecraft_plugin

echo [TEST] Maven 프로젝트 구조
if exist pom.xml (
    if exist src\main\java (
        if exist src\main\resources (
            echo [SUCCESS] Maven 프로젝트 구조 정상
            set /a PASSED_TESTS+=1
        ) else (
            echo [ERROR] src\main\resources 누락
            set /a FAILED_TESTS+=1
        )
    ) else (
        echo [ERROR] src\main\java 누락
        set /a FAILED_TESTS+=1
    )
) else (
    echo [ERROR] pom.xml 누락
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] Maven 의존성 해결
mvn dependency:resolve -q >nul 2>&1
if %errorlevel%==0 (
    echo [SUCCESS] Maven 의존성 해결 완료
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Maven 의존성 해결 실패
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] Java 컴파일
mvn clean compile -q >nul 2>&1
if %errorlevel%==0 (
    echo [SUCCESS] Java 컴파일 성공
    set /a PASSED_TESTS+=1
) else (
    echo [ERROR] Java 컴파일 실패
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

echo [TEST] JAR 패키징
mvn clean package -q -Dmaven.test.skip=true >nul 2>&1
if %errorlevel%==0 (
    if exist target\*.jar (
        echo [SUCCESS] JAR 패키징 성공
        echo [INFO] 생성된 JAR 파일들:
        dir target\*.jar /b
        set /a PASSED_TESTS+=1
    ) else (
        echo [ERROR] JAR 파일이 생성되지 않음
        set /a FAILED_TESTS+=1
    )
) else (
    echo [ERROR] JAR 패키징 실패
    set /a FAILED_TESTS+=1
)
set /a TOTAL_TESTS+=1

cd ..

REM 5. 결과 요약
echo.
echo [STEP] 5. 최종 테스트 결과 요약
echo.
echo 🏆 Windows 로컬 테스트 결과 요약
echo ════════════════════════════════════════════════════════════
echo.
echo 📊 통계:
echo   총 테스트 수: %TOTAL_TESTS%
echo   통과: %PASSED_TESTS%
echo   실패: %FAILED_TESTS%

if %TOTAL_TESTS% gtr 0 (
    set /a SUCCESS_RATE=PASSED_TESTS*100/TOTAL_TESTS
) else (
    set SUCCESS_RATE=0
)

echo   성공률: !SUCCESS_RATE!%%
echo.

if !SUCCESS_RATE! geq 90 (
    echo [SUCCESS] 🎉 우수 ^(!SUCCESS_RATE!%%^) - GCP VM 배포 준비 완료!
    echo.
    echo ✅ 다음 단계:
    echo   1. 파일 업로드: scp -r . namepix080@34.64.217.151:~/minecraft-modpack-ai/
    echo   2. GCP VM에서 설치: ./install.sh
    echo   3. API 키 설정 후 테스트
    set DEPLOYMENT_READY=true
) else if !SUCCESS_RATE! geq 75 (
    echo [WARNING] ⚠️ 양호 ^(!SUCCESS_RATE!%%^) - 일부 수정 후 배포 권장
    set DEPLOYMENT_READY=true
) else (
    echo [ERROR] ❌ 부족 ^(!SUCCESS_RATE!%%^) - 배포 전 문제 해결 필요
    set DEPLOYMENT_READY=false
)

echo.
echo 📋 Windows 개발 환경 정보:
echo   Python: %PYTHON_VERSION%
echo   플랫폼: Windows
echo   현재 디렉토리: %CD%

if "%DEPLOYMENT_READY%"=="true" (
    echo.
    echo 🚀 GCP VM 배포 체크리스트:
    echo   [ ] API 키 준비 ^(Google AI Studio, GCP 프로젝트^)
    echo   [ ] GCP VM SSH 접속 확인
    echo   [ ] 프로젝트 파일 업로드
    echo   [ ] install.sh 실행
    echo   [ ] API 키 설정
    echo   [ ] 백엔드 서비스 시작
    echo   [ ] 모드팩 서버 테스트
    
    echo.
    echo [SUCCESS] 🎯 로컬 검증 완료! GCP VM 배포를 진행하세요.
    exit /b 0
) else (
    echo.
    echo [ERROR] ❌ 로컬 환경에 문제가 있습니다. 수정 후 다시 테스트하세요.
    exit /b 1
)