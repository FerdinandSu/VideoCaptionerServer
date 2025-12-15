# VideoCaptioner - 无 UI 版本

这是 VideoCaptioner 的纯后端版本，移除了所有 UI 组件，只提供 RPC 接口。

## 变更说明

### 已移除的组件

1. **UI 依赖**
   - PyQt5
   - PyQt-Fluent-Widgets

2. **UI 代码**
   - `app/view/` - 所有界面文件
   - `app/components/` - 所有 UI 组件
   - `app/thread/` - UI 相关线程
   - `main.py` - 原 GUI 启动文件

3. **UI 配置项**
   - `MainWindow.MicaEnabled`
   - `MainWindow.DpiScale`
   - `MainWindow.Language`

### 保留的核心功能

- ✅ 视频转录（支持多种引擎）
  - FasterWhisper (可执行文件版)
  - **FasterWhisper (Python 版) 🐍** - 新增
  - WhisperCpp
  - Whisper API
  - B 接口 / J 接口

- ✅ 字幕处理
  - 字幕分割
  - 字幕优化
  - 字幕翻译（多种翻译服务）

- ✅ RPC 服务
  - Flask REST API
  - SignalR 实时通信
  - Swagger UI 文档

## 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

## 启动服务器

### 方式 1: 使用新的启动脚本（推荐）

```bash
uv run python main_rpc.py
```

### 方式 2: 使用原有的 RPC 服务器脚本

```bash
uv run python rpc_server.py
```

### 方式 3: 通过配置文件启动

在 `settings.json` 中设置：

```json
{
  "RPC": {
    "Enabled": true,
    "Host": "0.0.0.0",
    "Port": 5000
  }
}
```

然后运行：

```bash
uv run python main_rpc.py
```

## 使用 API

服务器启动后，你可以通过以下方式使用：

### 1. Swagger UI（推荐用于测试）

打开浏览器访问：http://localhost:5000/api/docs

### 2. cURL 命令

```bash
# 健康检查
curl http://localhost:5000/health

# 启动字幕化任务
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "video.mp4",
    "raw_subtitle_path": "output.srt",
    "translated_subtitle_path": "output_translated.srt"
  }'

# 获取任务状态
curl http://localhost:5000/api/rpc/get-status
```

### 3. Python 脚本

```python
import requests

BASE_URL = "http://localhost:5000"

# 启动任务
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "video.mp4",
        "raw_subtitle_path": "output.srt",
        "translated_subtitle_path": "output_translated.srt",
    }
)

if response.json()["success"]:
    print(f"任务已启动: {response.json()['task_id']}")
```

## 配置文件

配置文件位于 `settings.json`，采用嵌套的 JSON 格式：

```json
{
  "Transcribe": {
    "TranscribeModel": "FasterWhisper [Python] 🐍"
  },
  "FasterWhisper": {
    "Model": "large-v2",
    "ModelDir": "D:\\path\\to\\model",
    "Device": "cuda"
  },
  "LLM": {
    "LLMService": "Ollama",
    "Ollama_Model": "gemma3:12b",
    "Ollama_API_Base": "http://localhost:11434/v1"
  },
  "Translate": {
    "TranslatorServiceEnum": "LLM 大模型翻译"
  },
  "Subtitle": {
    "NeedTranslate": true,
    "TargetLanguage": "简体中文"
  }
}
```

详细配置说明请参考 [CONFIGURATION.md](CONFIGURATION.md)

## 新特性

### Python 版 Faster-Whisper

现在支持使用 Python 版的 faster-whisper 库，优势：

- ✅ 无需可执行文件
- ✅ 支持本地模型路径
- ✅ 更好的 Python 生态集成
- ✅ 支持 CUDA 和 CPU 推理

配置示例：

```json
{
  "Transcribe": {
    "TranscribeModel": "FasterWhisper [Python] 🐍"
  },
  "FasterWhisper": {
    "Model": "large-v2",
    "ModelDir": "D:\\OSS\\VideoCaptioner\\AppData\\models\\faster-whisper-large-v2",
    "Device": "cuda"
  }
}
```

### 智能配置过滤

配置文件现在会自动过滤无关配置项：

- 只保存当前选择的 LLM 服务配置
- 只保存当前选择的转录模型配置
- 配置文件更加简洁易读

## API 文档

详细的 API 使用说明请参考：

- [RPC_API_GUIDE.md](RPC_API_GUIDE.md) - API 使用指南
- [RPC_QUICKSTART.md](RPC_QUICKSTART.md) - 快速开始
- [SUBTITIZE_RPC_IMPLEMENTATION.md](SUBTITIZE_RPC_IMPLEMENTATION.md) - 实现细节

## 故障排查

### 问题：导入错误

如果遇到导入错误，确保已安装所有依赖：

```bash
uv sync
```

### 问题：端口被占用

修改 `settings.json` 中的端口：

```json
{
  "RPC": {
    "Port": 5001
  }
}
```

### 问题：CUDA 不可用

如果没有 GPU，在配置中使用 CPU：

```json
{
  "FasterWhisper": {
    "Device": "cpu"
  }
}
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

与原项目相同
