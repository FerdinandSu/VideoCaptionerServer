#!/bin/bash
# 在运行中的容器内测试 cuDNN 和 faster-whisper

set -e

echo "========================================"
echo "测试容器内的 cuDNN 和 faster-whisper"
echo "========================================"
echo ""

# 检查容器是否运行
if ! docker compose ps | grep -q "Up"; then
    echo "错误: 容器未运行"
    echo "请先启动容器: make up"
    exit 1
fi

echo "运行测试..."
echo ""

# 在容器内运行测试
docker compose exec videocaptioner python3 test_cudnn.py

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"
