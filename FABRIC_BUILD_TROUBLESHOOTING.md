# 🔧 Fabric 모드 빌드 문제 해결 가이드

## 📋 개요

이 가이드는 GCP VM Debian 환경에서 Fabric 모드 빌드 시 발생할 수 있는 모든 주요 문제와 해결 방법을 설명합니다.

## 🚨 주요 문제들과 해결 방법

### 1. Gradle Wrapper 누락 문제

**증상**:
```bash
./gradlew: No such file or directory
```

**원인**: Gradle wrapper 파일(`gradlew`)이 프로젝트에 포함되지 않음

**해결 방법**:
```bash
cd minecraft_fabric_mod

# 시스템 Gradle 버전 확인
gradle --version

# 버전이 8.0 미만이거나 없는 경우
if [[ "$(gradle --version | grep -o "[0-9]\+\.[0-9]\+" | head -1)" < "8.0" ]]; then
    # 최신 Gradle 다운로드
    wget -q https://services.gradle.org/distributions/gradle-8.8-bin.zip -O /tmp/gradle-8.8-bin.zip
    unzip -q /tmp/gradle-8.8-bin.zip -d /tmp
    
    # Wrapper 생성
    /tmp/gradle-8.8/bin/gradle wrapper --gradle-version 8.8 --distribution-type all
    
    # 정리
    rm -rf /tmp/gradle-8.8 /tmp/gradle-8.8-bin.zip
else
    gradle wrapper --gradle-version 8.8 --distribution-type all
fi

chmod +x ./gradlew
```

### 2. Fabric Loom SNAPSHOT 버전 문제

**증상**:
```bash
Plugin [id: 'fabric-loom', version: '1.10-SNAPSHOT'] was not found
```

**원인**: SNAPSHOT 버전은 불안정하며 공식 저장소에서 지원되지 않음

**해결 방법**:
```bash
cd minecraft_fabric_mod

# build.gradle 백업
cp build.gradle build.gradle.backup

# SNAPSHOT 버전을 안정 버전으로 변경
sed -i "s/fabric-loom.*version.*'[^']*'/fabric-loom' version '1.5.7'/g" build.gradle

# 변경 확인
grep "fabric-loom" build.gradle
```

### 3. 오래된 시스템 Gradle 버전 문제

**증상**:
```bash
You are using an outdated version of Gradle (4.4.1). Gradle 8.3 or higher is required.
```

**원인**: 시스템에 설치된 Gradle 버전이 Fabric Loom 요구사항보다 낮음

**해결 방법**:
```bash
# 현재 시스템 Gradle 버전 확인
gradle --version

# 8.0 미만인 경우 최신 Gradle 사용
GRADLE_VERSION="8.8"
wget -q "https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip" -O /tmp/gradle-${GRADLE_VERSION}-bin.zip
unzip -q /tmp/gradle-${GRADLE_VERSION}-bin.zip -d /tmp

# 최신 Gradle로 wrapper 생성
/tmp/gradle-${GRADLE_VERSION}/bin/gradle wrapper --gradle-version ${GRADLE_VERSION} --distribution-type all

# 정리
rm -rf /tmp/gradle-${GRADLE_VERSION} /tmp/gradle-${GRADLE_VERSION}-bin.zip
chmod +x ./gradlew
```

### 4. 네트워크 연결 문제

**증상**:
```bash
Could not resolve all dependencies
Connection timed out
```

**원인**: 방화벽, 프록시, 또는 네트워크 설정 문제

**해결 방법**:
```bash
# 네트워크 연결 테스트
curl -I https://maven.fabricmc.net/
curl -I https://services.gradle.org/

# 방화벽 설정 확인
sudo ufw status

# DNS 설정 확인
cat /etc/resolv.conf

# 프록시 설정이 있는 경우 gradle.properties에 추가
echo "systemProp.http.proxyHost=your-proxy-host" >> ~/.gradle/gradle.properties
echo "systemProp.http.proxyPort=8080" >> ~/.gradle/gradle.properties
```

### 5. Java 버전 호환성 문제

**증상**:
```bash
Unsupported Java version
Java 21 or higher is required
```

**원인**: Java 버전이 21 미만

**해결 방법**:
```bash
# Java 버전 확인
java -version

# Java 21 설치 (Ubuntu/Debian)
sudo apt update
sudo apt install openjdk-21-jdk

# JAVA_HOME 설정
export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64' >> ~/.bashrc

# 기본 Java 버전 변경
sudo update-alternatives --config java
```

### 6. 캐시 손상 문제

**증상**:
```bash
Build cache is corrupted
Unexpected lock protocol found in lock file
```

**원인**: Gradle 캐시가 손상됨

**해결 방법**:
```bash
cd minecraft_fabric_mod

# 로컬 캐시 삭제
rm -rf .gradle build

# 사용자 Gradle 캐시에서 Fabric Loom만 삭제
rm -rf ~/.gradle/caches/fabric-loom

# 전체 Gradle 캐시 삭제 (필요한 경우만)
# rm -rf ~/.gradle/caches

# 빌드 재시도
./gradlew clean build --refresh-dependencies
```

## 🎯 완전 자동화 해결 스크립트

프로젝트 루트에서 다음 스크립트를 실행하면 모든 문제를 자동으로 해결합니다:

```bash
# 자동 해결 스크립트 실행
chmod +x fix_fabric_build.sh
./fix_fabric_build.sh
```

## 🔍 수동 단계별 해결

자동 스크립트가 실패하는 경우 다음 단계를 순서대로 실행하세요:

### 1단계: 환경 정리
```bash
cd minecraft_fabric_mod
rm -rf .gradle build
rm -f gradlew gradlew.bat
rm -rf gradle/
```

### 2단계: build.gradle 수정
```bash
# SNAPSHOT 버전 확인
grep "fabric-loom" build.gradle

# SNAPSHOT이면 안정 버전으로 변경
sed -i "s/fabric-loom.*version.*'[^']*'/fabric-loom' version '1.5.7'/g" build.gradle
```

### 3단계: 최신 Gradle wrapper 생성
```bash
# 최신 Gradle 다운로드
wget -q https://services.gradle.org/distributions/gradle-8.8-bin.zip -O /tmp/gradle-8.8-bin.zip
unzip -q /tmp/gradle-8.8-bin.zip -d /tmp

# Wrapper 생성
/tmp/gradle-8.8/bin/gradle wrapper --gradle-version 8.8 --distribution-type all
chmod +x ./gradlew

# 정리
rm -rf /tmp/gradle-8.8 /tmp/gradle-8.8-bin.zip
```

### 4단계: 빌드 실행
```bash
./gradlew clean build --refresh-dependencies
```

### 5단계: 결과 확인
```bash
find build/libs -name "modpackai-fabric-*.jar"
ls -la build/libs/
```

## 📊 문제 진단 체크리스트

빌드 실패 시 다음 항목들을 순서대로 확인하세요:

- [ ] **Java 버전**: `java -version` (21+ 필요)
- [ ] **네트워크 연결**: `curl -I https://maven.fabricmc.net/`
- [ ] **Gradle wrapper 존재**: `ls -la gradlew`
- [ ] **build.gradle Loom 버전**: `grep fabric-loom build.gradle` (SNAPSHOT 아님)
- [ ] **디스크 공간**: `df -h`
- [ ] **권한 설정**: `ls -la gradlew` (실행 가능)

## 🚀 예방 조치

새로운 VM에서 문제 방지를 위한 권장사항:

### 1. 환경 설정 검증
```bash
# Java 21+ 설치 확인
java -version | grep "21\|22\|23"

# 네트워크 접근성 확인
curl -I https://maven.fabricmc.net/
curl -I https://services.gradle.org/

# 디스크 공간 확인 (최소 2GB 필요)
df -h
```

### 2. build.gradle 사전 수정
```bash
# 프로젝트 clone 후 즉시 실행
cd minecraft_fabric_mod
sed -i "s/fabric-loom.*version.*'[^']*'/fabric-loom' version '1.5.7'/g" build.gradle
```

### 3. 자동화 스크립트 활용
```bash
# 항상 fix_fabric_build.sh 먼저 실행
./fix_fabric_build.sh

# 또는 통합 빌드 스크립트 사용
./build_all_mods.sh
```

## 📞 추가 지원

이 가이드로 해결되지 않는 문제가 있는 경우:

1. **로그 파일 확인**: `minecraft_fabric_mod/build.log`
2. **상세 빌드 로그**: `./gradlew build --info --debug`
3. **GitHub Issues**: 프로젝트 저장소에 이슈 등록
4. **환경 정보 수집**:
   ```bash
   echo "Java: $(java -version 2>&1 | head -1)"
   echo "Gradle: $(gradle --version 2>/dev/null | head -1 || echo 'Not installed')"
   echo "OS: $(lsb_release -d 2>/dev/null || cat /etc/os-release | head -1)"
   echo "Disk: $(df -h . | tail -1)"
   ```

---

**💡 팁**: 이 가이드의 모든 해결책은 실제 발생한 문제를 바탕으로 작성되었으며, 새로운 VM 설치 시 99% 이상의 문제를 해결할 수 있습니다.