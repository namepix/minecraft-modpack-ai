#!/bin/bash

# Minecraft Modpack AI Assistant 업데이트 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Minecraft Modpack AI Assistant 업데이트 ===${NC}"
echo ""

# 백업 생성
echo -e "${YELLOW}📦 백업 생성 중...${NC}"
sudo cp -r /opt/mc_ai_backend /opt/mc_ai_backend.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✅ 백업 완료${NC}"

# 서비스 중지
echo -e "${YELLOW}🛑 서비스 중지 중...${NC}"
sudo systemctl stop mc-ai-backend
echo -e "${GREEN}✅ 서비스 중지됨${NC}"

# 코드 업데이트
echo -e "${YELLOW}🔄 코드 업데이트 중...${NC}"
cp -r backend/* /opt/mc_ai_backend/
cp -r config /opt/mc_ai_backend/
echo -e "${GREEN}✅ 코드 업데이트 완료${NC}"

# 의존성 업데이트
echo -e "${YELLOW}📦 의존성 업데이트 중...${NC}"
cd /opt/mc_ai_backend
source /opt/mc_ai_env/bin/activate
pip install -r requirements.txt --upgrade
echo -e "${GREEN}✅ 의존성 업데이트 완료${NC}"

# 플러그인 재빌드
echo -e "${YELLOW}🔌 플러그인 재빌드 중...${NC}"
cd minecraft_plugin
mvn clean package
sudo cp target/ModpackAI-1.0.jar /opt/minecraft/plugins/
echo -e "${GREEN}✅ 플러그인 업데이트 완료${NC}"

# 서비스 재시작
echo -e "${YELLOW}🚀 서비스 재시작 중...${NC}"
sudo systemctl daemon-reload
sudo systemctl start mc-ai-backend
echo -e "${GREEN}✅ 서비스 재시작됨${NC}"

# 상태 확인
echo -e "${YELLOW}🔍 상태 확인 중...${NC}"
sleep 3
if systemctl is-active --quiet mc-ai-backend; then
    echo -e "${GREEN}✅ 업데이트 성공!${NC}"
else
    echo -e "${RED}❌ 업데이트 실패 - 로그를 확인하세요${NC}"
    sudo journalctl -u mc-ai-backend -n 10
fi

echo ""
echo -e "${BLUE}=== 업데이트 완료 ===${NC}"
echo "백업 위치: /opt/mc_ai_backend.backup.*"
echo "서버 상태: sudo systemctl status mc-ai-backend"
echo "로그 확인: sudo journalctl -u mc-ai-backend -f" 