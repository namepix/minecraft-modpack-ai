@echo off
echo 마인크래프트 플러그인 빌드 중...

REM Maven이 설치되어 있는지 확인
where mvn >nul 2>nul
if %errorlevel% neq 0 (
    echo Maven이 설치되어 있지 않습니다.
    echo https://maven.apache.org/download.cgi 에서 Maven을 다운로드하여 설치하세요.
    pause
    exit /b 1
)

REM Java가 설치되어 있는지 확인
where java >nul 2>nul
if %errorlevel% neq 0 (
    echo Java가 설치되어 있지 않습니다.
    echo https://adoptium.net 에서 Java 11+을 다운로드하여 설치하세요.
    pause
    exit /b 1
)

echo Java 버전 확인:
java -version

echo Maven 버전 확인:
mvn -version

echo.
echo 플러그인 빌드 시작...
cd minecraft_plugin
mvn clean package

if %errorlevel% equ 0 (
    echo.
    echo ✅ 빌드 성공!
    echo 빌드된 파일: target\ModpackAI-1.0.jar
    echo.
    echo 이 파일을 마인크래프트 서버의 plugins 폴더에 복사하세요.
) else (
    echo.
    echo ❌ 빌드 실패!
    echo 에러 로그를 확인하여 문제를 해결하세요.
)

cd ..
pause