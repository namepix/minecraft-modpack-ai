#!/bin/bash
# ModpackAI 완전 정리 스크립트
# 기존 설치 흔적을 모두 제거하여 깔끔한 재설치 준비

set -e

echo "🧹 ModpackAI 설치 흔적 완전 정리 시작..."
echo "================================================"

# 현재 사용자 확인
CURRENT_USER=$(whoami)
echo "👤 현재 사용자: $CURRENT_USER"

# 1. 백엔드 서비스 중지 및 제거
echo ""
echo "🛑 1. 백엔드 서비스 중지 및 제거"
echo "--------------------------------"

# systemd 서비스 중지
if systemctl is-active --quiet mc-ai-backend 2>/dev/null; then
    echo "  ⏹️ mc-ai-backend 서비스 중지 중..."
    sudo systemctl stop mc-ai-backend || true
    echo "  ✅ 서비스 중지 완료"
else
    echo "  ℹ️ mc-ai-backend 서비스가 실행 중이 아님"
fi

# systemd 서비스 비활성화
if systemctl is-enabled --quiet mc-ai-backend 2>/dev/null; then
    echo "  ❌ mc-ai-backend 서비스 비활성화 중..."
    sudo systemctl disable mc-ai-backend || true
    echo "  ✅ 서비스 비활성화 완료"
else
    echo "  ℹ️ mc-ai-backend 서비스가 활성화되어 있지 않음"
fi

# systemd 서비스 파일 제거
if [ -f "/etc/systemd/system/mc-ai-backend.service" ]; then
    echo "  🗑️ systemd 서비스 파일 제거 중..."
    sudo rm -f /etc/systemd/system/mc-ai-backend.service
    sudo systemctl daemon-reload
    echo "  ✅ 서비스 파일 제거 완료"
else
    echo "  ℹ️ systemd 서비스 파일 없음"
fi

# 2. 백엔드 디렉토리 제거
echo ""
echo "🗂️ 2. 백엔드 설치 디렉토리 제거"
echo "-------------------------------"

BACKEND_DIRS=(
    "$HOME/minecraft-ai-backend"
    "$HOME/minecraft-modpack-ai-backend"
    "$HOME/mc-ai-backend"
    "$HOME/.minecraft-ai"
)

for dir in "${BACKEND_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  🗑️ 제거 중: $dir"
        rm -rf "$dir"
        echo "  ✅ 제거 완료: $dir"
    else
        echo "  ℹ️ 디렉토리 없음: $dir"
    fi
done

# 3. 프로젝트 디렉토리 내 빌드 파일 정리
echo ""
echo "🔨 3. 프로젝트 빌드 파일 정리"
echo "----------------------------"

PROJECT_DIR="$HOME/minecraft-modpack-ai"
if [ -d "$PROJECT_DIR" ]; then
    echo "  📁 프로젝트 디렉토리: $PROJECT_DIR"
    
    cd "$PROJECT_DIR"
    
    # NeoForge 모드 빌드 파일 정리
    if [ -d "minecraft_mod" ]; then
        echo "  🧹 NeoForge 모드 빌드 파일 정리..."
        cd minecraft_mod
        [ -d "build" ] && rm -rf build && echo "    ✅ build/ 디렉토리 제거"
        [ -d ".gradle" ] && rm -rf .gradle && echo "    ✅ .gradle/ 디렉토리 제거"
        [ -f "gradlew" ] && rm -f gradlew && echo "    ✅ gradlew 제거"
        [ -f "gradlew.bat" ] && rm -f gradlew.bat && echo "    ✅ gradlew.bat 제거"
        [ -d "gradle" ] && rm -rf gradle && echo "    ✅ gradle/ 디렉토리 제거"
        cd ..
    fi
    
    # Fabric 모드 빌드 파일 정리
    if [ -d "minecraft_fabric_mod" ]; then
        echo "  🧹 Fabric 모드 빌드 파일 정리..."
        cd minecraft_fabric_mod
        [ -d "build" ] && rm -rf build && echo "    ✅ build/ 디렉토리 제거"
        [ -d ".gradle" ] && rm -rf .gradle && echo "    ✅ .gradle/ 디렉토리 제거"
        [ -f "gradlew" ] && rm -f gradlew && echo "    ✅ gradlew 제거"
        [ -f "gradlew.bat" ] && rm -f gradlew.bat && echo "    ✅ gradlew.bat 제거"
        [ -d "gradle" ] && rm -rf gradle && echo "    ✅ gradle/ 디렉토리 제거"
        cd ..
    fi
    
    # 백엔드 가상환경 정리
    if [ -d "backend/venv" ]; then
        echo "  🐍 백엔드 가상환경 제거..."
        rm -rf backend/venv
        echo "    ✅ backend/venv 제거 완료"
    fi
    
    # 빌드 결과물 디렉토리 정리
    [ -d "build_output" ] && rm -rf build_output && echo "  ✅ build_output/ 디렉토리 제거"
    
else
    echo "  ⚠️ 프로젝트 디렉토리 없음: $PROJECT_DIR"
fi

# 4. 모드팩에서 기존 ModpackAI 모드 제거
echo ""
echo "🎮 4. 모드팩에서 기존 ModpackAI 모드 제거"
echo "--------------------------------------"

echo "  🔍 모드팩 디렉토리 검색 중..."
MODPACK_COUNT=0
while IFS= read -r -d '' mods_dir; do
    modpack_dir=$(dirname "$mods_dir")
    modpack_name=$(basename "$modpack_dir")
    
    # ModpackAI 모드 파일 찾기
    MODPACKAI_JARS=$(find "$mods_dir" -name "modpackai*.jar" 2>/dev/null || true)
    
    if [ -n "$MODPACKAI_JARS" ]; then
        echo "  📦 $modpack_name 에서 ModpackAI 모드 제거 중..."
        echo "$MODPACKAI_JARS" | while read -r jar_file; do
            if [ -f "$jar_file" ]; then
                rm -f "$jar_file"
                echo "    🗑️ 제거: $(basename "$jar_file")"
            fi
        done
        ((MODPACK_COUNT++))
    fi
done < <(find "$HOME" -maxdepth 3 -type d -name "mods" -print0 2>/dev/null || true)

echo "  📊 총 $MODPACK_COUNT 개 모드팩에서 ModpackAI 모드 제거 완료"

# 5. 임시 파일 정리
echo ""
echo "🗑️ 5. 임시 파일 정리"
echo "------------------"

TEMP_FILES=(
    "/tmp/gradle-*.zip"
    "/tmp/gradle-*/"
    "/tmp/modpackai-*"
)

for pattern in "${TEMP_FILES[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "  🧹 정리 중: $pattern"
        rm -rf $pattern
        echo "  ✅ 정리 완료: $pattern"
    else
        echo "  ℹ️ 파일 없음: $pattern"
    fi
done

# 6. 환경 변수 정리 (선택적)
echo ""
echo "🌍 6. 환경 변수 정리 (선택적)"
echo "----------------------------"

ENV_FILES=(
    "$HOME/.bashrc"
    "$HOME/.profile"
    "$HOME/.zshrc"
)

for env_file in "${ENV_FILES[@]}"; do
    if [ -f "$env_file" ]; then
        # ModpackAI 관련 환경 변수 백업 및 제거
        if grep -q "minecraft.*ai\|modpack.*ai\|MODPACK_AI" "$env_file" 2>/dev/null; then
            echo "  📝 $env_file 에서 ModpackAI 관련 설정 제거 중..."
            cp "$env_file" "${env_file}.backup.$(date +%Y%m%d_%H%M%S)"
            grep -v "minecraft.*ai\|modpack.*ai\|MODPACK_AI" "$env_file" > "${env_file}.tmp" && mv "${env_file}.tmp" "$env_file"
            echo "  ✅ 환경 변수 정리 완료 (백업: ${env_file}.backup.*)"
        else
            echo "  ℹ️ $env_file 에 ModpackAI 관련 설정 없음"
        fi
    fi
done

# 7. 포트 정리 (선택적)
echo ""
echo "🔌 7. 포트 5000 사용 프로세스 확인"
echo "-------------------------------"

PORT_5000_PROCESS=$(netstat -tlnp 2>/dev/null | grep ":5000 " | awk '{print $7}' | head -1)
if [ -n "$PORT_5000_PROCESS" ]; then
    echo "  ⚠️ 포트 5000 사용 중인 프로세스: $PORT_5000_PROCESS"
    echo "  💡 필요시 수동으로 종료: sudo kill -9 $(echo $PORT_5000_PROCESS | cut -d'/' -f1)"
else
    echo "  ✅ 포트 5000 사용 프로세스 없음"
fi

# 8. 정리 완료 확인
echo ""
echo "✅ 8. 정리 완료 확인"
echo "==================="

echo "  🔍 남은 ModpackAI 관련 파일 검색..."
REMAINING_FILES=$(find "$HOME" -name "*modpackai*" -o -name "*minecraft-ai*" 2>/dev/null | grep -v ".git" | head -10)

if [ -n "$REMAINING_FILES" ]; then
    echo "  ⚠️ 남은 파일들 (확인 필요):"
    echo "$REMAINING_FILES"
else
    echo "  ✅ 모든 ModpackAI 관련 파일 정리 완료"
fi

echo ""
echo "🎉 ModpackAI 설치 흔적 완전 정리 완료!"
echo "======================================="
echo ""
echo "📋 정리 요약:"
echo "  ✅ systemd 서비스 중지 및 제거"
echo "  ✅ 백엔드 디렉토리 제거"
echo "  ✅ 빌드 파일 및 캐시 정리"
echo "  ✅ 모드팩에서 ModpackAI 모드 제거 ($MODPACK_COUNT 개)"
echo "  ✅ 임시 파일 정리"
echo "  ✅ 환경 변수 정리"
echo ""
echo "🚀 이제 깔끔한 환경에서 대화형 설치를 시작할 수 있습니다!"
echo ""
echo "다음 단계:"
echo "  1. 터미널 재시작 (환경 변수 적용)"
echo "  2. 프로젝트 디렉토리로 이동: cd ~/minecraft-modpack-ai"
echo "  3. 대화형 설치 시작"