# 使用 NVIDIA CUDA 12.8.1 + cuDNN 9 runtime 镜像
FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04

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



# 第三步：安装项目依赖（只有代码或 pyproject.toml 改变时才重新执行）
RUN python3 -m uv pip install --system -e .

# 第二步：复制项目代码（改动频率高，放在后面）


COPY app ./app
COPY main.py ./

COPY test_cudnn.py ./

COPY resource/models/faster-whisper-tiny/ /test/faster-whisper-tiny/

# 第四步：验证 cuDNN 库文件存在（不需要 GPU）
RUN echo "\n======================================" && \
    echo "验证 cuDNN 库文件..." && \
    echo "======================================\n" && \
    ls -lh /usr/lib/x86_64-linux-gnu/libcudnn*.so* | head -5 && \
    echo "\n✓ cuDNN 库文件验证通过\n"

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
