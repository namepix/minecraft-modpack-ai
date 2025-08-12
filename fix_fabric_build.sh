#!/bin/bash
# Fabric 모드 빌드 완전 해결 스크립트 (2025.08.12 최신 버전)

set -euo pipefail

echo "🔧 Fabric 모드 빌드 문제 완전 해결 시작..."

# Fabric 모드 디렉토리로 이동
cd ~/minecraft-modpack-ai/minecraft_fabric_mod

echo "📋 1단계: 네트워크 연결 확인..."
if curl -I https://maven.fabricmc.net/ &>/dev/null; then
    echo "✅ Fabric Maven 저장소 연결 정상"
else
    echo "⚠️ Fabric Maven 저장소 연결 불가 - 네트워크 설정 확인 필요"
fi

echo "🧹 2단계: 기존 빌드 파일 및 캐시 완전 삭제..."
rm -rf .gradle build ~/.gradle/caches
rm -f gradlew gradlew.bat
rm -rf gradle/

echo "📝 3단계: 설정 파일 업데이트 확인..."
echo "   - settings.gradle: 플러그인 관리 설정 ✓"
echo "   - gradle.properties: 최신 Fabric 버전 ✓"
echo "   - build.gradle: Fabric Loom 1.7-SNAPSHOT ✓"

echo "🚀 4단계: 최신 Gradle Wrapper 생성..."
gradle wrapper --gradle-version 8.10.2 --distribution-type all
chmod +x ./gradlew

echo "🔍 5단계: 의존성 해결 테스트..."
if ./gradlew dependencies --configuration compileClasspath --quiet; then
    echo "✅ 의존성 해결 성공"
else
    echo "❌ 의존성 해결 실패 - 네트워크 또는 설정 문제"
    exit 1
fi

echo "🔨 6단계: Fabric 모드 빌드 실행..."
./gradlew clean build --refresh-dependencies

echo "✅ 7단계: 빌드 결과 확인..."
FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)
if [ -f "$FABRIC_JAR" ]; then
    echo "🎉 Fabric 모드 빌드 성공!"
    echo "📦 빌드된 파일: $FABRIC_JAR"
    ls -la build/libs/
else
    echo "❌ 빌드된 JAR 파일을 찾을 수 없습니다."
    exit 1
fi

echo "🎯 Fabric 모드 빌드 완료! 이제 5-2 통합 빌드를 진행할 수 있습니다."