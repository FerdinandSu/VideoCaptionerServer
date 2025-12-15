#!/bin/bash
# VideoCaptioner Docker 快速部署脚本

set -e

echo "=========================================="
echo "VideoCaptioner Docker 部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose plugin"
    exit 1
fi

# 检查 NVIDIA Docker
if ! docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}警告: NVIDIA Container Toolkit 可能未正确配置${NC}"
    echo "如果需要 GPU 支持，请安装 NVIDIA Container Toolkit"
    read -p "继续部署? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查必要文件
echo "检查必要文件..."

if [ ! -f "settings.json" ]; then
    echo -e "${RED}错误: settings.json 不存在${NC}"
    exit 1
fi

if [ ! -d "AppData/models" ]; then
    echo -e "${YELLOW}警告: AppData/models 目录不存在${NC}"
    echo "创建模型目录..."
    mkdir -p AppData/models
fi

# 创建必要目录
echo "创建必要目录..."
mkdir -p data work

# 构建镜像
echo ""
echo -e "${GREEN}开始构建 Docker 镜像...${NC}"
docker compose build

# 启动服务
echo ""
echo -e "${GREEN}启动服务...${NC}"
docker compose up -d

# 等待服务就绪
echo ""
echo "等待服务启动..."
sleep 5

# 检查服务状态
if docker compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ 服务启动成功!${NC}"
    echo ""
    echo "访问地址:"
    echo "  - Swagger UI: http://localhost:5000/api/docs"
    echo "  - 健康检查: http://localhost:5000/health"
    echo ""
    echo "查看日志:"
    echo "  docker compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker compose down"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo "查看日志:"
    docker compose logs
    exit 1
fi
