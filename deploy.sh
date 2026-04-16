#!/bin/bash
# AICS 部署脚本
# 部署到服务器 47.243.159.224

set -e

# 配置变量
SERVER_IP="47.243.159.224"
SERVER_USER="root"
DEPLOY_DIR="/opt/aics"
REPO_URL="https://github.com/weisili08/hfcc_work.git"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  AICS 部署脚本${NC}"
echo -e "${BLUE}  目标服务器: ${SERVER_IP}${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# 检查 SSH 连接
echo -e "${YELLOW}[1/6] 检查 SSH 连接...${NC}"
if ssh -o ConnectTimeout=5 -o BatchMode=yes ${SERVER_USER}@${SERVER_IP} "echo '连接成功'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH 连接正常${NC}"
else
    echo -e "${YELLOW}需要输入密码进行 SSH 连接${NC}"
fi

# 执行远程部署
echo -e "${YELLOW}[2/6] 检查服务器 Docker 环境...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e

echo "检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo "Docker 安装完成"
else
    echo "Docker 已安装: $(docker --version)"
fi

echo "检查 Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo "安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose 安装完成"
else
    echo "Docker Compose 已安装: $(docker compose version)"
fi
ENDSSH

echo -e "${GREEN}✓ 服务器环境检查完成${NC}"

# 克隆代码
echo -e "${YELLOW}[3/6] 克隆代码到服务器...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << ENDSSH
set -e

# 创建部署目录
mkdir -p ${DEPLOY_DIR}
cd ${DEPLOY_DIR}

# 如果目录已存在代码，先备份再更新
if [ -d "aics" ]; then
    echo "检测到已有代码，正在更新..."
    cd aics
    git pull origin main || true
else
    echo "克隆代码仓库..."
    git clone ${REPO_URL} aics
    cd aics
fi

echo "代码已就绪"
ENDSSH

echo -e "${GREEN}✓ 代码克隆完成${NC}"

# 配置环境变量
echo -e "${YELLOW}[4/6] 配置环境变量...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e
cd /opt/aics/aics/backend

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "已创建 .env 文件，请根据需要修改配置"
fi

# 创建 docker-compose 环境变量文件
cat > /opt/aics/aics/.env.prod << 'ENVEOF'
# 生产环境配置
FLASK_ENV=production
SECRET_KEY=hfcc-aics-production-secret-key-2024
CORS_ORIGINS=*

# LLM 配置（请根据实际情况修改）
LLM_API_KEY=your-api-key-here
LLM_API_URL=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
ENVEOF

echo "环境变量配置完成"
ENDSSH

echo -e "${GREEN}✓ 环境变量配置完成${NC}"

# 停止旧容器
echo -e "${YELLOW}[5/6] 停止旧容器（如果存在）...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} "cd ${DEPLOY_DIR}/aics && docker compose down || true"
echo -e "${GREEN}✓ 旧容器已停止${NC}"

# 启动新容器
echo -e "${YELLOW}[6/6] 启动 Docker 容器...${NC}"
ssh ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
set -e
cd /opt/aics/aics

# 使用 docker compose 构建并启动
docker compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
docker compose ps
ENDSSH

echo -e "${GREEN}✓ 服务启动完成${NC}"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  前端访问: ${BLUE}http://${SERVER_IP}${NC}"
echo -e "  后端API:  ${BLUE}http://${SERVER_IP}:5000${NC}"
echo -e "  健康检查: ${BLUE}http://${SERVER_IP}:5000/api/v1/system/health${NC}"
echo ""
echo -e "  查看日志: ${YELLOW}ssh root@${SERVER_IP} 'cd /opt/aics/aics && docker compose logs -f'${NC}"
echo ""
