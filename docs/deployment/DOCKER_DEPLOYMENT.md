# VideoCaptioner Docker 部署指南

## 前置要求

### 1. 安装 Docker 和 NVIDIA Container Toolkit

**Ubuntu/Debian:**
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**验证 GPU 访问:**
```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### 2. 安装 Docker Compose

```bash
# Docker Compose V2 (推荐)
sudo apt-get install docker-compose-plugin

# 验证安装
docker compose version
```

## 部署步骤

### 1. 准备目录结构

```
VideoCaptioner/
├── settings.json           # 配置文件
├── AppData/
│   └── models/            # FasterWhisper 模型目录
│       └── faster-whisper-large-v2/
├── data/                  # 数据目录（视频、字幕等）
├── work/                  # 工作目录
├── Dockerfile
├── docker-compose.yml
└── main.py
```

### 2. 配置 settings.json

**Linux 环境下的配置示例:**

```json
{
  "Cache": {
    "CacheEnabled": true
  },
  "FasterWhisper": {
    "Device": "cuda",
    "Model": "large-v2",
    "ModelDir": "/app/AppData/models",
    "VadFilter": true,
    "VadMethod": "silero_v4",
    "VadThreshold": 0.4
  },
  "LLM": {
    "LLMService": "Ollama",
    "Ollama_API_Base": "http://host.docker.internal:11434/v1",
    "Ollama_API_Key": "ollama",
    "Ollama_Model": "gemma3:12b"
  },
  "RPC": {
    "Enabled": true,
    "Host": "0.0.0.0",
    "Port": 5000
  },
  "Transcribe": {
    "TranscribeLanguage": "Auto",
    "TranscribeModel": "FasterWhisper [Python] 🐍"
  },
  "Translate": {
    "BatchSize": 10,
    "ThreadNum": 8,
    "TranslatorServiceEnum": "LLM 大模型翻译"
  },
  "Subtitle": {
    "TargetLanguage": "简体中文",
    "NeedTranslate": true
  }
}
```

**注意事项:**
- `Host` 设置为 `"0.0.0.0"` 以允许容器外访问
- `ModelDir` 使用容器内路径 `/app/AppData/models`
- 如果要访问宿主机服务（如 Ollama），使用 `host.docker.internal`

### 3. 准备模型文件

将 FasterWhisper 模型放到 `AppData/models` 目录：

```bash
# 示例目录结构
AppData/models/
├── faster-whisper-large-v2/
│   ├── config.json
│   ├── model.bin
│   ├── tokenizer.json
│   └── vocabulary.txt
```

### 4. 构建和启动

```bash
# 构建镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

## 使用方法

### 访问 API

**Swagger UI:**
```
http://localhost:5000/api/docs
```

**健康检查:**
```bash
curl http://localhost:5000/health
```

**启动字幕化任务:**
```bash
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/video.mp4",
    "raw_subtitle_path": "/data/video.srt",
    "translated_subtitle_path": "/data/video.translated.srt",
    "language": "en"
  }'
```

**查看任务状态:**
```bash
curl http://localhost:5000/api/rpc/get-status
```

## 故障排查

### 1. GPU 不可用

```bash
# 检查容器内 GPU
docker compose exec videocaptioner nvidia-smi

# 检查 NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

### 2. 查看容器日志

```bash
# 实时日志
docker compose logs -f videocaptioner

# 最近 100 行
docker compose logs --tail=100 videocaptioner
```

### 3. 进入容器调试

```bash
docker compose exec videocaptioner /bin/bash
```

### 4. cuDNN 问题

如果遇到 cuDNN 错误，确保基础镜像版本与 NVIDIA 驱动兼容：

```bash
# 检查驱动版本
nvidia-smi

# 根据驱动选择合适的 CUDA 镜像
# CUDA 12.x: nvidia/cuda:12.2.0-runtime-ubuntu22.04
# CUDA 11.x: nvidia/cuda:11.8.0-runtime-ubuntu22.04
```

## 性能优化

### 1. 指定 GPU

```yaml
# docker-compose.yml
environment:
  - CUDA_VISIBLE_DEVICES=0  # 使用第一块 GPU
  - CUDA_VISIBLE_DEVICES=0,1  # 使用多块 GPU
```

### 2. 内存限制

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
    reservations:
      memory: 4G
```

### 3. 使用本地模型缓存

将 HuggingFace cache 挂载到宿主机：

```yaml
volumes:
  - ~/.cache/huggingface:/root/.cache/huggingface:rw
```

## 生产环境建议

1. **使用环境变量管理敏感信息:**
   ```yaml
   environment:
     - OLLAMA_API_KEY=${OLLAMA_API_KEY}
   ```

2. **启用日志轮转:**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

3. **设置资源限制:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4'
         memory: 8G
   ```

4. **使用反向代理 (Nginx):**
   ```nginx
   location /videocaptioner/ {
       proxy_pass http://localhost:5000/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并重启
docker compose down
docker compose build
docker compose up -d
```
