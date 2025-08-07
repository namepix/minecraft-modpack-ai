@echo off
chcp 65001 >nul 2>&1
echo 🧪 Quick Local Test Fixed
echo ========================

echo [TEST] Python Check
python --version
if %errorlevel%==0 (echo [✅] Python OK) else (echo [❌] Python Missing)

echo [TEST] Java Check  
java -version >nul 2>&1
if %errorlevel%==0 (echo [✅] Java OK) else (echo [❌] Java Missing)

echo [TEST] Maven Check
echo Checking Maven...
mvn -version >nul 2>&1
if %errorlevel%==0 (
    echo [✅] Maven OK
    mvn -version | findstr "Apache Maven"
) else (
    echo [❌] Maven Missing or PATH issue
    where mvn
)

echo [TEST] Project Files
if exist backend\app.py (echo [✅] Backend OK) else (echo [❌] Backend Missing)
if exist minecraft_plugin\pom.xml (echo [✅] Plugin OK) else (echo [❌] Plugin Missing)

echo.
echo [TEST] Maven Build
if exist minecraft_plugin\pom.xml (
    echo Building plugin...
    cd minecraft_plugin
    echo Current directory: %cd%
    mvn --version
    mvn clean compile -q
    if %errorlevel%==0 (
        echo Compile OK, now packaging...
        mvn package -q -Dmaven.test.skip=true
        if %errorlevel%==0 (echo [✅] Build OK) else (echo [❌] Package Failed)
    ) else (
        echo [❌] Compile Failed
    )
    cd ..
) else (
    echo [❌] pom.xml not found
)

echo.
echo ✅ Quick test completed!
pause