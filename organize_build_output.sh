#!/bin/bash
# 빌드 결과물 정리 스크립트
# 이미 빌드된 모드들을 build_output/ 폴더에 정리합니다

set -e

echo "📂 빌드 결과물 정리 시작"
echo "========================"

# 현재 디렉토리 저장
ORIGINAL_DIR=$(pwd)

# 빌드 결과물 폴더 생성
BUILD_OUTPUT_DIR="build_output"
mkdir -p "$BUILD_OUTPUT_DIR"

echo "✅ 빌드 결과물 폴더 생성: $BUILD_OUTPUT_DIR"

# NeoForge 모드 파일 찾기 및 복사
echo ""
echo "🔨 NeoForge 모드 파일 정리..."
if [ -d "minecraft_mod" ]; then
    NEOFORGE_JAR=$(find minecraft_mod/build/libs -name "modpackai-*.jar" 2>/dev/null | head -n1)
    
    if [ -f "$NEOFORGE_JAR" ]; then
        cp "$NEOFORGE_JAR" "$BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar"
        echo "✅ NeoForge 모드: $BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar"
        
        # 파일 크기 정보
        NEOFORGE_SIZE=$(ls -lh "$BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar" | awk '{print $5}')
        echo "   크기: $NEOFORGE_SIZE"
    else
        echo "⚠️ NeoForge 모드 빌드 파일을 찾을 수 없습니다"
        echo "   빌드가 필요한 경우: cd minecraft_mod && ./gradlew build"
    fi
else
    echo "⚠️ minecraft_mod 디렉토리를 찾을 수 없습니다"
fi

# Fabric 모드 파일 찾기 및 복사
echo ""
echo "🧵 Fabric 모드 파일 정리..."
if [ -d "minecraft_fabric_mod" ]; then
    FABRIC_JAR=$(find minecraft_fabric_mod/build/libs -name "modpackai-fabric-*.jar" 2>/dev/null | head -n1)
    
    if [ -f "$FABRIC_JAR" ]; then
        cp "$FABRIC_JAR" "$BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar"
        echo "✅ Fabric 모드: $BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar"
        
        # 파일 크기 정보
        FABRIC_SIZE=$(ls -lh "$BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar" | awk '{print $5}')
        echo "   크기: $FABRIC_SIZE"
    else
        echo "⚠️ Fabric 모드 빌드 파일을 찾을 수 없습니다"
        echo "   빌드가 필요한 경우: cd minecraft_fabric_mod && ./gradlew build"
        echo "   또는 빌드 문제 해결: ./fix_fabric_build.sh"
    fi
else
    echo "⚠️ minecraft_fabric_mod 디렉토리를 찾을 수 없습니다"
fi

echo ""
echo "📋 빌드 결과물 정리 완료"
echo "========================"
echo "📁 정리 결과물 위치: $BUILD_OUTPUT_DIR/"

# 폴더 내용 확인
if [ -d "$BUILD_OUTPUT_DIR" ] && [ "$(ls -A $BUILD_OUTPUT_DIR)" ]; then
    echo ""
    echo "📦 정리된 파일들:"
    ls -la "$BUILD_OUTPUT_DIR/"
    echo ""
    
    # 사용법 안내
    echo "🎯 사용법:"
    echo "  - NeoForge 서버: modpackai-neoforge-1.0.0.jar를 mods/ 폴더에 복사"
    echo "  - Fabric 서버: modpackai-fabric-1.0.0.jar를 mods/ 폴더에 복사"
    echo ""
    echo "⚠️  주의: 두 모드를 동시에 설치하지 마세요!"
else
    echo ""
    echo "⚠️ 정리할 빌드 파일이 없습니다"
    echo "   먼저 다음 중 하나를 실행하세요:"
    echo "   - 개별 빌드: cd minecraft_mod && ./gradlew build"
    echo "   - 개별 빌드: cd minecraft_fabric_mod && ./gradlew build" 
    echo "   - 통합 빌드: ./build_all_mods.sh"
fi