.PHONY: help build up down logs restart clean test rebuild test-cudnn

help:
	@echo "VideoCaptioner Docker 管理命令"
	@echo ""
	@echo "使用方法:"
	@echo "  make build       - 构建 Docker 镜像"
	@echo "  make up          - 启动服务"
	@echo "  make down        - 停止服务"
	@echo "  make logs        - 查看日志"
	@echo "  make restart     - 重启服务"
	@echo "  make rebuild     - 重新构建并启动"
	@echo "  make shell       - 进入容器"
	@echo "  make test        - 测试 API"
	@echo "  make test-cudnn  - 测试 cuDNN 环境"
	@echo "  make clean       - 清理容器和镜像"
	@echo "  make gpu-test    - 测试 GPU 访问"

build:
	docker compose build

up:
	docker compose up -d
	@echo "服务已启动"
	@echo "Swagger UI: http://localhost:5000/api/docs"

down:
	docker compose down

logs:
	docker compose logs -f

restart:
	docker compose restart

rebuild:
	docker compose down
	docker compose build
	docker compose up -d
	@echo "服务已重新构建并启动"
	@echo "查看日志: make logs"

shell:
	docker compose exec videocaptioner /bin/bash

test:
	@bash test-docker.sh

clean:
	docker compose down -v
	docker rmi videocaptioner:latest || true

gpu-test:
	docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi

# 开发环境
dev-up:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

dev-logs:
	docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f

# 生产环境
prod-up:
	docker compose -f docker-compose.yml up -d --build

prod-logs:
	docker compose -f docker-compose.yml logs -f --tail=100
