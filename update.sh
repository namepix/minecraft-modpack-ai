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
cp -r $HOME/minecraft-ai-backend $HOME/minecraft-ai-backend.backup.$(date +%Y%m%d_%H%M%S)
echo -e "${GREEN}✅ 백업 완료${NC}"

# 서비스 중지
echo -e "${YELLOW}🛑 서비스 중지 중...${NC}"
sudo systemctl stop mc-ai-backend
echo -e "${GREEN}✅ 서비스 중지됨${NC}"

# 코드 업데이트
echo -e "${YELLOW}🔄 코드 업데이트 중...${NC}"
cp -r backend/* $HOME/minecraft-ai-backend/
cp -r config $HOME/minecraft-ai-backend/
echo -e "${GREEN}✅ 코드 업데이트 완료${NC}"

# 의존성 업데이트
echo -e "${YELLOW}📦 의존성 업데이트 중...${NC}"
cd $HOME/minecraft-ai-backend
source $HOME/minecraft-ai-env/bin/activate
pip install -r requirements.txt --upgrade
echo -e "${GREEN}✅ 의존성 업데이트 완료${NC}"

# 플러그인 재빌드
echo -e "${YELLOW}🔌 플러그인 재빌드 중...${NC}"
cd minecraft_plugin
mvn clean package
# 플러그인은 각 모드팩의 plugins 폴더에 개별적으로 설치되므로 여기서는 빌드만 수행
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
echo "백업 위치: $HOME/minecraft-ai-backend.backup.*"
echo "서버 상태: sudo systemctl status mc-ai-backend"
echo "로그 확인: sudo journalctl -u mc-ai-backend -f" 