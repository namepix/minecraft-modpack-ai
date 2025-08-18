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

# 2. Fabric 모드 빌드 (강화된 오류 처리)
echo "🔨 Fabric 모드 빌드 시작"
echo "----------------------------"
if [ -d "minecraft_fabric_mod" ]; then
    cd minecraft_fabric_mod
    
    echo "✅ Gradle wrapper 확인/생성 (강화된 버전)"
    if [ ! -f "gradlew" ] || [ ! -x "gradlew" ]; then
        echo "   Gradle wrapper 생성 중..."
        
        # 시스템 Gradle 버전 확인
        SYSTEM_GRADLE_VERSION=""
        if command -v gradle &> /dev/null; then
            SYSTEM_GRADLE_VERSION=$(gradle --version 2>/dev/null | grep "Gradle" | head -1 | grep -o "[0-9]\+\.[0-9]\+" || echo "unknown")
        fi
        
        echo "   시스템 Gradle 버전: $SYSTEM_GRADLE_VERSION"
        
        # Gradle 8+ 필요, 시스템 버전이 오래된 경우 다운로드
        if [[ "$SYSTEM_GRADLE_VERSION" < "8.0" ]] || [[ "$SYSTEM_GRADLE_VERSION" == "unknown" ]]; then
            echo "   ⚠️ 시스템 Gradle 버전이 8.0 미만입니다. 최신 Gradle 다운로드 중..."
            
            # 임시 디렉토리에 최신 Gradle 다운로드
            GRADLE_VERSION="8.8"
            wget -q "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" -O /tmp/gradle-${GRADLE_VERSION}-bin.zip
            unzip -q /tmp/gradle-${GRADLE_VERSION}-bin.zip -d /tmp
            
            # 최신 Gradle로 wrapper 생성
            /tmp/gradle-${GRADLE_VERSION}/bin/gradle wrapper --gradle-version ${GRADLE_VERSION} --distribution-type all
            
            # 임시 파일 정리
            rm -rf /tmp/gradle-${GRADLE_VERSION} /tmp/gradle-${GRADLE_VERSION}-bin.zip
        else
            gradle wrapper --gradle-version 8.8 --distribution-type all
        fi
        
        chmod +x ./gradlew
    fi
    
    # Fabric Loom 플러그인 버전 검증 및 수정
    echo "📝 Fabric Loom 플러그인 버전 확인..."
    if grep -q "fabric-loom.*SNAPSHOT" build.gradle; then
        echo "   ⚠️ SNAPSHOT 버전 발견 - 안정 버전으로 변경합니다..."
        
        # 백업 생성
        cp build.gradle build.gradle.backup
        
        # SNAPSHOT을 안정 버전으로 변경
        sed -i "s/fabric-loom.*version.*'[^']*'/fabric-loom' version '1.5.7'/g" build.gradle
        
        echo "   ✅ Fabric Loom 버전을 1.5.7로 수정했습니다."
    fi
    
    echo "🧹 이전 빌드 결과물 정리"
    ./gradlew clean 2>/dev/null || {
        echo "   ⚠️ clean 실패, 캐시 삭제 후 재시도..."
        rm -rf .gradle build
        chmod +x ./gradlew
        ./gradlew clean
    }
    
    echo "📦 Fabric 모드 빌드"
    if ./gradlew build --refresh-dependencies; then
        echo "✅ Fabric 모드 빌드 성공"
    else
        echo "❌ Fabric 모드 빌드 실패 - 자동 수정 시도..."
        echo "   fix_fabric_build.sh 스크립트를 실행합니다..."
        
        cd "$ORIGINAL_DIR"
        if [ -f "fix_fabric_build.sh" ]; then
            chmod +x fix_fabric_build.sh
            ./fix_fabric_build.sh
            cd minecraft_fabric_mod
        else
            echo "   ❌ fix_fabric_build.sh 스크립트를 찾을 수 없습니다."
            echo "   수동으로 문제를 해결하세요."
            exit 1
        fi
    fi
    
    # 빌드 결과 확인 (더 유연한 검색)
    FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)
    if [ -f "$FABRIC_JAR" ]; then
        echo "✅ Fabric 모드 빌드 성공: $FABRIC_JAR"
        FABRIC_JAR="$FABRIC_JAR"
    else
        echo "❌ Fabric 모드 빌드 실패 - JAR 파일을 찾을 수 없습니다"
        echo "📋 build/libs/ 디렉토리 내용:"
        ls -la build/libs/ || echo "   디렉토리가 존재하지 않습니다."
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
