# 语言参数支持

## 问题

用户在使用 Python 版 faster-whisper 时遇到语言代码错误：

```
ValueError: '英语' is not a valid language code
```

这是因为 faster-whisper 需要 ISO 语言代码（如 "en", "zh"），而配置文件使用了中文显示名称（如 "英语", "中文"）。

## 解决方案

### 1. **添加语言代码转换功能**

在 `TranscribeLanguageEnum` 中添加了 `to_language_code()` 静态方法 (app/core/entities.py:292-400)：

```python
@staticmethod
def to_language_code(value) -> str:
    """将 TranscribeLanguageEnum 转换为 ISO 语言代码

    支持：
    - 枚举值: TranscribeLanguageEnum.ENGLISH -> "en"
    - 语言名称: "英语" -> "en", "中文" -> "zh"
    - ISO 代码: "en" -> "en"（直接返回）
    - Auto: "Auto" -> None（自动检测）
    """
```

**支持的输入格式：**
- ✅ ISO 语言代码：`"en"`, `"zh"`, `"ja"` 等
- ✅ 中文名称：`"英语"`, `"中文"`, `"日本語"` 等
- ✅ 自动检测：`"Auto"` 或 `None`
- ✅ 枚举值：`TranscribeLanguageEnum.ENGLISH`

### 2. **FasterWhisperPythonASR 自动转换**

修改 `FasterWhisperPythonASR.__init__()` 使用语言代码转换 (app/core/asr/faster_whisper_python.py:48-50):

```python
# 转换语言代码（如果需要）
from ..entities import TranscribeLanguageEnum
self.language = TranscribeLanguageEnum.to_language_code(language)
```

### 3. **添加 RPC 语言参数**

#### StartSubtitize 方法

添加可选的 `language` 参数 (app/rpc/rpc_service.py:189-195):

```python
def start_subtitize(
    self,
    video_path: str,
    raw_subtitle_path: str,
    translated_subtitle_path: str,
    language: Optional[str] = None,  # 新增参数
) -> int:
```

#### 参数说明

- **language**: 转录语言（可选）
  - 不提供：使用配置文件中的语言设置
  - `"Auto"` 或 `None`: 自动检测语言
  - `"en"`, `"zh"`, `"ja"` 等: ISO 语言代码
  - `"英语"`, `"中文"`, `"日本語"` 等: 语言名称

#### SubtitizeTask 数据类

添加 `language` 字段 (app/rpc/task_manager.py:36):

```python
@dataclass
class SubtitizeTask:
    """字幕化任务"""
    task_id: int
    video_path: str
    raw_subtitle_path: str
    translated_subtitle_path: str
    language: Optional[str] = None  # 新增字段
```

#### 执行器使用语言参数

修改 `subtitize_executor._transcribe()` 优先使用任务的语言参数 (app/rpc/subtitize_executor.py:141-145):

```python
transcribe_config = TranscribeConfig(
    transcribe_model=cfg.get(cfg.transcribe_model),
    transcribe_language=(
        task.language  # 优先使用任务指定的语言
        if task.language
        else cfg.get(cfg.transcribe_language).value  # 否则使用配置文件
    ),
    # ...
)
```

## 使用方法

### cURL 示例

```bash
# 使用配置文件中的语言设置
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "video.mp4",
    "raw_subtitle_path": "output.srt",
    "translated_subtitle_path": "output_translated.srt"
  }'

# 指定使用英语
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "video.mp4",
    "raw_subtitle_path": "output.srt",
    "translated_subtitle_path": "output_translated.srt",
    "language": "en"
  }'

# 使用中文名称
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "video.mp4",
    "raw_subtitle_path": "output.srt",
    "translated_subtitle_path": "output_translated.srt",
    "language": "中文"
  }'

# 自动检测
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "video.mp4",
    "raw_subtitle_path": "output.srt",
    "translated_subtitle_path": "output_translated.srt",
    "language": "Auto"
  }'
```

### Python 示例

```python
import requests

BASE_URL = "http://localhost:5000"

# 方式 1: 使用配置文件中的语言
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "video.mp4",
        "raw_subtitle_path": "output.srt",
        "translated_subtitle_path": "output_translated.srt",
    }
)

# 方式 2: 指定使用英语
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "video.mp4",
        "raw_subtitle_path": "output.srt",
        "translated_subtitle_path": "output_translated.srt",
        "language": "en",
    }
)

# 方式 3: 使用中文名称
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "video.mp4",
        "raw_subtitle_path": "output.srt",
        "translated_subtitle_path": "output_translated.srt",
        "language": "中文",
    }
)

# 方式 4: 自动检测
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "video.mp4",
        "raw_subtitle_path": "output.srt",
        "translated_subtitle_path": "output_translated.srt",
        "language": "Auto",
    }
)
```

## 测试

运行测试脚本：

```bash
uv run python test_language_param.py
```

## 支持的语言代码

| 语言名称 | ISO 代码 | 语言名称 | ISO 代码 |
|---------|---------|---------|---------|
| Auto | `None` | 英语 | `en` |
| 中文 | `zh` | 日本語 | `ja` |
| 韩语 | `ko` | 粤语 | `yue` |
| 法语 | `fr` | 德语 | `de` |
| 西班牙语 | `es` | 俄语 | `ru` |
| 葡萄牙语 | `pt` | 土耳其语 | `tr` |
| ... | ... | ... | ... |

完整列表请参考 `app/core/entities.py` 中的 `TranscribeLanguageEnum.to_language_code()` 方法。

## 配置文件

建议将配置文件中的语言设置为 `"Auto"` 以启用自动检测：

```json
{
  "Transcribe": {
    "TranscribeLanguage": "Auto"
  }
}
```

然后在调用 RPC 时根据需要指定具体语言。
