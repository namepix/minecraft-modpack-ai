# 🛠️ 관리자를 위한 AI 모드 추가 가이드

## 📋 개요

이 가이드는 GCP VM Debian에서 기존 마인크래프트 모드팩 서버에 AI 모드를 추가하는 방법을 설명합니다.

### **현재 구조**
```
/home/namepix080/
├── enigmatica_10/
│   ├── start-server.sh (또는 다른 스크립트명)
│   ├── mods/
│   │   ├── AE2NetworkAnalyzer-1.21-2.1.0-neoforge.jar
│   │   ├── AI-Improvements-1.21-0.5.3.jar
│   │   └── ... (기존 모드들)
│   ├── config/
│   ├── world/
│   └── ...
├── integrated_MC/
│   ├── start.sh (또는 다른 스크립트명)
│   ├── mods/
│   │   └── ... (기존 모드들)
│   └── ...
├── atm10/
│   ├── [다른 스크립트명]
│   ├── mods/
│   │   └── ... (기존 모드들)
│   └── ...
├── beyond_depth/
├── carpg/
├── cteserver/
├── prominence_2/
├── mnm/
├── test/
└── minecraft-ai-backend/  ← 이미 존재 (선택사항)
```

### **AI 모드 추가 후 구조**
```
/home/namepix080/
├── enigmatica_10/
│   ├── start.sh (통일된 스크립트명)
│   ├── mods/
│   │   ├── AE2NetworkAnalyzer-1.21-2.1.0-neoforge.jar
│   │   ├── AI-Improvements-1.21-0.5.3.jar
│   │   └── ... (기존 모드들)
│   ├── plugins/                    ← 새로 생성
│   │   ├── ModpackAI-1.0.jar      ← AI 플러그인
│   │   └── ModpackAI/             ← 플러그인 설정 폴더
│   │       └── config.yml         ← AI 설정 파일
│   ├── config/
│   ├── world/
│   └── ...
├── integrated_MC/
│   ├── start.sh (통일된 스크립트명)
│   ├── mods/
│   │   └── ... (기존 모드들)
│   ├── plugins/                    ← 새로 생성
│   │   ├── ModpackAI-1.0.jar      ← AI 플러그인
│   │   └── ModpackAI/             ← 플러그인 설정 폴더
│   │       └── config.yml         ← AI 설정 파일
│   └── ...
├── atm10/
│   ├── start.sh (통일된 스크립트명)
│   ├── mods/
│   │   └── ... (기존 모드들)
│   ├── plugins/                    ← 새로 생성
│   │   ├── ModpackAI-1.0.jar      ← AI 플러그인
│   │   └── ModpackAI/             ← 플러그인 설정 폴더
│   │       └── config.yml         ← AI 설정 파일
│   └── ...
├── beyond_depth/
├── carpg/
├── cteserver/
├── prominence_2/
├── mnm/
├── test/
└── minecraft-ai-backend/           ← AI 백엔드 (공통)
    ├── app.py
    ├── models/
    ├── database/
    ├── .env
    └── ...
```

---

## 🚀 1단계: AI 백엔드 설치

### **1.1 프로젝트 다운로드**
```bash
cd ~
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
chmod +x install.sh
```

### **1.2 자동 설치 실행**
```bash
./install.sh
```

### **1.3 API 키 설정**
```bash
nano ~/minecraft-ai-backend/.env
```

**필수 설정**:
```bash
# OpenAI API 키
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic API 키 (선택사항)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Google API 키 (선택사항)
GOOGLE_API_KEY=your-google-api-key

# GCP 설정 (RAG 기능용)
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name
```

### **1.4 백엔드 서비스 시작**
```bash
sudo systemctl start mc-ai-backend
sudo systemctl enable mc-ai-backend
sudo systemctl status mc-ai-backend
```

---

## 🔧 2단계: 시작 스크립트 통일

### **2.1 스크립트명 통일**
모든 모드팩의 시작 스크립트를 `start.sh`로 통일합니다:

```bash
#!/bin/bash
# normalize_start_scripts.sh

# 모드팩 디렉토리 목록
MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e"
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

echo "모드팩 시작 스크립트 통일 작업 시작..."

for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        echo "처리 중: $modpack"
        cd "$HOME/$modpack"
        
        # 기존 start.sh가 있으면 백업
        if [ -f "start.sh" ]; then
            mv start.sh start.sh.backup
        fi
        
        # 가능한 스크립트 파일들 찾기
        if [ -f "start-server.sh" ]; then
            mv start-server.sh start.sh
            echo "  start-server.sh → start.sh"
        elif [ -f "run.sh" ]; then
            mv run.sh start.sh
            echo "  run.sh → start.sh"
        elif [ -f "start.bat" ]; then
            # Windows 배치 파일을 Linux 스크립트로 변환
            echo "#!/bin/bash" > start.sh
            echo "java -jar server.jar nogui" >> start.sh
            chmod +x start.sh
            echo "  start.bat → start.sh (변환됨)"
        else
            echo "  ⚠️ 시작 스크립트를 찾을 수 없음"
        fi
        
        # 실행 권한 부여
        chmod +x start.sh
    else
        echo "⚠️ 디렉토리를 찾을 수 없음: $modpack"
    fi
done

echo "스크립트 통일 작업 완료!"
```

### **2.2 스크립트 실행**
```bash
chmod +x normalize_start_scripts.sh
./normalize_start_scripts.sh
```

---

## 🎮 3단계: 기존 모드팩에 AI 플러그인 추가

### **3.1 플러그인 빌드**
```bash
# AI 백엔드 폴더에서 플러그인 빌드
cd ~/minecraft-ai-backend/minecraft_plugin
mvn clean package

# 빌드된 플러그인 파일 위치: target/ModpackAI-1.0.jar
```

### **3.2 모든 모드팩에 플러그인 자동 설치**
```bash
#!/bin/bash
# setup_all_modpacks.sh

# 모드팩 디렉토리 목록
MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e"
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

echo "모든 모드팩에 AI 플러그인 설치 시작..."

for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        echo "설치 중: $modpack"
        
        # plugins 디렉토리 생성
        mkdir -p "$HOME/$modpack/plugins/ModpackAI"
        
        # 플러그인 파일 복사
        cp ~/minecraft-ai-backend/minecraft_plugin/target/ModpackAI-1.0.jar "$HOME/$modpack/plugins/"
        
        # 설정 파일 생성
        cat > "$HOME/$modpack/plugins/ModpackAI/config.yml" << EOF
backend:
  url: "http://localhost:5000"
  timeout: 30

ai_item:
  material: "NETHER_STAR"
  name: "§6§l모드팩 AI 어시스턴트"
  lore:
    - "§7우클릭하여 AI와 대화하세요"
    - "§7모드팩 관련 질문에 답변해드립니다"

modpack:
  name: "$modpack"
  version: "1.0.0"

permissions:
  use: "modpackai.use"
  admin: "modpackai.admin"
EOF
        
        echo "✅ $modpack 설치 완료"
    else
        echo "⚠️ 디렉토리를 찾을 수 없음: $modpack"
    fi
done

echo "모든 모드팩 설치 완료!"
```

### **3.3 설치 스크립트 실행**
```bash
chmod +x setup_all_modpacks.sh
./setup_all_modpacks.sh
```

---

## 🔧 4단계: 모드팩별 AI 데이터 설정

### **4.1 모드팩 분석 및 데이터 생성**
각 모드팩의 데이터를 AI 시스템에 등록합니다:

```bash
# CLI 스크립트 사용
modpack_switch enigmatica_10 1.0.0
modpack_switch integrated_MC 1.0.0
modpack_switch atm10 1.0.0

# 또는 수동으로 모드팩 분석
curl -X POST http://localhost:5000/api/modpack/analyze \
  -H "Content-Type: application/json" \
  -d '{"modpack_path": "/home/namepix080/enigmatica_10"}'
```

### **4.2 모든 모드팩 자동 분석**
```bash
#!/bin/bash
# analyze_all_modpacks.sh

MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e"
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

echo "모든 모드팩 분석 시작..."

for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        echo "분석 중: $modpack"
        
        # CLI 스크립트로 모드팩 분석
        modpack_switch "$modpack" 1.0.0
        
        echo "✅ $modpack 분석 완료"
    else
        echo "⚠️ 디렉토리를 찾을 수 없음: $modpack"
    fi
done

echo "모든 모드팩 분석 완료!"
```

---

## 🎯 5단계: 서버 시작 스크립트 수정

### **5.1 기존 start.sh 수정**
각 모드팩의 `start.sh` 파일에 AI 백엔드 확인 로직을 추가합니다:

```bash
#!/bin/bash
# start.sh (수정된 버전)

MODPACK_NAME=$(basename $(pwd))
echo "모드팩 서버 시작: $MODPACK_NAME"

# AI 백엔드 상태 확인
echo "AI 백엔드 상태 확인 중..."
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "⚠️  AI 백엔드가 실행되지 않았습니다."
    echo "AI 백엔드를 시작하세요: sudo systemctl start mc-ai-backend"
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ AI 백엔드가 정상 실행 중입니다."
fi

# 기존 서버 시작 명령어
java -Xmx4G -Xms2G -jar server.jar nogui
```

### **5.2 모든 모드팩의 start.sh 자동 수정**
```bash
#!/bin/bash
# update_all_start_scripts.sh

MODPACKS=(
    "enigmatica_10"
    "enigmatica_9e"
    "enigmatica_6"
    "integrated_MC"
    "atm10"
    "beyond_depth"
    "carpg"
    "cteserver"
    "prominence_2"
    "mnm"
    "test"
)

for modpack in "${MODPACKS[@]}"; do
    if [ -d "$HOME/$modpack" ]; then
        start_script="$HOME/$modpack/start.sh"
        if [ -f "$start_script" ]; then
            # 백업 생성
            cp "$start_script" "$start_script.backup"
            
            # AI 백엔드 확인 로직 추가
            cat > "$start_script" << 'EOF'
#!/bin/bash

MODPACK_NAME=$(basename $(pwd))
echo "모드팩 서버 시작: $MODPACK_NAME"

# AI 백엔드 상태 확인
echo "AI 백엔드 상태 확인 중..."
if ! curl -s http://localhost:5000/health > /dev/null; then
    echo "⚠️  AI 백엔드가 실행되지 않았습니다."
    echo "AI 백엔드를 시작하세요: sudo systemctl start mc-ai-backend"
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ AI 백엔드가 정상 실행 중입니다."
fi

# 기존 서버 시작 명령어
java -Xmx4G -Xms2G -jar server.jar nogui
EOF
            
            chmod +x "$start_script"
            echo "start.sh 업데이트됨: $modpack"
        fi
    fi
done
```

---

## 🧪 6단계: 테스트 및 확인

### **6.1 시스템 상태 확인**
```bash
# 백엔드 서비스 상태
sudo systemctl status mc-ai-backend

# API 응답 확인
curl http://localhost:5000/health

# 사용 가능한 모드팩 확인
modpack_switch --list
```

### **6.2 게임 내 테스트**
1. 모드팩 서버 시작
   ```bash
   cd ~/enigmatica_10
   ./start.sh
   ```
2. 게임에 접속
3. AI 어시스턴트 아이템(네더스타) 획득
4. 우클릭하여 AI 채팅 테스트
5. 명령어 테스트: `/modpackai help`

### **6.3 로그 확인**
```bash
# 백엔드 로그
sudo journalctl -u mc-ai-backend -f

# 플러그인 로그 (게임 내)
# 각 모드팩의 logs/latest.log 파일 확인
```

---

## 🔄 7단계: 모드팩 변경 시 AI 설정

### **7.1 새 모드팩 추가**
```bash
# 1. 새 모드팩 폴더 생성
mkdir ~/newmodpack
cd ~/newmodpack

# 2. AI 플러그인 추가
mkdir -p plugins/ModpackAI
cp ~/minecraft-ai-backend/minecraft_plugin/target/ModpackAI-1.0.jar plugins/

# 3. 설정 파일 생성
cat > plugins/ModpackAI/config.yml << EOF
backend:
  url: "http://localhost:5000"
  timeout: 30

ai_item:
  material: "NETHER_STAR"
  name: "§6§l모드팩 AI 어시스턴트"
  lore:
    - "§7우클릭하여 AI와 대화하세요"
    - "§7모드팩 관련 질문에 답변해드립니다"

modpack:
  name: "newmodpack"
  version: "1.0.0"

permissions:
  use: "modpackai.use"
  admin: "modpackai.admin"
EOF

# 4. 모드팩 데이터 등록
modpack_switch newmodpack 1.0.0
```

### **7.2 모드팩 전환**
```bash
# 현재 실행 중인 서버 종료 후
cd ~/newmodpack
./start.sh
```

---

## 🚨 문제 해결

### **AI 백엔드 연결 오류**
```bash
# 서비스 재시작
sudo systemctl restart mc-ai-backend

# 포트 확인
netstat -tlnp | grep 5000

# 방화벽 확인
sudo ufw status
```

### **플러그인 로드 오류**
```bash
# 플러그인 파일 확인
ls -la ~/enigmatica_10/plugins/ModpackAI-1.0.jar
ls -la ~/integrated_MC/plugins/ModpackAI-1.0.jar

# 권한 수정
chmod 644 ~/*/plugins/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### **API 키 오류**
```bash
# 환경 변수 확인
grep API_KEY ~/minecraft-ai-backend/.env

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

### **스크립트 실행 오류**
```bash
# 실행 권한 확인
ls -la ~/enigmatica_10/start.sh
ls -la ~/integrated_MC/start.sh

# 권한 수정
chmod +x ~/*/start.sh
```

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 백엔드 서비스가 정상 실행 중인지
2. API 키가 올바르게 설정되었는지
3. 플러그인 파일이 올바른 위치에 있는지
4. 방화벽 설정이 올바른지
5. 시작 스크립트가 통일되었는지

**🎮 AI 모드가 성공적으로 추가되었습니다!** 🚀 