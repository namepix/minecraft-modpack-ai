#!/bin/bash
# Fabric 모드 빌드 완전 해결 스크립트 (2025.08.18 최신 버전)
# 이 스크립트는 Fabric 모드 빌드에서 발생하는 모든 주요 문제를 자동으로 해결합니다.

set -euo pipefail

echo "🔧 Fabric 모드 빌드 문제 완전 해결 시작..."
echo "=========================================="

# 프로젝트 루트로 이동 (현재 위치가 어디든 상관없이)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Fabric 모드 디렉토리 확인
if [ ! -d "minecraft_fabric_mod" ]; then
    echo "❌ minecraft_fabric_mod 디렉토리를 찾을 수 없습니다."
    echo "   현재 위치: $(pwd)"
    echo "   프로젝트 루트에서 실행하세요."
    exit 1
fi

cd minecraft_fabric_mod

echo "📋 1단계: 네트워크 연결 확인..."
if curl -I https://maven.fabricmc.net/ &>/dev/null; then
    echo "✅ Fabric Maven 저장소 연결 정상"
else
    echo "⚠️ Fabric Maven 저장소 연결 불가 - 네트워크 설정 확인 필요"
fi

echo ""
echo "🧹 2단계: 기존 빌드 파일 및 캐시 완전 삭제..."
rm -rf .gradle build 
# 사용자 gradle 캐시는 조심스럽게 삭제 (다른 프로젝트에 영향을 줄 수 있음)
rm -rf ~/.gradle/caches/fabric-loom 2>/dev/null || true
rm -f gradlew gradlew.bat
rm -rf gradle/

echo ""
echo "📝 3단계: Fabric Loom 플러그인 버전 자동 수정..."

# build.gradle에서 fabric-loom 버전 확인 및 수정
if grep -q "fabric-loom.*SNAPSHOT" build.gradle; then
    echo "⚠️ SNAPSHOT 버전 발견 - 안정 버전으로 변경합니다..."
    
    # 백업 생성
    cp build.gradle build.gradle.backup
    
    # SNAPSHOT을 안정 버전으로 변경
    sed -i "s/fabric-loom.*version.*'[^']*'/fabric-loom' version '1.5.7'/g" build.gradle
    
    echo "✅ Fabric Loom 버전을 1.5.7로 수정했습니다."
    echo "   백업 파일: build.gradle.backup"
else
    echo "✅ Fabric Loom 버전 설정이 이미 안정적입니다."
fi

echo ""
echo "🚀 4단계: 최신 Gradle Wrapper 생성..."

# 시스템 Gradle 버전 확인
SYSTEM_GRADLE_VERSION=""
if command -v gradle &> /dev/null; then
    SYSTEM_GRADLE_VERSION=$(gradle --version 2>/dev/null | grep "Gradle" | head -1 | grep -o "[0-9]\+\.[0-9]\+" || echo "unknown")
fi

echo "   시스템 Gradle 버전: $SYSTEM_GRADLE_VERSION"

# Gradle 8+ 필요, 시스템 버전이 오래된 경우 다운로드
if [[ "$SYSTEM_GRADLE_VERSION" < "8.0" ]] || [[ "$SYSTEM_GRADLE_VERSION" == "unknown" ]]; then
    echo "⚠️ 시스템 Gradle 버전이 8.0 미만입니다. 최신 Gradle 다운로드 중..."
    
    # 임시 디렉토리에 최신 Gradle 다운로드
    GRADLE_VERSION="8.8"
    GRADLE_URL="https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip"
    
    echo "   다운로드 중: $GRADLE_URL"
    wget -q "$GRADLE_URL" -O /tmp/gradle-${GRADLE_VERSION}-bin.zip
    
    echo "   압축 해제 중..."
    unzip -q /tmp/gradle-${GRADLE_VERSION}-bin.zip -d /tmp
    
    echo "   Gradle Wrapper 생성 중..."
    /tmp/gradle-${GRADLE_VERSION}/bin/gradle wrapper --gradle-version ${GRADLE_VERSION} --distribution-type all
    
    echo "   임시 파일 정리 중..."
    rm -rf /tmp/gradle-${GRADLE_VERSION} /tmp/gradle-${GRADLE_VERSION}-bin.zip
else
    echo "✅ 시스템 Gradle 버전이 충분합니다."
    gradle wrapper --gradle-version 8.8 --distribution-type all
fi

chmod +x ./gradlew

echo ""
echo "🔍 5단계: Gradle 환경 검증..."
echo "   Gradle Wrapper 버전: $(./gradlew --version | grep "Gradle" | head -1 || echo ' 확인 실패')"
echo "   Java 버전: $(java -version 2>&1 | head -1 || echo 'Java 없음')"

echo ""
echo "🔍 6단계: 의존성 해결 테스트..."
if ./gradlew dependencies --configuration compileClasspath --quiet 2>/dev/null; then
    echo "✅ 의존성 해결 성공"
else
    echo "⚠️ 의존성 해결에 문제가 있지만 빌드를 시도합니다..."
fi

echo ""
echo "🔨 7단계: Fabric 모드 빌드 실행..."
echo "   빌드 시작 시간: $(date)"

# 빌드 실행 (상세 로그 출력)
if ./gradlew clean build --refresh-dependencies --info | tee build.log; then
    echo "✅ 빌드 성공!"
else
    echo "❌ 빌드 실패. 로그를 확인하세요:"
    echo "   로그 파일: build.log"
    echo "   마지막 20줄:"
    tail -20 build.log
    exit 1
fi

echo ""
echo "✅ 8단계: 빌드 결과 확인..."
FABRIC_JAR=$(find build/libs -name "modpackai-fabric-*.jar" | head -n1)

if [ -f "$FABRIC_JAR" ]; then
    echo "🎉 Fabric 모드 빌드 성공!"
    echo "📦 빌드된 파일:"
    ls -la build/libs/
    echo ""
    echo "📊 파일 정보:"
    echo "   위치: $(readlink -f "$FABRIC_JAR")"
    echo "   크기: $(ls -lh "$FABRIC_JAR" | awk '{print $5}')"
    echo "   생성시간: $(ls -l "$FABRIC_JAR" | awk '{print $6, $7, $8}')"
else
    echo "❌ 빌드된 JAR 파일을 찾을 수 없습니다."
    echo "📋 build/libs/ 디렉토리 내용:"
    ls -la build/libs/ || echo "   디렉토리가 존재하지 않습니다."
    exit 1
fi

echo ""
echo "🎯 Fabric 모드 빌드 완료!"
echo "=========================="
echo "✅ 다음 단계: 통합 빌드 스크립트(build_all_mods.sh) 실행"
echo "✅ 또는 수동으로 모드팩 mods/ 폴더에 JAR 파일 복사"
echo ""
echo "💡 문제가 재발하는 경우:"
echo "   1. build.gradle 파일의 Fabric Loom 버전을 확인하세요"
echo "   2. 네트워크 연결과 방화벽 설정을 확인하세요"
echo "   3. Java 21+ 버전이 설치되어 있는지 확인하세요"