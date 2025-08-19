# 🎯 다중 Java 버전 지원 가이드

## 📋 개요

ModpackAI는 이제 **Java 17**과 **Java 21** 모두를 지원하여 다양한 모드팩에서 사용할 수 있습니다.

### 🔧 지원하는 구성

| 모드팩 예시 | 플랫폼 | Java 버전 | JAR 파일명 |
|-------------|--------|-----------|------------|
| enigmatica_10 | NeoForge | 21 | modpackai-neoforge-java21-1.0.0.jar |
| prominence_2 | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |
| all_the_mods_9 | NeoForge | 21 | modpackai-neoforge-java21-1.0.0.jar |
| vault_hunters | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |

---

## 🚀 빠른 시작

### 1. 다중 버전 빌드
```bash
# 모든 Java 버전용 모드를 한 번에 빌드
./build_all_mods_multi_java.sh
```

### 2. 자동 모드팩 선택 및 설치
```bash
# prominence_2 (Fabric, Java 17) 설치
./modpack_selector.sh prominence_2

# enigmatica_10 (NeoForge, Java 21) 설치  
./modpack_selector.sh enigmatica_10

# 모드팩 폴더 직접 지정
./modpack_selector.sh prominence_2 /opt/minecraft/prominence2
```

---

## 🔧 수동 설치 (고급 사용자용)

### Java 17 모드팩 (prominence_2 등)

```bash
# 1. Java 17용 빌드
cd minecraft_fabric_mod
./gradlew build -PtargetJavaVersion=17

# 2. JAR 파일 복사
cp build/libs/modpackai-fabric-*.jar /your/prominence2/mods/
```

### Java 21 모드팩 (enigmatica_10 등)

```bash
# 1. Java 21용 빌드 (기본값)
cd minecraft_mod  
./gradlew build -PtargetJavaVersion=21

# 2. JAR 파일 복사
cp build/libs/modpackai-*.jar /your/enigmatica10/mods/
```

---

## 🏗️ 기술적 세부사항

### 동적 Java 버전 빌드 시스템

프로젝트는 이제 **동적 Java 버전 선택**을 지원합니다:

```gradle
// build.gradle에서 자동으로 Java 버전을 선택
def javaVersion = project.hasProperty('targetJavaVersion') ? 
    project.targetJavaVersion as int : 21

// NeoForge 버전도 자동 선택
def neoforgeVersion = javaVersion == 17 ? '20.4.237' : '21.1.184'
```

### 플랫폼별 호환성 매트릭스

| Platform | Java 17 | Java 21 | Minecraft 버전 |
|----------|---------|---------|----------------|
| **NeoForge** | 20.4.237 | 21.1.184 | 1.20.1 / 1.21.1 |
| **Fabric** | 0.15.11 | 0.15.11 | 1.20.1 |

---

## 📦 빌드 결과물

### 자동 생성되는 JAR 파일들

```
build_output/
├── modpackai-neoforge-java17-1.0.0.jar    # Java 17 NeoForge
├── modpackai-neoforge-java21-1.0.0.jar    # Java 21 NeoForge  
├── modpackai-fabric-java17-1.0.0.jar      # Java 17 Fabric
└── modpackai-fabric-java21-1.0.0.jar      # Java 21 Fabric
```

### 파일 선택 가이드

1. **모드팩의 플랫폼 확인** (NeoForge/Fabric)
2. **Java 버전 요구사항 확인**
3. **해당하는 JAR 파일 선택**

---

## 🛠️ 트러블슈팅

### "Java 버전이 맞지 않습니다" 오류

**문제**: 서버 시작 시 Java 버전 호환성 오류
```
Caused by: java.lang.UnsupportedClassVersionError: 
com/modpackai/ModpackAIMod has been compiled by a more recent version of Java
```

**해결책**:
1. 모드팩의 Java 요구사항 확인
2. 올바른 JAR 파일 사용:
   ```bash
   # prominence_2 (Java 17 필요)
   ./modpack_selector.sh prominence_2
   
   # enigmatica_10 (Java 21 필요)  
   ./modpack_selector.sh enigmatica_10
   ```

### 기존 JAR 파일 충돌

**문제**: 여러 버전의 ModpackAI JAR가 동시 설치됨

**해결책**:
```bash
# 기존 파일 자동 제거 및 새 파일 설치
./modpack_selector.sh <모드팩명>

# 또는 수동 제거
find /your/modpack/mods -name "modpackai*.jar" -delete
```

### 빌드 실패

**문제**: 특정 Java 버전 빌드 실패

**해결책**:
```bash
# 시스템 Java 버전 확인
java -version

# 필요한 경우 Java 17 설치 (Ubuntu/Debian)
sudo apt install openjdk-17-jdk

# JAVA_HOME 환경변수 설정
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

---

## 🎯 모드팩별 권장 설정

### 인기 모드팩 호환성 표

| 모드팩 | 플랫폼 | Java | 권장 JAR |
|--------|--------|------|----------|
| **Enigmatica 10** | NeoForge | 21 | modpackai-neoforge-java21-1.0.0.jar |
| **Prominence II** | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |
| **All The Mods 9** | NeoForge | 21 | modpackai-neoforge-java21-1.0.0.jar |
| **Vault Hunters** | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |
| **Create: Above and Beyond** | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |
| **Better Minecraft** | Fabric | 17 | modpackai-fabric-java17-1.0.0.jar |

### 새로운 모드팩 추가

`modpack_selector.sh`의 모드팩 데이터베이스에 추가:

```bash
# modpack_selector.sh 편집
declare -A MODPACK_DB=(
    # 기존 항목들...
    ["your_new_modpack"]="fabric:17:1.20.1"  # 플랫폼:Java버전:MC버전
)
```

---

## 🔄 업데이트 및 유지보수

### 정기 업데이트

```bash
# 1. 프로젝트 업데이트
git pull origin main

# 2. 새 버전 빌드
./build_all_mods_multi_java.sh

# 3. 활성 모드팩 재설치
./modpack_selector.sh <현재_모드팩>
```

### 버전 관리

- **Java 17 버전**: 구형 모드팩 호환성 유지
- **Java 21 버전**: 최신 모드팩 및 성능 최적화
- **자동 선택**: 모드팩별 최적 버전 자동 감지

---

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/namepix/minecraft-modpack-ai/issues)
- **새 모드팩 요청**: 이슈에 모드팩 정보 포함하여 요청
- **버그 리포트**: Java 버전, 모드팩명, 오류 로그 포함

**⭐ 이 기능이 도움이 되었다면 프로젝트에 스타를 눌러주세요!**