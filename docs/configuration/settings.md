# 配置文件说明

## settings.json 结构

VideoCaptioner 使用 JSON 格式的配置文件，采用嵌套结构组织配置项。

## 完整配置示例

```json
{
  "Cache": {
    "CacheEnabled": true
  },
  "FasterWhisper": {
    "Device": "cuda",
    "FfMdxKim2": false,
    "Model": "large-v2",
    "ModelDir": "/app/AppData/models",
    "OneWord": true,
    "Program": "/path/to/faster-whisper-xxl",
    "Prompt": "",
    "VadFilter": true,
    "VadMethod": "silero_v4",
    "VadThreshold": 0.4
  },
  "LLM": {
    "LLMService": "Ollama",
    "Ollama_API_Base": "http://localhost:11434/v1",
    "Ollama_API_Key": "ollama",
    "Ollama_Model": "gemma3:12b"
  },
  "RPC": {
    "Enabled": true,
    "Host": "0.0.0.0",
    "Port": 5000
  },
  "Save": {
    "Work_Dir": "/app/work"
  },
  "Subtitle": {
    "CustomPromptText": "",
    "MaxWordCountCJK": 25,
    "MaxWordCountEnglish": 20,
    "NeedOptimize": false,
    "NeedSplit": true,
    "NeedTranslate": true,
    "TargetLanguage": "简体中文"
  },
  "SubtitleStyle": {
    "Layout": "译文在上",
    "PreviewImage": "",
    "StyleName": "default"
  },
  "Transcribe": {
    "OutputFormat": "SRT",
    "TranscribeLanguage": "Auto",
    "TranscribeModel": "FasterWhisper [Python] 🐍"
  },
  "Translate": {
    "BatchSize": 10,
    "DeeplxEndpoint": "",
    "NeedReflectTranslate": false,
    "ThreadNum": 8,
    "TranslatorServiceEnum": "LLM 大模型翻译"
  },
  "Update": {
    "CheckUpdateAtStartUp": false
  },
  "Video": {
    "NeedVideo": true,
    "SoftSubtitle": false,
    "VideoQuality": "极高质量"
  }
}
```

## 配置项详解

### Cache - 缓存配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| CacheEnabled | boolean | true | 是否启用转录缓存 |

### FasterWhisper - FasterWhisper 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| Device | string | "cuda" | 设备类型: "cuda", "cpu" |
| FfMdxKim2 | boolean | false | 是否启用人声分离 |
| Model | string | "large-v2" | 模型名称 |
| ModelDir | string | "" | 本地模型目录路径 |
| OneWord | boolean | true | 是否启用词级时间戳 |
| Program | string | "" | FasterWhisper 可执行文件路径 |
| Prompt | string | "" | 转录提示词 |
| VadFilter | boolean | true | 是否启用 VAD 过滤 |
| VadMethod | string | "silero_v4" | VAD 方法 |
| VadThreshold | number | 0.4 | VAD 阈值 (0-1) |

**VadMethod 可选值:**
- `silero_v3` - Silero VAD v3
- `silero_v4` - Silero VAD v4 (推荐)
- `silero_v5` - Silero VAD v5
- `pyannote_v3` - PyAnnote v3
- `auditok` - Auditok
- `webrtc` - WebRTC VAD

### LLM - 大语言模型配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| LLMService | string | "Ollama" | LLM 服务类型 |

**LLMService 可选值:**
- `Ollama` - 本地 Ollama 服务
- `DeepSeek` - DeepSeek API
- `OpenAI` - OpenAI API
- `SiliconCloud` - 硅基流动
- `LM Studio` - LM Studio
- `Gemini` - Google Gemini
- `ChatGLM` - 智谱 ChatGLM

#### Ollama 配置

| 配置项 | 类型 | 说明 |
|--------|------|------|
| Ollama_API_Base | string | Ollama API 地址 |
| Ollama_API_Key | string | API 密钥（通常为 "ollama"）|
| Ollama_Model | string | 模型名称 |

#### DeepSeek 配置

| 配置项 | 类型 | 说明 |
|--------|------|------|
| DeepSeek_API_Base | string | DeepSeek API 地址 |
| DeepSeek_API_Key | string | API 密钥 |
| DeepSeek_Model | string | 模型名称 |

#### OpenAI 配置

| 配置项 | 类型 | 说明 |
|--------|------|------|
| OpenAI_API_Base | string | OpenAI API 地址 |
| OpenAI_API_Key | string | API 密钥 |
| OpenAI_Model | string | 模型名称 |

### RPC - RPC 服务配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| Enabled | boolean | true | 是否启用 RPC 服务 |
| Host | string | "0.0.0.0" | 监听地址 |
| Port | number | 5000 | 监听端口 |
| MasterUrl | string | "" | Master SignalR Hub URL (可选) |

**重要提示:**
- Docker 环境使用 `"0.0.0.0"` 允许外部访问
- 本地开发可使用 `"localhost"` 或 `"127.0.0.1"`

### Save - 保存配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| Work_Dir | string | "work" | 工作目录路径 |

### Subtitle - 字幕配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| CustomPromptText | string | "" | 自定义提示词 |
| MaxWordCountCJK | number | 25 | 中日韩文字最大字数 |
| MaxWordCountEnglish | number | 20 | 英文单词最大数量 |
| NeedOptimize | boolean | false | 是否启用 LLM 优化 |
| NeedSplit | boolean | true | 是否启用智能分割 |
| NeedTranslate | boolean | true | 是否启用翻译 |
| TargetLanguage | string | "简体中文" | 目标翻译语言 |

### SubtitleStyle - 字幕样式配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| Layout | string | "译文在上" | 字幕布局 |
| StyleName | string | "default" | 样式名称 |

**Layout 可选值:**
- `仅原文` - 只显示原文
- `仅译文` - 只显示译文
- `原文在上` - 双语，原文在上
- `译文在上` - 双语，译文在上

### Transcribe - 转录配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| OutputFormat | string | "SRT" | 输出格式 |
| TranscribeLanguage | string | "Auto" | 转录语言 |
| TranscribeModel | string | "" | 转录模型 |

**TranscribeModel 可选值:**
- `FasterWhisper ✨` - FasterWhisper (exe 版本)
- `FasterWhisper [Python] 🐍` - FasterWhisper (Python 库)
- `WhisperCpp` - Whisper C++ 实现
- `Whisper [API] ✨` - Whisper API

**TranscribeLanguage 可选值:**
- `Auto` - 自动检测
- ISO 代码: `en`, `zh`, `ja`, `ko` 等
- 语言名称: `英语`, `中文`, `日本語` 等

### Translate - 翻译配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| BatchSize | number | 10 | 批处理大小 |
| DeeplxEndpoint | string | "" | DeepLX 端点 (如使用) |
| NeedReflectTranslate | boolean | false | 是否启用反思翻译 |
| ThreadNum | number | 8 | 线程数 |
| TranslatorServiceEnum | string | "" | 翻译服务 |

**TranslatorServiceEnum 可选值:**
- `LLM 大模型翻译` - 使用 LLM 翻译
- `DeepLx 翻译` - DeepL 翻译
- `微软翻译` - Bing 翻译
- `谷歌翻译` - Google 翻译

### Update - 更新配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| CheckUpdateAtStartUp | boolean | false | 启动时检查更新 |

### Video - 视频配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| NeedVideo | boolean | true | 是否生成视频 |
| SoftSubtitle | boolean | false | 是否使用软字幕 |
| VideoQuality | string | "极高质量" | 视频质量 |

## 环境特定配置

### Docker 环境

```json
{
  "FasterWhisper": {
    "ModelDir": "/app/AppData/models"
  },
  "RPC": {
    "Host": "0.0.0.0"
  },
  "LLM": {
    "Ollama_API_Base": "http://host.docker.internal:11434/v1"
  }
}
```

### Windows 环境

```json
{
  "FasterWhisper": {
    "ModelDir": "D:\\OSS\\VideoCaptioner\\AppData\\models",
    "Program": "C:\\path\\to\\faster-whisper-xxl.exe"
  },
  "RPC": {
    "Host": "localhost"
  }
}
```

### Linux 环境

```json
{
  "FasterWhisper": {
    "ModelDir": "/opt/videocaptioner/models"
  },
  "RPC": {
    "Host": "0.0.0.0"
  }
}
```

## 配置最佳实践

### 1. 性能优化

```json
{
  "FasterWhisper": {
    "Device": "cuda",
    "VadFilter": true,
    "VadThreshold": 0.4
  },
  "Translate": {
    "ThreadNum": 8,
    "BatchSize": 10
  }
}
```

### 2. 质量优先

```json
{
  "Subtitle": {
    "NeedOptimize": true,
    "NeedSplit": true
  },
  "Translate": {
    "NeedReflectTranslate": true
  }
}
```

### 3. 成本控制

```json
{
  "Subtitle": {
    "NeedOptimize": false
  },
  "Translate": {
    "NeedReflectTranslate": false,
    "TranslatorServiceEnum": "谷歌翻译"
  }
}
```

## 配置验证

启动时会自动验证配置，如有错误会在日志中显示。

## 相关文档

- [转录配置详解](transcribe.md)
- [翻译配置详解](translate.md)
- [部署配置](../deployment/docker-deployment.md)
