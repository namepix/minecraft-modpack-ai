# 🛠️ 관리자를 위한 AI 모드 추가 가이드

## 📋 개요

이 가이드는 GCP VM Debian에서 기존 마인크래프트 모드팩 서버에 AI 모드를 추가하는 방법을 설명합니다.

### **현재 구조**
```
/home/username/
├── modpack1/
│   ├── start.sh
│   └── (모드팩 파일들)
├── modpack2/
│   ├── start.sh
│   └── (모드팩 파일들)
└── modpack3/
    ├── start.sh
    └── (모드팩 파일들)
```

### **AI 모드 추가 후 구조**
```
/home/username/
├── modpack1/
│   ├── start.sh
│   ├── plugins/ModpackAI-1.0.jar
│   └── (모드팩 파일들)
├── modpack2/
│   ├── start.sh
│   ├── plugins/ModpackAI-1.0.jar
│   └── (모드팩 파일들)
└── /opt/mc_ai_backend/  # AI 백엔드 (공통)
```

---

## 🚀 1단계: AI 백엔드 설치

### **1.1 프로젝트 다운로드**
```bash
cd ~
git clone https://github.com/your-username/minecraft-modpack-ai.git
cd minecraft-modpack-ai
chmod +x install.sh
```

### **1.2 자동 설치 실행**
```bash
./install.sh
```

### **1.3 API 키 설정**
```bash
nano /opt/mc_ai_backend/.env
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

## 🎮 2단계: 기존 모드팩에 AI 플러그인 추가

### **2.1 플러그인 파일 복사**
각 모드팩 폴더에 AI 플러그인을 추가합니다:

```bash
# 예시: modpack1에 AI 플러그인 추가
cp /opt/minecraft/plugins/ModpackAI-1.0.jar ~/modpack1/plugins/

# 모든 모드팩에 한 번에 추가
for dir in ~/modpack*; do
    if [ -d "$dir" ]; then
        mkdir -p "$dir/plugins"
        cp /opt/minecraft/plugins/ModpackAI-1.0.jar "$dir/plugins/"
        echo "AI 플러그인 추가됨: $dir"
    fi
done
```

### **2.2 플러그인 설정 파일 생성**
각 모드팩 폴더에 설정 파일을 생성합니다:

```bash
# modpack1 예시
cat > ~/modpack1/plugins/ModpackAI/config.yml << EOF
# ModpackAI 설정
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
  name: "modpack1"
  version: "1.0.0"

permissions:
  use: "modpackai.use"
  admin: "modpackai.admin"
EOF
```

### **2.3 모든 모드팩에 설정 자동 생성**
```bash
#!/bin/bash
# setup_all_modpacks.sh

for dir in ~/modpack*; do
    if [ -d "$dir" ]; then
        modpack_name=$(basename "$dir")
        
        # plugins 디렉토리 생성
        mkdir -p "$dir/plugins/ModpackAI"
        
        # 설정 파일 생성
        cat > "$dir/plugins/ModpackAI/config.yml" << EOF
# ModpackAI 설정
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
  name: "$modpack_name"
  version: "1.0.0"

permissions:
  use: "modpackai.use"
  admin: "modpackai.admin"
EOF
        
        echo "설정 완료: $modpack_name"
    fi
done
```

---

## 🔧 3단계: 모드팩별 AI 데이터 설정

### **3.1 모드팩 분석 및 데이터 생성**
각 모드팩의 데이터를 AI 시스템에 등록합니다:

```bash
# 모드팩 파일이 있는 경우
modpack_switch modpack1 1.0.0

# 또는 수동으로 모드팩 분석
curl -X POST http://localhost:5000/api/modpack/analyze \
  -H "Content-Type: application/json" \
  -d '{"modpack_path": "/path/to/modpack1.zip"}'
```

### **3.2 모드팩별 설정 스크립트**
```bash
#!/bin/bash
# setup_modpack_ai.sh

MODPACK_NAME=$1
MODPACK_PATH=$2

if [ -z "$MODPACK_NAME" ] || [ -z "$MODPACK_PATH" ]; then
    echo "사용법: $0 <모드팩명> <모드팩파일경로>"
    exit 1
fi

echo "모드팩 AI 설정 시작: $MODPACK_NAME"

# 1. 모드팩 분석
echo "모드팩 분석 중..."
curl -X POST http://localhost:5000/api/modpack/switch \
  -H "Content-Type: application/json" \
  -d "{
    \"modpack_path\": \"$MODPACK_PATH\",
    \"modpack_name\": \"$MODPACK_NAME\",
    \"modpack_version\": \"1.0.0\"
  }"

# 2. 설정 파일 업데이트
CONFIG_FILE="$HOME/${MODPACK_NAME}/plugins/ModpackAI/config.yml"
if [ -f "$CONFIG_FILE" ]; then
    sed -i "s/modpack_name:.*/modpack_name: \"$MODPACK_NAME\"/" "$CONFIG_FILE"
    echo "설정 파일 업데이트됨: $CONFIG_FILE"
fi

echo "모드팩 AI 설정 완료: $MODPACK_NAME"
```

---

## 🎯 4단계: 서버 시작 스크립트 수정

### **4.1 기존 start.sh 수정**
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

### **4.2 모든 모드팩의 start.sh 자동 수정**
```bash
#!/bin/bash
# update_all_start_scripts.sh

for dir in ~/modpack*; do
    if [ -d "$dir" ]; then
        start_script="$dir/start.sh"
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

# 기존 서버 시작 명령어 (백업에서 복원)
java -Xmx4G -Xms2G -jar server.jar nogui
EOF
            
            chmod +x "$start_script"
            echo "start.sh 업데이트됨: $dir"
        fi
    fi
done
```

---

## 🧪 5단계: 테스트 및 확인

### **5.1 시스템 상태 확인**
```bash
# 백엔드 서비스 상태
sudo systemctl status mc-ai-backend

# API 응답 확인
curl http://localhost:5000/health

# 사용 가능한 모드팩 확인
modpack_switch --list
```

### **5.2 게임 내 테스트**
1. 모드팩 서버 시작
2. 게임에 접속
3. AI 어시스턴트 아이템(네더스타) 획득
4. 우클릭하여 AI 채팅 테스트
5. 명령어 테스트: `/modpackai help`

### **5.3 로그 확인**
```bash
# 백엔드 로그
sudo journalctl -u mc-ai-backend -f

# 플러그인 로그 (게임 내)
# /opt/minecraft/logs/latest.log
```

---

## 🔄 6단계: 모드팩 변경 시 AI 설정

### **6.1 새 모드팩 추가**
```bash
# 1. 새 모드팩 폴더 생성
mkdir ~/newmodpack
cd ~/newmodpack

# 2. AI 플러그인 추가
mkdir -p plugins/ModpackAI
cp /opt/minecraft/plugins/ModpackAI-1.0.jar plugins/

# 3. 설정 파일 생성
# (위의 2.2 단계 참조)

# 4. 모드팩 데이터 등록
modpack_switch newmodpack 1.0.0
```

### **6.2 모드팩 전환**
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
ls -la ~/modpack*/plugins/ModpackAI-1.0.jar

# 권한 수정
chmod 644 ~/modpack*/plugins/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### **API 키 오류**
```bash
# 환경 변수 확인
grep API_KEY /opt/mc_ai_backend/.env

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

---

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 백엔드 서비스가 정상 실행 중인지
2. API 키가 올바르게 설정되었는지
3. 플러그인 파일이 올바른 위치에 있는지
4. 방화벽 설정이 올바른지

**🎮 AI 모드가 성공적으로 추가되었습니다!** 🚀 