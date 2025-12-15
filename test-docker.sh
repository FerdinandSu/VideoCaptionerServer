#!/bin/bash
# Docker 部署测试脚本

set -e

API_BASE="http://localhost:5000"

echo "=========================================="
echo "VideoCaptioner Docker API 测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试健康检查
echo "1. 测试健康检查..."
if curl -f "$API_BASE/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 健康检查通过${NC}"
else
    echo -e "${RED}✗ 健康检查失败${NC}"
    exit 1
fi

# 测试状态接口
echo ""
echo "2. 测试状态接口..."
response=$(curl -s "$API_BASE/status")
if echo "$response" | grep -q "success"; then
    echo -e "${GREEN}✓ 状态接口正常${NC}"
    echo "响应: $response"
else
    echo -e "${RED}✗ 状态接口失败${NC}"
    exit 1
fi

# 测试 Swagger UI
echo ""
echo "3. 测试 Swagger UI..."
if curl -f "$API_BASE/api/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Swagger UI 可访问${NC}"
else
    echo -e "${RED}✗ Swagger UI 不可访问${NC}"
fi

# 测试任务状态接口
echo ""
echo "4. 测试任务状态接口..."
response=$(curl -s "$API_BASE/api/rpc/get-status")
if echo "$response" | grep -q "status"; then
    echo -e "${GREEN}✓ 任务状态接口正常${NC}"
    echo "响应: $response"
else
    echo -e "${RED}✗ 任务状态接口失败${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}所有测试完成!${NC}"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - Swagger UI: $API_BASE/api/docs"
echo "  - 健康检查: $API_BASE/health"
echo "  - 任务状态: $API_BASE/api/rpc/get-status"
