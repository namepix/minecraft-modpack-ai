#!/bin/bash
# Fabric 모드 대안 해결 방법 (공식 템플릿 기반)

set -euo pipefail

echo "🔄 대안 방법: 공식 Fabric 템플릿으로 재구성..."

cd ~/minecraft-modpack-ai

echo "💾 1단계: 기존 Fabric 모드 백업..."
if [ -d "minecraft_fabric_mod" ]; then
    mv minecraft_fabric_mod minecraft_fabric_mod_backup_$(date +%Y%m%d_%H%M%S)
    echo "✅ 백업 완료"
fi

echo "📥 2단계: 공식 Fabric 템플릿 다운로드..."
git clone https://github.com/FabricMC/fabric-example-mod.git minecraft_fabric_mod
cd minecraft_fabric_mod

echo "🔧 3단계: 프로젝트 정보 수정..."
# gradle.properties 수정
cat > gradle.properties << 'EOF'
# Gradle 최적화
org.gradle.jvmargs=-Xmx3G
org.gradle.parallel=true
org.gradle.caching=true

# Fabric Properties - 2025년 8월 최신
minecraft_version=1.20.1
yarn_mappings=1.20.1+build.10
loader_version=0.15.11

# 모드 정보
mod_version=1.0.0
maven_group=com.modpackai
archives_base_name=modpackai-fabric

# Dependencies
fabric_version=0.92.2+1.20.1
EOF

# fabric.mod.json 수정
cat > src/main/resources/fabric.mod.json << 'EOF'
{
    "schemaVersion": 1,
    "id": "modpackai",
    "version": "${version}",
    "name": "Modpack AI Assistant",
    "description": "AI-powered assistant for Minecraft modpacks with Gemini 2.5 Pro integration",
    "authors": ["ModpackAI Team"],
    "contact": {
        "homepage": "https://github.com/namepix/minecraft-modpack-ai",
        "sources": "https://github.com/namepix/minecraft-modpack-ai"
    },
    "license": "MIT",
    "icon": "assets/modpackai/icon.png",
    "environment": "*",
    "entrypoints": {
        "main": ["com.modpackai.ModpackAIMod"],
        "client": ["com.modpackai.client.ModpackAIClientMod"]
    },
    "mixins": [],
    "depends": {
        "fabricloader": ">=0.14.0",
        "minecraft": "~1.20.1",
        "java": ">=21",
        "fabric-api": "*"
    }
}
EOF

echo "📂 4단계: 기존 소스 코드 복사..."
BACKUP_DIR=$(ls -1d ../minecraft_fabric_mod_backup_* | head -1)
if [ -d "$BACKUP_DIR/src" ]; then
    rm -rf src/main/java/net  # 예제 코드 삭제
    cp -r "$BACKUP_DIR/src/main/java/com" src/main/java/ 2>/dev/null || true
    echo "✅ 소스 코드 복사 완료"
fi

echo "🔨 5단계: 빌드 실행..."
./gradlew clean build

echo "✅ 6단계: 빌드 결과 확인..."
FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)
if [ -f "$FABRIC_JAR" ]; then
    echo "🎉 대안 방법으로 Fabric 모드 빌드 성공!"
    echo "📦 빌드된 파일: $FABRIC_JAR"
    ls -la build/libs/
else
    echo "❌ 대안 방법도 실패했습니다."
    exit 1
fi

echo "🎯 공식 템플릿 기반 Fabric 모드 구성 완료!"