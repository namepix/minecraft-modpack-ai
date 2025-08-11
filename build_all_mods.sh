#!/bin/bash

# ModpackAI 통합 빌드 스크립트
# NeoForge와 Fabric 모드를 모두 빌드합니다

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 ModpackAI 통합 빌드 시작"
echo "================================"

# 현재 디렉토리 저장
ORIGINAL_DIR=$(pwd)

# Java 버전 확인
echo "📋 Java 버전 확인"
java -version
echo ""

# 1. NeoForge 모드 빌드
echo "🔨 NeoForge 모드 빌드 시작"
echo "------------------------------"
if [ -d "minecraft_mod" ]; then
    cd minecraft_mod
    
    echo "✅ Gradle wrapper 확인/생성"
    if [ ! -f "gradlew" ]; then
        echo "   Gradle wrapper 생성 중..."
        gradle wrapper --gradle-version 8.8 --distribution-type all
    fi
    
    echo "🧹 이전 빌드 결과물 정리"
    ./gradlew clean
    
    echo "📦 NeoForge 모드 빌드"
    ./gradlew build
    
    # 빌드 결과 확인
    if [ -f "build/libs/modpackai-1.0.0.jar" ]; then
        echo "✅ NeoForge 모드 빌드 성공: build/libs/modpackai-1.0.0.jar"
        NEOFORGE_JAR="build/libs/modpackai-1.0.0.jar"
    else
        echo "❌ NeoForge 모드 빌드 실패"
        cd "$ORIGINAL_DIR"
        exit 1
    fi
    
    cd "$ORIGINAL_DIR"
else
    echo "❌ minecraft_mod 디렉토리를 찾을 수 없습니다"
    exit 1
fi

echo ""

# 2. Fabric 모드 빌드
echo "🔨 Fabric 모드 빌드 시작"
echo "----------------------------"
if [ -d "minecraft_fabric_mod" ]; then
    cd minecraft_fabric_mod
    
    echo "✅ Gradle wrapper 확인/생성"
    if [ ! -f "gradlew" ]; then
        echo "   Gradle wrapper 생성 중..."
        gradle wrapper --gradle-version 8.8 --distribution-type all
    fi
    
    echo "🧹 이전 빌드 결과물 정리"
    ./gradlew clean
    
    echo "📦 Fabric 모드 빌드"
    ./gradlew build
    
    # 빌드 결과 확인
    if [ -f "build/libs/modpackai-fabric-1.0.0.jar" ]; then
        echo "✅ Fabric 모드 빌드 성공: build/libs/modpackai-fabric-1.0.0.jar"
        FABRIC_JAR="build/libs/modpackai-fabric-1.0.0.jar"
    else
        echo "❌ Fabric 모드 빌드 실패"
        cd "$ORIGINAL_DIR"
        exit 1
    fi
    
    cd "$ORIGINAL_DIR"
else
    echo "❌ minecraft_fabric_mod 디렉토리를 찾을 수 없습니다"
    exit 1
fi

echo ""

# 3. 빌드 결과물 정리
echo "📂 빌드 결과물 정리"
echo "----------------------"
BUILD_OUTPUT_DIR="build_output"
mkdir -p "$BUILD_OUTPUT_DIR"

# NeoForge JAR 복사
if [ -f "minecraft_mod/$NEOFORGE_JAR" ]; then
    cp "minecraft_mod/$NEOFORGE_JAR" "$BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar"
    echo "✅ NeoForge 모드: $BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar"
fi

# Fabric JAR 복사
if [ -f "minecraft_fabric_mod/$FABRIC_JAR" ]; then
    cp "minecraft_fabric_mod/$FABRIC_JAR" "$BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar"
    echo "✅ Fabric 모드: $BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar"
fi

echo ""

# 4. 빌드 완료 정보
echo "🎉 빌드 완료!"
echo "=============="
echo "📁 빌드 결과물 위치: $BUILD_OUTPUT_DIR/"
ls -la "$BUILD_OUTPUT_DIR/"
echo ""

# 파일 크기 정보
if [ -f "$BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar" ]; then
    NEOFORGE_SIZE=$(ls -lh "$BUILD_OUTPUT_DIR/modpackai-neoforge-1.0.0.jar" | awk '{print $5}')
    echo "📦 NeoForge 모드: $NEOFORGE_SIZE"
fi

if [ -f "$BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar" ]; then
    FABRIC_SIZE=$(ls -lh "$BUILD_OUTPUT_DIR/modpackai-fabric-1.0.0.jar" | awk '{print $5}')
    echo "📦 Fabric 모드: $FABRIC_SIZE"
fi

echo ""
echo "🎯 사용법:"
echo "  - NeoForge 서버: modpackai-neoforge-1.0.0.jar를 mods/ 폴더에 복사"
echo "  - Fabric 서버: modpackai-fabric-1.0.0.jar를 mods/ 폴더에 복사"
echo ""
echo "⚠️  주의: 두 모드를 동시에 설치하지 마세요!"