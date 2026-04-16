#!/bin/bash
# AICS - 公募基金客服AI辅助系统
# 一键启动脚本
# 使用方法: ./start.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  AICS - 公募基金客服AI辅助系统${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.11+${NC}"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js 18+${NC}"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到 npm，请先安装 npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境检查通过${NC}"
echo ""

# 函数：启动后端
start_backend() {
    echo -e "${YELLOW}[1/2] 启动后端服务...${NC}"
    cd "${PROJECT_ROOT}/backend"
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}  创建虚拟环境...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo -e "${BLUE}  安装后端依赖...${NC}"
    pip install -q -r requirements.txt
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}  警告: 未找到 .env 文件，使用 .env.example 创建${NC}"
        cp .env.example .env
        echo -e "${YELLOW}  请编辑 backend/.env 文件配置必要的环境变量${NC}"
    fi
    
    # 启动后端
    echo -e "${GREEN}  后端服务启动中... (http://localhost:5001)${NC}"
    python run.py &
    BACKEND_PID=$!
    
    # 等待后端启动
    sleep 3
    
    # 检查后端是否成功启动
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        exit 1
    fi
    
    deactivate
    cd "${PROJECT_ROOT}"
}

# 函数：启动前端
start_frontend() {
    echo -e "${YELLOW}[2/2] 启动前端服务...${NC}"
    cd "${PROJECT_ROOT}/frontend"
    
    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}  安装前端依赖...${NC}"
        npm install
    fi
    
    # 启动前端
    echo -e "${GREEN}  前端服务启动中... (http://localhost:5173)${NC}"
    npm run dev &
    FRONTEND_PID=$!
    
    # 等待前端启动
    sleep 5
    
    # 检查前端是否成功启动
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${RED}✗ 前端服务启动失败${NC}"
        exit 1
    fi
    
    cd "${PROJECT_ROOT}"
}

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${BLUE}  后端服务已停止${NC}"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${BLUE}  前端服务已停止${NC}"
    fi
    echo -e "${GREEN}服务已清理完毕${NC}"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

# 启动服务
start_backend
echo ""
start_frontend

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  所有服务已启动成功！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  前端访问: ${BLUE}http://localhost:5173${NC}"
echo -e "  后端API:  ${BLUE}http://localhost:5001${NC}"
echo -e "  健康检查: ${BLUE}http://localhost:5001/api/v1/system/health${NC}"
echo ""
echo -e "  按 ${YELLOW}Ctrl+C${NC} 停止所有服务"
echo ""

# 等待用户中断
wait
