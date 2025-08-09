#!/usr/bin/env bash
# 준비/빌드 자동화: NeoForge 모드 빌드 환경 준비 + 빌드
# - Gradle 8.10.2 래퍼 생성/사용
# - settings.gradle(.kts) 네오포지 리포지토리 설정 (백업 후 안전 교체)
# - 빌드 실행 및 결과 안내

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $*"; }
ok() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err() { echo -e "${RED}[ERROR]${NC} $*"; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MOD_DIR="$ROOT_DIR/minecraft_mod"

if [[ ! -d "$MOD_DIR" ]]; then
  err "minecraft_mod 디렉토리를 찾을 수 없습니다: $MOD_DIR"
  err "프로젝트 루트를 확인하세요."
  exit 1
fi

log "프로젝트 루트: $ROOT_DIR"
log "모드 디렉토리: $MOD_DIR"

cd "$MOD_DIR"

# 0) 의존 도구
log "필수 패키지 확인(wget, unzip)"
if ! command -v wget >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y wget; fi
if ! command -v unzip >/dev/null 2>&1; then sudo apt-get update && sudo apt-get install -y unzip; fi

# 1) Java 버전 표기(검증용)
if command -v java >/dev/null 2>&1; then
  log "Java 버전:" && java -version || true
else
  warn "java 명령을 찾을 수 없습니다. JDK 17+를 설치하세요."
fi

# 2) settings.gradle(.kts) 구성: NeoForged 저장소 추가 (플러그인 해석 전에 필요)
SETTINGS_GROOVY="settings.gradle"
SETTINGS_KTS="settings.gradle.kts"

NEOFORGED_BLOCK_GROOVY='pluginManagement {\n  repositories {\n    maven { url "https://maven.neoforged.net/releases" }\n    gradlePluginPortal()\n    mavenCentral()\n  }\n  plugins {\n    id "net.neoforged.gradle.userdev" version "7.0.0"\n  }\n}\ndependencyResolutionManagement {\n  repositories {\n    maven { url "https://maven.neoforged.net/releases" }\n    mavenCentral()\n  }\n}\nrootProject.name = "modpackai"\n'

NEOFORGED_BLOCK_KTS='pluginManagement {\n  repositories {\n    maven("https://maven.neoforged.net/releases")\n    gradlePluginPortal()\n    mavenCentral()\n  }\n  plugins {\n    id("net.neoforged.gradle.userdev") version "7.0.0"\n  }\n}\ndependencyResolutionManagement {\n  repositories {\n    maven("https://maven.neoforged.net/releases")\n    mavenCentral()\n  }\n}\nrootProject.name = "modpackai"\n'

ensure_settings_repo() {
  local file="$1"; local block="$2"; local label="$3"
  if [[ -f "$file" ]]; then
    if grep -q "maven\.neoforged\.net" "$file"; then
      ok "$label 이미 설정되어 있음: $file"
      return 0
    fi
    cp "$file" "$file.bak"
    warn "$file 에 NeoForged 저장소가 없어 백업 후 안전 교체합니다 → $file.bak"
  fi
  printf "%b" "$block" > "$file"
  ok "$label 작성 완료: $file"
}

# 강제로 Groovy DSL 사용(이스케이프 문제 회피)
ensure_settings_repo "$SETTINGS_GROOVY" "$NEOFORGED_BLOCK_GROOVY" "settings.gradle"

# 3) Gradle 8.13 준비 및 래퍼 생성/사용 (settings 작성 이후 실행)
GRADLE_VERSION="8.8"
GRADLE_BASE="/opt/gradle/gradle-${GRADLE_VERSION}"
if [[ ! -x "./gradlew" ]]; then
  log "Gradle 래퍼가 없어 임시 Gradle ${GRADLE_VERSION}를 설치합니다. (sudo 필요)"
  if [[ ! -d "$GRADLE_BASE" ]]; then
    sudo mkdir -p /opt/gradle
    wget -q https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -O /tmp/gradle.zip
    sudo unzip -q /tmp/gradle.zip -d /opt/gradle
  fi
  export PATH="$GRADLE_BASE/bin:$PATH"
  log "Gradle 래퍼 생성"
  gradle wrapper --gradle-version "$GRADLE_VERSION"
else
  ok "Gradle 래퍼 발견: ./gradlew"
fi

log "Gradle 버전 확인"
./gradlew --version

# 4) 빌드 실행
log "빌드 시작: clean build (--refresh-dependencies)"
./gradlew --refresh-dependencies clean build

# 5) 결과 표시
log "빌드 결과 파일 목록"
find "$MOD_DIR/build/libs" -maxdepth 1 -type f -name "*.jar" 2>/dev/null | sed 's|.*/||' || true
ok "빌드 완료"

echo "다음 단계: 생성된 JAR를 각 모드팩 mods/ 폴더로 복사하세요."
echo "예: cp $MOD_DIR/build/libs/modpackai-*.jar ~/enigmatica_10/mods/"


