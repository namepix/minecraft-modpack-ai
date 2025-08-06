# 🛠️ 관리자를 위한 AI 모드 추가 가이드

## 📋 개요

이 가이드는 GCP VM Debian에서 기존 마인크래프트 모드팩 서버에 AI 모드를 추가하는 방법을 설명합니다.

### **🎯 설치 방법 선택**

| 방법 | 설명 | 추천도 | 소요시간 |
|------|------|--------|----------|
| **🚀 완전 자동 설치** | 한 번의 명령어로 모든 설치 완료 | ⭐⭐⭐⭐⭐ | 10-15분 |
| **🔧 단계별 설치** | 각 단계를 수동으로 진행 | ⭐⭐⭐ | 20-30분 |

---

## 🚀 방법 1: 완전 자동 설치 (권장)

### **사전 준비사항**
- ✅ GCP VM Debian 서버에 SSH 접속 가능
- ✅ 마인크래프트 모드팩 서버가 이미 설치되어 있음
- ✅ API 키 준비 (OpenAI 필수, Anthropic/Google 선택)

### **1단계: 프로젝트 다운로드**
**터미널에서 다음 명령어를 입력하세요:**

```bash
cd ~
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
```

**설명**: 
- `cd ~` : 홈 디렉토리로 이동
- `git clone` : GitHub에서 프로젝트를 다운로드
- `cd minecraft-modpack-ai` : 다운로드된 프로젝트 폴더로 이동

### **2단계: 완전 자동 설치 실행**
**터미널에서 다음 명령어를 입력하세요:**

```bash
chmod +x install.sh
./install.sh
```

**설명**: 
- `chmod +x install.sh` : 설치 스크립트에 실행 권한을 부여
- `./install.sh` : 설치 스크립트를 실행

**이 스크립트가 자동으로 수행하는 작업:**
- ✅ AI 백엔드 설치 및 설정
- ✅ 플러그인 빌드 (의존성 자동 설치 포함)
- ✅ 시작 스크립트 통일
- ✅ 모든 모드팩에 플러그인 설치
- ✅ API 키 설정 확인
- ✅ 백엔드 서비스 시작
- ✅ 모든 모드팩 AI 분석

### **3단계: API 키 및 GCP 설정 (필수)**
스크립트 실행 중 API 키 설정 안내가 나타납니다. 

**3.1 환경 변수 파일 열기**
**터미널에서 다음 명령어를 입력하세요:**

```bash
nano $HOME/minecraft-ai-backend/.env
```

**3.2 API 키 및 GCP 설정 입력**
**편집기에서 파일 내용을 다음과 같이 수정하세요:**

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Anthropic API 키 (선택)
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key

# Google API 키 (선택)
GOOGLE_API_KEY=your-actual-google-api-key

# GCP 설정 (RAG 기능용, 필수)
GCP_PROJECT_ID=your-actual-gcp-project-id
GCS_BUCKET_NAME=your-actual-gcs-bucket-name
```

**3.3 GCP 설정 방법**
**GCP 프로젝트 ID 확인:**
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 드롭다운에서 프로젝트 ID 확인
3. 또는 `gcloud config get-value project` 명령어로 확인

**GCS 버킷 생성:**
1. [Cloud Storage](https://console.cloud.google.com/storage/browser) 페이지 접속
2. "버킷 만들기" 클릭
3. 버킷 이름 입력 (예: `minecraft-ai-rag-data`)
4. 지역 선택 (예: `us-central1`)
5. "만들기" 클릭

**3.4 파일 저장**
**편집기에서 다음 키를 순서대로 눌러 저장하세요:**
1. `Ctrl + X` (저장 및 종료)
2. `Y` (변경사항 저장 확인)
3. `Enter` (파일명 확인)

**API 키 획득 방법:**
- **OpenAI**: https://platform.openai.com/api-keys 에서 생성
- **Anthropic**: https://console.anthropic.com/ 에서 생성
- **Google**: https://makersuite.google.com/app/apikey 에서 생성

### **4단계: 게임 서버 시작 및 테스트**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 모드팩 서버 시작
cd ~/enigmatica_10
./start.sh
```

**설명**: enigmatica_10 모드팩 서버를 시작합니다.

**게임 내 테스트:**
1. 게임에 접속
2. `/modpackai help` 명령어로 사용법 확인
3. `/give @p nether_star 1` 명령어로 AI 어시스턴트 아이템 획득
4. 네더스타 아이템을 들고 우클릭하여 AI 채팅 테스트

---

## 🔧 방법 2: 단계별 설치

### **사전 준비사항**
- ✅ GCP VM Debian 서버에 SSH 접속 가능
- ✅ 마인크래프트 모드팩 서버가 이미 설치되어 있음
- ✅ API 키 준비 (OpenAI 필수, Anthropic/Google 선택)
- ✅ Java 17 이상 설치됨
- ✅ Maven 설치됨

### **1단계: AI 백엔드 설치**

**1.1 프로젝트 다운로드**
**터미널에서 다음 명령어를 입력하세요:**

```bash
cd ~
git clone https://github.com/namepix/minecraft-modpack-ai.git
cd minecraft-modpack-ai
```

**1.2 자동 설치 실행**
**터미널에서 다음 명령어를 입력하세요:**

```bash
chmod +x install.sh
./install.sh
```

**설명**: 이 스크립트가 AI 백엔드, 데이터베이스, 서비스 등을 모두 설치합니다.

### **2단계: 플러그인 빌드**

**터미널에서 다음 명령어를 입력하세요:**

```bash
cd minecraft_plugin
mvn clean package
cd ..
```

**설명**: 
- `cd minecraft_plugin` : 플러그인 폴더로 이동
- `mvn clean package` : Java 플러그인을 빌드
- `cd ..` : 상위 폴더로 돌아가기

**빌드된 파일 위치**: `minecraft_plugin/target/ModpackAI-1.0.jar`

### **3단계: 시작 스크립트 통일**

**3.1 스크립트 파일 생성**
**터미널에서 다음 명령어를 입력하세요:**

```bash
nano normalize_start_scripts.sh
```

**3.2 스크립트 내용 입력**
**편집기에서 다음 내용을 복사하여 붙여넣으세요:**

```bash
#!/bin/bash

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

**3.3 파일 저장**
**편집기에서 다음 키를 순서대로 눌러 저장하세요:**
1. `Ctrl + X` (저장 및 종료)
2. `Y` (변경사항 저장 확인)
3. `Enter` (파일명 확인)

**3.4 스크립트 실행**
**터미널에서 다음 명령어를 입력하세요:**

```bash
chmod +x normalize_start_scripts.sh
./normalize_start_scripts.sh
```

**설명**: 
- `chmod +x` : 스크립트에 실행 권한 부여
- `./normalize_start_scripts.sh` : 스크립트 실행

### **4단계: 모든 모드팩에 플러그인 설치**

**4.1 스크립트 파일 생성**
**터미널에서 다음 명령어를 입력하세요:**

```bash
nano setup_all_modpacks.sh
```

**4.2 스크립트 내용 입력**
**편집기에서 다음 내용을 복사하여 붙여넣으세요:**

```bash
#!/bin/bash

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
        cp minecraft_plugin/target/ModpackAI-1.0.jar "$HOME/$modpack/plugins/"
        
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

**4.3 파일 저장**
**편집기에서 다음 키를 순서대로 눌러 저장하세요:**
1. `Ctrl + X` (저장 및 종료)
2. `Y` (변경사항 저장 확인)
3. `Enter` (파일명 확인)

**4.4 스크립트 실행**
**터미널에서 다음 명령어를 입력하세요:**

```bash
chmod +x setup_all_modpacks.sh
./setup_all_modpacks.sh
```

### **5단계: API 키 및 GCP 설정**

**5.1 환경 변수 파일 열기**
**터미널에서 다음 명령어를 입력하세요:**

```bash
nano $HOME/minecraft-ai-backend/.env
```

**5.2 API 키 및 GCP 설정 입력**
**편집기에서 파일 내용을 다음과 같이 수정하세요:**

```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Anthropic API 키 (선택)
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-api-key

# Google API 키 (선택)
GOOGLE_API_KEY=your-actual-google-api-key

# GCP 설정 (RAG 기능용, 필수)
GCP_PROJECT_ID=your-actual-gcp-project-id
GCS_BUCKET_NAME=your-actual-gcs-bucket-name
```

**5.3 GCP 설정 방법**
**GCP 프로젝트 ID 확인:**
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 프로젝트 선택 드롭다운에서 프로젝트 ID 확인
3. 또는 `gcloud config get-value project` 명령어로 확인

**GCS 버킷 생성:**
1. [Cloud Storage](https://console.cloud.google.com/storage/browser) 페이지 접속
2. "버킷 만들기" 클릭
3. 버킷 이름 입력 (예: `minecraft-ai-rag-data`)
4. 지역 선택 (예: `us-central1`)
5. "만들기" 클릭

**5.4 파일 저장**
**편집기에서 다음 키를 순서대로 눌러 저장하세요:**
1. `Ctrl + X` (저장 및 종료)
2. `Y` (변경사항 저장 확인)
3. `Enter` (파일명 확인)

### **6단계: 백엔드 서비스 시작**

**터미널에서 다음 명령어를 입력하세요:**

```bash
sudo systemctl start mc-ai-backend
sudo systemctl enable mc-ai-backend
```

**설명**: 
- `sudo systemctl start mc-ai-backend` : AI 백엔드 서비스 시작
- `sudo systemctl enable mc-ai-backend` : 시스템 부팅 시 자동 시작되도록 설정

**서비스 상태 확인:**
```bash
sudo systemctl status mc-ai-backend
```

### **7단계: 모드팩 분석 및 설정**

**7.1 모드팩 파일 업로드**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 모드팩 디렉토리 생성 (이미 생성되어 있을 수 있음)
sudo mkdir -p /tmp/modpacks
sudo chmod 755 /tmp/modpacks
```

**모드팩 파일을 `/tmp/modpacks/` 디렉토리에 업로드하세요:**
- **SCP 사용**: `scp your-modpack.zip username@server-ip:/tmp/modpacks/`
- **SFTP 사용**: 파일을 `/tmp/modpacks/` 디렉토리에 업로드
- **직접 복사**: USB나 다른 방법으로 파일을 서버에 복사

**7.2 모드팩 분석 실행**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 방법 1: 설정 파일에서 모드팩 정보 읽어서 분석
modpack_switch

# 방법 2: 특정 모드팩 분석 (버전 자동 추출)
modpack_switch CreateModpack

# 방법 3: 특정 모드팩과 버전으로 분석
modpack_switch FTBRevelation 1.0.0

# 사용 가능한 모드팩 목록 확인
modpack_switch --list
```

**설명**: 
- **방법 1**: `.env` 파일의 `CURRENT_MODPACK_NAME`과 `CURRENT_MODPACK_VERSION`을 읽어서 분석
- **방법 2**: 파일명에서 버전을 자동으로 추출 시도 (실패 시 기본값 1.0 사용)
- **방법 3**: 사용자가 지정한 버전으로 분석

**7.3 분석 결과 확인**
**분석이 완료되면 다음과 같은 정보가 표시됩니다:**

```
📊 분석 결과:
  🎮 모드팩: CreateModpack v1.0.0
  📦 모드 수: 150
  🛠️ 제작법 수: 2500
  🎯 아이템 수: 3000
  🌐 언어 매핑: 500개 추가
```

**설정 파일이 자동으로 업데이트되어 다음 분석부터는 `modpack_switch`만 입력하면 됩니다.**

---

## 📁 설치 후 파일 구조

### **현재 구조 (설치 전)**
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

### **설치 후 구조**
```
/home/namepix080/
├── enigmatica_10/
│   ├── start.sh                    ← 통일된 스크립트명
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
│   ├── start.sh                    ← 통일된 스크립트명
│   ├── mods/
│   │   └── ... (기존 모드들)
│   ├── plugins/                    ← 새로 생성
│   │   ├── ModpackAI-1.0.jar      ← AI 플러그인
│   │   └── ModpackAI/             ← 플러그인 설정 폴더
│   │       └── config.yml         ← AI 설정 파일
│   └── ...
├── atm10/
│   ├── start.sh                    ← 통일된 스크립트명
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

## 🎮 게임 내 사용법

### **기본 명령어**
**게임 내에서 다음 명령어를 입력하세요:**

```bash
/modpackai help          # 도움말 보기
/modpackai chat          # AI 채팅 GUI 열기
/modpackai recipe <아이템> # 제작법 조회
/modpackai models        # AI 모델 선택
/modpackai current       # 현재 AI 모델 정보
```

### **AI 어시스턴트 아이템**
- **아이템**: 네더스타 (Nether Star)
- **획득 방법**: 게임 내에서 `/give @p nether_star 1` 명령어 입력
- **사용법**: 아이템을 들고 우클릭

### **GUI 구성**
- **왼쪽**: 3x3 제작법 표시 영역
- **오른쪽**: AI 채팅 영역
- **하단**: AI 모델 선택 버튼

---

## 🔧 관리자 도구

### **시스템 모니터링**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 시스템 상태 확인
./monitor.sh

# 백엔드 서비스 상태
sudo systemctl status mc-ai-backend

# 로그 확인
sudo journalctl -u mc-ai-backend -f
```

### **모드팩 변경**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 모드팩 변경
modpack_switch enigmatica_10 1.0.0

# 사용 가능한 모드팩 목록
modpack_switch --list
```

### **업데이트**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 시스템 업데이트
./update.sh
```

---

## 🚨 문제 해결

### **백엔드 서비스 오류**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 서비스 재시작
sudo systemctl restart mc-ai-backend

# 로그 확인
sudo journalctl -u mc-ai-backend -f

# 포트 확인
netstat -tlnp | grep 5000
```

### **플러그인 로드 오류**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 플러그인 파일 확인
ls -la ~/enigmatica_10/plugins/ModpackAI-1.0.jar

# 권한 수정
chmod 644 ~/*/plugins/ModpackAI-1.0.jar

# Java 버전 확인
java -version
```

### **API 키 오류**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 환경 변수 확인
grep API_KEY $HOME/minecraft-ai-backend/.env

# 서비스 재시작
sudo systemctl restart mc-ai-backend
```

### **스크립트 실행 오류**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 실행 권한 확인
ls -la ~/enigmatica_10/start.sh

# 권한 수정
chmod +x ~/*/start.sh
```

### **RAG 시스템 오류**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# GCP 설정 확인
grep GCP $HOME/minecraft-ai-backend/.env

# GCP 프로젝트 연결 확인
gcloud auth list

# GCS 버킷 접근 확인
gsutil ls gs://your-bucket-name

# RAG 서비스 상태 확인
sudo journalctl -u mc-ai-backend | grep RAG
```

**일반적인 RAG 오류:**
- **GCP_PROJECT_ID 누락**: Google Cloud Console에서 프로젝트 ID 확인
- **GCS_BUCKET_NAME 누락**: Cloud Storage에서 버킷 생성
- **권한 오류**: GCP 서비스 계정에 Storage 권한 부여
- **네트워크 오류**: GCP API 활성화 확인

---

## 📞 지원

### **문제 발생 시 확인사항**
1. ✅ 백엔드 서비스가 정상 실행 중인지
2. ✅ API 키가 올바르게 설정되었는지
3. ✅ GCP 설정이 올바르게 되어 있는지
4. ✅ GCS 버킷에 접근할 수 있는지
5. ✅ 플러그인 파일이 올바른 위치에 있는지
6. ✅ 시작 스크립트가 통일되었는지
7. ✅ 방화벽 설정이 올바른지

### **로그 확인**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 백엔드 로그
sudo journalctl -u mc-ai-backend -f

# RAG 관련 로그만 확인
sudo journalctl -u mc-ai-backend | grep -i rag

# 게임 서버 로그
tail -f ~/enigmatica_10/logs/latest.log
```

### **시스템 정보**
**터미널에서 다음 명령어를 입력하세요:**

```bash
# 시스템 상태
./monitor.sh

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

---

## 🎯 설치 체크리스트

### **사전 준비**
- [ ] GCP VM Debian 환경
- [ ] 마인크래프트 모드팩 서버 실행 중
- [ ] API 키 준비 (OpenAI, Anthropic, Google)
- [ ] GCP 프로젝트 ID 확인
- [ ] GCS 버킷 생성 완료

### **설치 과정**
- [ ] 프로젝트 다운로드
- [ ] 완전 자동 설치 실행 (또는 단계별 설치)
- [ ] API 키 설정
- [ ] GCP 설정 (프로젝트 ID, 버킷 이름)
- [ ] 백엔드 서비스 시작
- [ ] 모드팩 분석 완료

### **테스트**
- [ ] 게임 서버 시작
- [ ] AI 명령어 테스트 (`/modpackai help`)
- [ ] AI 채팅 테스트 (네더스타 아이템)
- [ ] 제작법 조회 테스트

---

## 📝 중요 참고사항

### **스크립트 파일 생성 방법**
1. **터미널에서 `nano 파일명.sh` 입력**
2. **편집기에서 코드 복사-붙여넣기**
3. **Ctrl+X, Y, Enter로 저장**
4. **`chmod +x 파일명.sh`로 실행 권한 부여**
5. **`./파일명.sh`로 스크립트 실행**

### **API 키 설정 방법**

**🌟 우선순위: Gemini Pro (메인 모델)**
1. **Google AI Studio (ai.google.dev)에서 API 키 생성** ⭐ 최우선 설정
2. **GCP VM과 동일한 Google 계정 사용 (무료 크레딧 활용)**

**📖 백업 모델들 (선택사항)**
3. **OpenAI (platform.openai.com)** - 무료 티어 사용
4. **Anthropic (console.anthropic.com)** - 무료 티어 사용

**설정 방법:**
1. **`nano $HOME/minecraft-ai-backend/.env`로 파일 열기**
2. **실제 API 키로 교체 (특히 GOOGLE_API_KEY는 필수)**
3. **Ctrl+X, Y, Enter로 저장**

**💡 참고**: Gemini Pro가 기본 모델이므로 GOOGLE_API_KEY만 설정해도 기본 동작합니다!

### **파일 편집기 사용법**
- **nano**: 간단한 텍스트 편집기
- **Ctrl+X**: 저장 및 종료
- **Y**: 변경사항 저장 확인
- **Enter**: 파일명 확인

---

**🎮 AI 모드가 성공적으로 추가되었습니다!** 🚀

이제 게임 내에서 AI 어시스턴트와 함께 즐거운 모드팩 플레이를 즐기세요! 