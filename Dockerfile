# 使用 NVIDIA CUDA 基础镜像（不含 cuDNN，我们将安装 cuDNN 9）
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
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

# 升级 pip 并安装 uv
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY pyproject.toml ./
COPY app ./app
COPY main.py ./

# 安装 Python 依赖
RUN python3 -m uv pip install --system -e .

# 安装 cuDNN 9 和 cuBLAS（faster-whisper 需要）
RUN python3 -m pip install nvidia-cudnn-cu12 nvidia-cublas-cu12

# 查找并设置 cuDNN 库路径
RUN CUDNN_PATH=$(python3 -c "import nvidia.cudnn; print(nvidia.cudnn.__path__[0])") && \
    echo "cuDNN path: $CUDNN_PATH" && \
    ln -s $CUDNN_PATH/lib/libcudnn*.so* /usr/local/lib/ && \
    ldconfig

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
