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

# 第一步：只复制依赖声明文件（改动频率低）
COPY pyproject.toml ./

# 第二步：安装 cuDNN 和 cuBLAS（独立于项目代码，会被 Docker 缓存）
RUN python3 -m pip install nvidia-cudnn-cu12 nvidia-cublas-cu12

# 第三步：创建 cuDNN 库符号链接
RUN CUDNN_PATH=$(python3 -c "import nvidia.cudnn; print(nvidia.cudnn.__path__[0])") && \
    echo "cuDNN path: $CUDNN_PATH" && \
    ln -s $CUDNN_PATH/lib/libcudnn*.so* /usr/local/lib/ && \
    ldconfig

# 第四步：复制项目代码（改动频率高，放在后面）
COPY app ./app
COPY main.py ./

# 第五步：安装项目依赖（只有代码或 pyproject.toml 改变时才重新执行）
RUN python3 -m uv pip install --system -e .

COPY test_cudnn.py ./

COPY resource/models/faster-whisper-tiny/ /test/faster-whisper-tiny/

# 第六步：测试 cuDNN 和 faster-whisper 是否正常工作
RUN echo "\n======================================" && \
    echo "运行环境测试..." && \
    echo "======================================\n" && \
    python3 test_cudnn.py && \
    echo "\n✓ 环境测试通过，继续构建...\n"

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
