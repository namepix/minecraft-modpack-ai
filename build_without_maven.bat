@echo off
chcp 65001 >nul 2>&1
echo 🔨 Building without Maven
echo ========================

cd minecraft_plugin

echo [INFO] Creating target directory...
mkdir target 2>nul

echo [INFO] Downloading Spigot API...
curl -L "https://hub.spigotmc.org/nexus/service/local/artifact/maven/redirect?r=snapshots&g=org.spigotmc&a=spigot-api&v=1.20.1-R0.1-SNAPSHOT" -o target\spigot-api.jar

echo [INFO] Compiling Java sources...
javac -cp "target\spigot-api.jar" -d target\classes src\main\java\com\modpackai\*.java

echo [INFO] Copying resources...
xcopy src\main\resources target\classes\ /E /I /Y >nul 2>&1

echo [INFO] Creating JAR...
cd target\classes
jar cf ..\ModpackAI-1.0.jar *
cd ..\..

if exist target\ModpackAI-1.0.jar (
    echo [✅] Build successful: target\ModpackAI-1.0.jar
) else (
    echo [❌] Build failed
)

echo.
pause