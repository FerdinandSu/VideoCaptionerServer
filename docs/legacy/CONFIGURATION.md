# 配置文件说明

## 配置文件位置

默认配置文件：`settings.json`

## 配置文件格式

配置文件使用 JSON 格式，采用嵌套的结构：

```json
{
  "GroupName": {
    "ConfigName": "value"
  }
}
```

**示例：**

```json
{
  "LLM": {
    "LLMService": "Ollama",
    "Ollama_Model": "gemma3:12b"
  },
  "Transcribe": {
    "TranscribeModel": "FasterWhisper [Python] 🐍"
  }
}
```

## 默认配置说明

已创建的 `settings.json` 包含以下配置：

### 转录配置（Transcribe）

- **转录模型**: FasterWhisper ✨
- **Faster Whisper 模型**: large-v2
- **设备**: cuda (GPU加速)
- **输出格式**: SRT
- **转录语言**: Auto (自动检测)

### LLM 配置（用于翻译和优化）

- **LLM 服务**: Ollama
- **Ollama 模型**: gemma3:12b
- **Ollama API 地址**: http://10.123.3.3:11434/v1
- **Ollama API Key**: ollama

### 翻译配置

- **翻译服务**: LLM 大模型翻译
- **目标语言**: 简体中文
- **启用翻译**: true
- **启用字幕分割**: true
- **批处理大小**: 10
- **线程数**: 8

### 字幕处理配置

- **启用优化**: false
- **启用翻译**: true
- **启用分割**: true
- **中文最大字数**: 25
- **英文最大单词数**: 20

## 修改配置

### 方式 1: 直接编辑 settings.json

使用文本编辑器打开 `settings.json`，修改对应的值。

**重要枚举值参考：**

#### 转录模型（Transcribe.TranscribeModel）
- `"B 接口"` - B 接口
- `"J 接口"` - J 接口
- `"Whisper [API] ✨"` - Whisper API
- `"FasterWhisper ✨"` - FasterWhisper（可执行文件版）
- `"FasterWhisper [Python] 🐍"` - FasterWhisper（Python 库版，支持本地模型）
- `"WhisperCpp"` - WhisperCpp

#### Faster Whisper 模型（FasterWhisper.Model）
- `"tiny"` - tiny 模型（最快，准确度最低）
- `"base"` - base 模型
- `"small"` - small 模型
- `"medium"` - medium 模型
- `"large-v1"` - large-v1 模型
- `"large-v2"` - large-v2 模型（推荐）
- `"large-v3"` - large-v3 模型
- `"large-v3-turbo"` - large-v3-turbo 模型（最新，速度快）

#### LLM 服务（LLM.LLMService）
- `"OpenAI"` - OpenAI
- `"SiliconCloud"` - SiliconCloud
- `"DeepSeek"` - DeepSeek
- `"Ollama"` - Ollama（本地部署）
- `"LM Studio"` - LM Studio（本地部署）
- `"Gemini"` - Google Gemini
- `"ChatGLM"` - ChatGLM

#### 翻译服务（Translate.TranslatorServiceEnum）
- `"LLM 大模型翻译"` - 使用 LLM 进行翻译（推荐）
- `"DeepLx 翻译"` - DeepLx 翻译
- `"微软翻译"` - Microsoft Translator
- `"谷歌翻译"` - Google Translate

#### 目标语言（Subtitle.TargetLanguage）
- `"简体中文"` - 简体中文
- `"繁体中文"` - 繁体中文
- `"英语"` - 英语
- `"日本語"` - 日语
- `"韩语"` - 韩语
- 等等...

### 方式 2: 通过程序 API

```python
from app.common.config import cfg

# 加载配置
cfg.load('settings.json')

# 修改配置
cfg.set(cfg.ollama_model, "llama3:8b")
cfg.set(cfg.need_translate, True)

# 配置会自动保存
```

## 常见配置场景

### 场景 1: 使用本地 Ollama

```json
{
  "LLM": {
    "LLMService": "Ollama",
    "Ollama_Model": "gemma3:12b",
    "Ollama_API_Base": "http://localhost:11434/v1"
  },
  "Translate": {
    "TranslatorServiceEnum": "LLM 大模型翻译"
  }
}
```

### 场景 2: 使用 OpenAI API

```json
{
  "LLM": {
    "LLMService": "OpenAI",
    "OpenAI_Model": "gpt-4o-mini",
    "OpenAI_API_Key": "your-api-key-here",
    "OpenAI_API_Base": "https://api.openai.com/v1"
  },
  "Translate": {
    "TranslatorServiceEnum": "LLM 大模型翻译"
  }
}
```

### 场景 3: 使用 DeepSeek

```json
{
  "LLM": {
    "LLMService": "DeepSeek",
    "DeepSeek_Model": "deepseek-chat",
    "DeepSeek_API_Key": "your-api-key-here"
  },
  "Translate": {
    "TranslatorServiceEnum": "LLM 大模型翻译"
  }
}
```

### 场景 4: 使用本地 FasterWhisper 模型（Python 版）

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

**说明：**
- Python 版 FasterWhisper 使用 faster-whisper Python 库，无需可执行文件
- 支持使用本地模型路径，不需要每次下载
- ModelDir 指定本地模型文件夹的完整路径
- 可以使用 CUDA 或 CPU 进行推理

### 场景 5: 只转录不翻译

```json
{
  "Subtitle": {
    "NeedTranslate": false,
    "NeedOptimize": false,
    "NeedSplit": true
  }
}
```

### 场景 6: 使用免费翻译服务

```json
{
  "Translate": {
    "TranslatorServiceEnum": "微软翻译"
  }
}
```

或者

```json
{
  "Translate": {
    "TranslatorServiceEnum": "谷歌翻译"
  }
}
```

## 配置项完整列表

### LLM 相关
- `LLM.LLMService` - LLM 服务提供商
- `LLM.OpenAI_*` - OpenAI 相关配置
- `LLM.Ollama_*` - Ollama 相关配置
- `LLM.DeepSeek_*` - DeepSeek 相关配置
- 等等...

### 转录相关
- `Transcribe.TranscribeModel` - 转录模型
- `Transcribe.OutputFormat` - 输出格式
- `Transcribe.TranscribeLanguage` - 转录语言

### FasterWhisper 相关
- `FasterWhisper.Model` - 模型大小
- `FasterWhisper.Device` - 运算设备（cuda/cpu）
- `FasterWhisper.VadFilter` - VAD 过滤
- `FasterWhisper.VadThreshold` - VAD 阈值
- `FasterWhisper.VadMethod` - VAD 方法
- `FasterWhisper.FfMdxKim2` - 人声提取
- `FasterWhisper.OneWord` - 单字处理
- `FasterWhisper.Prompt` - 提示词

### 翻译相关
- `Translate.TranslatorServiceEnum` - 翻译服务
- `Translate.NeedReflectTranslate` - 反思翻译
- `Translate.BatchSize` - 批处理大小
- `Translate.ThreadNum` - 线程数

### 字幕相关
- `Subtitle.NeedOptimize` - 是否优化
- `Subtitle.NeedTranslate` - 是否翻译
- `Subtitle.NeedSplit` - 是否分割
- `Subtitle.TargetLanguage` - 目标语言
- `Subtitle.MaxWordCountCJK` - 中文最大字数
- `Subtitle.MaxWordCountEnglish` - 英文最大单词数
- `Subtitle.CustomPromptText` - 自定义提示词

### 视频相关
- `Video.SoftSubtitle` - 软字幕
- `Video.NeedVideo` - 是否生成视频
- `Video.VideoQuality` - 视频质量

### RPC 相关
- `RPC.Enabled` - 是否启用 RPC
- `RPC.Host` - 监听地址
- `RPC.Port` - 监听端口
- `RPC.MasterUrl` - Master URL

### 其他
- `Save.Work_Dir` - 工作目录
- `Cache.CacheEnabled` - 是否启用缓存
- `Update.CheckUpdateAtStartUp` - 启动时检查更新

## 注意事项

1. **字符编码**: 配置文件必须使用 UTF-8 编码
2. **JSON 格式**: 注意 JSON 语法（逗号、引号等）
3. **枚举值**: 枚举类型的配置必须使用准确的字符串值（包括特殊字符如 `✨`）
4. **布尔值**: 使用 `true` / `false`（小写，不带引号）
5. **数字**: 直接写数字，不要加引号
6. **路径**: Windows 路径使用双反斜杠 `\\` 或单正斜杠 `/`

## 故障排查

### 问题：配置没有生效

**解决方案：**
1. 检查配置文件语法是否正确（使用 JSON 验证器）
2. 确认配置项的 key 名称正确（区分大小写）
3. 确认枚举值使用正确的字符串
4. 检查日志输出，看是否有配置加载错误

### 问题：Ollama 连接失败

**解决方案：**
1. 确认 Ollama 服务正在运行
2. 检查 API 地址是否正确（包括端口）
3. 测试连接：`curl http://10.123.3.3:11434/v1/models`

### 问题：FasterWhisper 模型下载失败

**解决方案：**
1. 手动下载模型到 `FasterWhisper.ModelDir` 指定的目录
2. 或使用较小的模型（如 `"tiny"` 或 `"base"`）进行测试
