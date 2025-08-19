#!/bin/bash

# ModpackAI 다중 Java 버전 통합 빌드 스크립트
# Java 17과 Java 21 버전을 모두 빌드합니다

set -e  # 오류 발생 시 스크립트 중단

echo "🚀 ModpackAI 다중 Java 버전 빌드 시작"
echo "=========================================="

# 현재 디렉토리 저장
ORIGINAL_DIR=$(pwd)

# Java 버전 배열
JAVA_VERSIONS=(17 21)

# 모드팩별 권장 Java 버전 (build.properties에서 자동 읽기)
declare -A MODPACK_JAVA_MAP
if [ -f "build.properties" ]; then
    while IFS='=' read -r key value; do
        if [[ $key != \#* && $key == *"="* ]]; then
            # 모드팩 매핑 파싱 (enigmatica_10=21 형식)
            if [[ $key =~ ^[a-z_0-9]+$ ]]; then
                MODPACK_JAVA_MAP["$key"]="$value"
            fi
        fi
    done < build.properties
fi

# Java 버전 확인
echo "📋 시스템 Java 버전 확인"
java -version
echo ""

# 빌드 결과물 정리 디렉토리
BUILD_OUTPUT_DIR="build_output"
mkdir -p "$BUILD_OUTPUT_DIR"

echo "🔧 지원하는 Java 버전: ${JAVA_VERSIONS[*]}"
echo ""

# 각 Java 버전별로 빌드
for java_ver in "${JAVA_VERSIONS[@]}"; do
    echo "==============================================="
    echo "🎯 Java $java_ver 버전 빌드 시작"
    echo "==============================================="
    
    # 1. NeoForge 모드 빌드 (Java 버전별)
    echo "🔨 NeoForge 모드 빌드 (Java $java_ver)"
    echo "--------------------------------------"
    if [ -d "minecraft_mod" ]; then
        cd minecraft_mod
        
        echo "✅ Gradle wrapper 확인/생성"
        if [ ! -f "gradlew" ]; then
            echo "   Gradle wrapper 생성 중..."
            gradle wrapper --gradle-version 8.8 --distribution-type all
        fi
        
        echo "🧹 이전 빌드 결과물 정리"
        ./gradlew clean
        
        echo "📦 NeoForge 모드 빌드 (Java $java_ver)"
        # Java 버전을 Gradle 프로퍼티로 전달
        ./gradlew build -PtargetJavaVersion=$java_ver
        
        # 빌드 결과 확인 및 복사
        if [ -f "build/libs/modpackai-1.0.0.jar" ]; then
            echo "✅ NeoForge 모드 빌드 성공 (Java $java_ver)"
            cp "build/libs/modpackai-1.0.0.jar" "$ORIGINAL_DIR/$BUILD_OUTPUT_DIR/modpackai-neoforge-java${java_ver}-1.0.0.jar"
        else
            echo "❌ NeoForge 모드 빌드 실패 (Java $java_ver)"
        fi
        
        cd "$ORIGINAL_DIR"
    else
        echo "❌ minecraft_mod 디렉토리를 찾을 수 없습니다"
    fi
    
    echo ""
    
    # 2. Fabric 모드 빌드 (Java 버전별)
    echo "🔨 Fabric 모드 빌드 (Java $java_ver)"
    echo "------------------------------------"
    if [ -d "minecraft_fabric_mod" ]; then
        cd minecraft_fabric_mod
        
        echo "✅ Gradle wrapper 확인/생성"
        if [ ! -f "gradlew" ] || [ ! -x "gradlew" ]; then
            echo "   Gradle wrapper 생성 중..."
            gradle wrapper --gradle-version 8.8 --distribution-type all
            chmod +x ./gradlew
        fi
        
        echo "🧹 이전 빌드 결과물 정리"
        ./gradlew clean
        
        echo "📦 Fabric 모드 빌드 (Java $java_ver)"
        # Java 버전을 Gradle 프로퍼티로 전달
        if ./gradlew build -PtargetJavaVersion=$java_ver --refresh-dependencies; then
            echo "✅ Fabric 모드 빌드 성공 (Java $java_ver)"
            
            # 빌드 결과 확인 및 복사
            FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)
            if [ -f "$FABRIC_JAR" ]; then
                cp "$FABRIC_JAR" "$ORIGINAL_DIR/$BUILD_OUTPUT_DIR/modpackai-fabric-java${java_ver}-1.0.0.jar"
            fi
        else
            echo "❌ Fabric 모드 빌드 실패 (Java $java_ver)"
        fi
        
        cd "$ORIGINAL_DIR"
    else
        echo "❌ minecraft_fabric_mod 디렉토리를 찾을 수 없습니다"
    fi
    
    echo ""
done

# 3. 빌드 완료 정보
echo "🎉 다중 Java 버전 빌드 완료!"
echo "==============================="
echo "📁 빌드 결과물 위치: $BUILD_OUTPUT_DIR/"
ls -la "$BUILD_OUTPUT_DIR/"
echo ""

# 모드팩별 사용 가이드 생성
echo "📋 모드팩별 사용 가이드:"
echo "========================"

# 알려진 모드팩들에 대한 가이드
declare -A KNOWN_MODPACKS=(
    ["enigmatica_10"]="NeoForge, Java 21"
    ["prominence_2"]="Fabric, Java 17"
    ["all_the_mods_9"]="NeoForge, Java 21"
    ["vault_hunters"]="Fabric, Java 17"
    ["create_above_and_beyond"]="Fabric, Java 17"
    ["better_minecraft"]="Fabric, Java 17"
)

for modpack in "${!KNOWN_MODPACKS[@]}"; do
    info="${KNOWN_MODPACKS[$modpack]}"
    platform=$(echo "$info" | cut -d',' -f1)
    java_req=$(echo "$info" | cut -d',' -f2 | tr -d ' ')
    
    if [[ $platform == "NeoForge" ]]; then
        jar_name="modpackai-neoforge-${java_req,,}-1.0.0.jar"
    else
        jar_name="modpackai-fabric-${java_req,,}-1.0.0.jar"
    fi
    
    if [ -f "$BUILD_OUTPUT_DIR/$jar_name" ]; then
        echo "✅ $modpack ($info): $jar_name"
    else
        echo "❌ $modpack ($info): $jar_name (빌드 실패)"
    fi
done

echo ""
echo "🎯 사용법:"
echo "========="
echo "1. 해당 모드팩의 mods/ 폴더에 올바른 JAR 파일을 복사하세요"
echo "2. 기존 modpackai*.jar 파일이 있다면 제거하세요"
echo "3. 서버를 재시작하세요"
echo ""
echo "⚠️  주의사항:"
echo "- 같은 모드팩에 여러 버전을 동시에 설치하지 마세요"
echo "- Java 버전이 모드팩 요구사항과 일치하는지 확인하세요"
echo ""

# 성공한 빌드 개수 확인
success_count=$(ls -1 "$BUILD_OUTPUT_DIR"/modpackai-*.jar 2>/dev/null | wc -l)
total_expected=$((${#JAVA_VERSIONS[@]} * 2))  # 2 platforms * Java versions

echo "📊 빌드 결과: $success_count/$total_expected 성공"

if [ $success_count -eq $total_expected ]; then
    echo "🎉 모든 빌드가 성공했습니다!"
    exit 0
else
    echo "⚠️ 일부 빌드가 실패했습니다. 로그를 확인하세요."
    exit 1
fi