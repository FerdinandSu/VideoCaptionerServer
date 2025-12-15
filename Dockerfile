# 使用 NVIDIA CUDA 基础镜像
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    ffmpeg \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 并添加到 PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="/root/.cargo/bin:$PATH"' >> /root/.bashrc

# 设置 PATH 环境变量（在构建时生效）
ENV PATH="/root/.cargo/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./
COPY app ./app
COPY main.py ./

# 安装 Python 依赖（在同一层中确保 PATH 生效）
RUN /root/.cargo/bin/uv pip install --system -e .

# 创建必要的目录
RUN mkdir -p /app/AppData/models \
    /app/work \
    /data

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python3", "main.py"]
