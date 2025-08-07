@echo off
chcp 65001 >nul 2>&1
echo 🧪 Quick Local Test
echo ==================

echo [TEST] Python Check
python --version
if %errorlevel%==0 (echo [✅] Python OK) else (echo [❌] Python Missing)

echo [TEST] Java Check  
java -version >nul 2>&1
if %errorlevel%==0 (echo [✅] Java OK) else (echo [❌] Java Missing)

echo [TEST] Maven Check
mvn -version >nul 2>&1
if %errorlevel%==0 (echo [✅] Maven OK) else (echo [❌] Maven Missing)

echo [TEST] Project Files
if exist backend\app.py (echo [✅] Backend OK) else (echo [❌] Backend Missing)
if exist minecraft_plugin\pom.xml (echo [✅] Plugin OK) else (echo [❌] Plugin Missing)

echo.
echo [TEST] Maven Build
cd minecraft_plugin
mvn clean package -q -Dmaven.test.skip=true
if %errorlevel%==0 (echo [✅] Build OK) else (echo [❌] Build Failed)

echo.
echo ✅ Quick test completed!
pause