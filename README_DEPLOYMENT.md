# 🚀 GCP VM 배포 및 업데이트 가이드

이 가이드는 로컬에서 개발한 마인크래프트 AI 시스템을 GCP VM에 배포하고, 이후 로컬 수정사항을 간단하게 VM에 반영하는 방법을 설명합니다.

## 📋 사전 준비사항

### 1. GCP VM 설정
- **VM 인스턴스**: Debian 11 또는 Ubuntu 20.04+
- **최소 사양**: 2 vCPU, 4GB RAM, 20GB SSD
- **권장 사양**: 4 vCPU, 8GB RAM, 40GB SSD
- **방화벽**: 포트 5000 (HTTP), 22 (SSH) 개방

### 2. 로컬 환경 요구사항
- Git
- Java 17+ (Maven)
- Python 3.8+
- SSH 키 쌍 (GCP VM 접속용)

### 3. API 키 준비
- **Google API Key** (Gemini 2.5 Pro, 필수)
- **OpenAI API Key** (GPT, 선택)
- **Anthropic API Key** (Claude, 선택)

## 🔧 초기 배포 설정

### 1. 배포 설정 파일 생성

```bash
# deploy.config.example을 복사
cp deploy.config.example deploy.config

# 실제 환경에 맞게 수정
nano deploy.config
```

**deploy.config 예시:**
```bash
GCP_VM_IP="34.123.45.67"
GCP_VM_USER="john"
GCP_VM_PROJECT_PATH="/home/john/mc_ai"
SSH_KEY_PATH="~/.ssh/gcp_key"
MC_SERVER_PLUGINS_DIR="/opt/minecraft/plugins"  # 선택사항
```

### 2. SSH 키 설정 (GCP VM 접속용)

```bash
# 새 SSH 키 생성 (필요한 경우)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/gcp_key

# 공개 키를 GCP VM에 추가
# GCP Console -> Compute Engine -> Metadata -> SSH Keys에서 추가
cat ~/.ssh/gcp_key.pub
```

### 3. GCP VM에 기본 패키지 설치

GCP VM에 SSH로 접속하여 필요한 패키지를 설치합니다:

```bash
# VM에 접속
ssh -i ~/.ssh/gcp_key username@your-vm-ip

# 패키지 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Java 17 설치 (OpenJDK)
sudo apt install -y openjdk-17-jdk

# Maven 설치
sudo apt install -y maven

# 시스템 모니터링 도구 설치
sudo apt install -y htop nethogs iotop
```

## 🚀 초기 배포 실행

### 1. 배포 스크립트 실행

```bash
# 배포 스크립트에 실행 권한 부여
chmod +x deploy.sh

# 초기 배포 실행
./deploy.sh
```

배포 스크립트는 다음 작업을 수행합니다:
1. SSH 연결 테스트
2. 로컬 파일 변경사항 확인
3. Java 플러그인 빌드
4. Python 백엔드 테스트
5. 프로젝트 파일 압축 및 업로드
6. GCP VM에서 배포 실행
7. Python 가상환경 설정
8. systemd 서비스 등록 및 시작

### 2. 배포 후 확인

```bash
# VM에서 서비스 상태 확인
ssh -i ~/.ssh/gcp_key username@vm-ip
sudo systemctl status mc-ai-backend

# API 테스트
curl http://localhost:5000/health

# 로그 확인
sudo journalctl -u mc-ai-backend -f
```

## 🔄 업데이트 방법

로컬에서 코드를 수정한 후 GCP VM에 반영하는 방법입니다.

### 1. 빠른 업데이트 (권장)

```bash
# 업데이트 스크립트에 실행 권한 부여
chmod +x update.sh

# 전체 업데이트
./update.sh

# 백엔드만 업데이트
./update.sh backend

# 플러그인만 업데이트  
./update.sh plugin
```

### 2. 수동 업데이트

**백엔드만 업데이트:**
```bash
# 백엔드 파일 압축
tar czf backend_update.tar.gz --exclude="__pycache__" --exclude="*.pyc" --exclude="venv" backend/

# VM에 업로드
scp -i ~/.ssh/gcp_key backend_update.tar.gz username@vm-ip:/tmp/

# VM에서 업데이트 실행
ssh -i ~/.ssh/gcp_key username@vm-ip "
    cd /home/username/mc_ai &&
    sudo systemctl stop mc-ai-backend &&
    tar xzf /tmp/backend_update.tar.gz &&
    cd backend && source venv/bin/activate && pip install -r requirements.txt &&
    sudo systemctl start mc-ai-backend
"
```

**플러그인만 업데이트:**
```bash
# 로컬에서 플러그인 빌드
cd minecraft_plugin
mvn clean package

# 빌드된 JAR 파일을 VM에 복사
scp -i ~/.ssh/gcp_key target/modpack-ai-plugin-1.0.0.jar username@vm-ip:/opt/minecraft/plugins/
```

## 🛠️ 환경변수 설정

VM의 `.env` 파일을 수정하여 API 키를 설정합니다:

```bash
# VM에 접속
ssh -i ~/.ssh/gcp_key username@vm-ip

# .env 파일 편집
cd /home/username/mc_ai/backend
nano .env
```

**.env 파일 내용:**
```bash
# 필수 - Google Gemini API (웹검색 지원)
GOOGLE_API_KEY=your-google-api-key

# 선택사항 - 백업 AI 모델들
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# RAG 시스템 (선택사항)
GCP_PROJECT_ID=your-gcp-project
GCS_BUCKET_NAME=your-gcs-bucket
```

## 📊 모니터링 및 로그

### 1. 시스템 상태 확인

```bash
# 서비스 상태
sudo systemctl status mc-ai-backend

# 실시간 로그
sudo journalctl -u mc-ai-backend -f

# 시스템 리소스
htop

# API 상태 확인
curl http://localhost:5000/health
curl http://localhost:5000/metrics
```

### 2. 성능 모니터링

새로 추가된 모니터링 엔드포인트:
```bash
# 기본 헬스체크
curl http://localhost:5000/health

# 상세 메트릭
curl http://localhost:5000/metrics

# 성능 보고서
curl http://localhost:5000/health/detailed
```

## 🚨 문제 해결

### 1. 일반적인 문제

**서비스가 시작되지 않는 경우:**
```bash
# 자세한 로그 확인
sudo journalctl -u mc-ai-backend -n 50

# 서비스 재시작
sudo systemctl restart mc-ai-backend

# Python 가상환경 재생성
cd /home/username/mc_ai/backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**API 키 오류:**
```bash
# .env 파일 확인
cat /home/username/mc_ai/backend/.env

# 환경변수 테스트
cd /home/username/mc_ai/backend
source venv/bin/activate
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"
```

### 2. 성능 최적화

**메모리 사용량이 높은 경우:**
```bash
# Python 프로세스 확인
ps aux | grep python

# 메모리 사용량 모니터링
free -h

# 로그 파일 정리
sudo journalctl --vacuum-time=7d
```

**응답이 느린 경우:**
```bash
# 네트워크 상태 확인
ping google.com

# CPU 사용량 확인
top

# API 응답 시간 테스트
time curl http://localhost:5000/health
```

## 🔒 보안 설정

### 1. 방화벽 설정

```bash
# ufw 방화벽 설정
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 5000/tcp  # API 서버
sudo ufw status
```

### 2. SSL/TLS 설정 (권장)

```bash
# Certbot 설치 (Let's Encrypt)
sudo apt install -y certbot

# SSL 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# Nginx 프록시 설정 (선택사항)
sudo apt install -y nginx
```

## 📝 정기 유지보수

### 1. 일일 점검사항
- 서비스 상태 확인: `sudo systemctl status mc-ai-backend`
- 로그 점검: `sudo journalctl -u mc-ai-backend --since="1 day ago"`
- 리소스 사용량: `htop`, `df -h`

### 2. 주간 작업
- 시스템 업데이트: `sudo apt update && sudo apt upgrade`
- 로그 파일 정리: `sudo journalctl --vacuum-time=7d`
- 백업 확인: `ls -la ~/mc_ai_backups/`

### 3. 월간 작업
- API 사용량 분석
- 성능 메트릭 리뷰
- 보안 업데이트 적용

이제 로컬에서 개발하고 `./update.sh`로 간단하게 배포할 수 있습니다! 🎉