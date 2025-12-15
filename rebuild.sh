#!/bin/bash
# 快速重建和重启脚本

echo "停止现有容器..."
docker compose down

echo "重新构建镜像..."
docker compose build

echo "启动服务..."
docker compose up -d

echo "等待服务启动..."
sleep 5

echo "查看日志..."
docker compose logs -f
