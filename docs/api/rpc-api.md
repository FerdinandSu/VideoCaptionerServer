# VideoCaptioner RPC API 参考

## 基本信息

**Base URL**: `http://localhost:5000`

**API 版本**: 1.0.0

**Swagger UI**: `http://localhost:5000/api/docs`

## 认证

当前版本不需要认证。如需在生产环境使用，建议配置反向代理（Nginx/Traefik）添加认证。

## 端点列表

### 系统管理

#### 健康检查

```http
GET /health
```

**响应示例:**
```json
{
  "success": true,
  "status": "healthy"
}
```

#### 获取连接状态

```http
GET /status
```

**响应示例:**
```json
{
  "success": true,
  "is_connected": false,
  "master_url": null,
  "status": "idle"
}
```

### RPC 服务

#### 启动字幕化任务

```http
POST /api/rpc/start-subtitize
```

**请求体:**
```json
{
  "video_path": "/data/video.mp4",
  "raw_subtitle_path": "/data/video.srt",
  "translated_subtitle_path": "/data/video.translated.srt",
  "language": "en"  // 可选
}
```

**参数说明:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video_path | string | 是 | 视频文件路径 |
| raw_subtitle_path | string | 是 | 原始字幕输出路径 |
| translated_subtitle_path | string | 是 | 翻译字幕输出路径 |
| language | string | 否 | 转录语言（ISO 代码或语言名称）|

**language 参数支持格式:**
- ISO 代码: `"en"`, `"zh"`, `"ja"`, `"ko"` 等
- 语言名称: `"英语"`, `"中文"`, `"日本語"` 等
- 自动检测: `"Auto"` 或不提供此参数

**响应示例:**

成功:
```json
{
  "success": true,
  "task_id": 1,
  "message": "任务已启动: task_id=1"
}
```

失败（已有任务运行）:
```json
{
  "success": false,
  "task_id": -1,
  "message": "已有任务正在运行"
}
```

失败（参数无效）:
```json
{
  "success": false,
  "task_id": -2,
  "message": "参数无效"
}
```

#### 停止字幕化任务

```http
POST /api/rpc/stop-subtitize
```

**请求体:**
```json
{
  "task_id": 1
}
```

**响应示例:**
```json
{
  "success": true,
  "task_id": 1,
  "message": "任务已停止"
}
```

#### 获取任务状态

```http
GET /api/rpc/get-status
```

**响应示例:**

空闲状态:
```json
{
  "status": "idle"
}
```

任务运行中:
```json
{
  "status": "busy",
  "current_task": {
    "task_id": 1,
    "state": "transcribing",
    "progress": 4500,  // 万分制 (0-10000)
    "video_path": "/data/video.mp4",
    "message": "正在转录"
  }
}
```

### SignalR（可选）

#### 设置 Master URL

```http
GET /set-master?url=<master_url>
```

**参数:**
- `url`: Master SignalR Hub 的 URL

**响应示例:**
```json
{
  "success": true,
  "message": "已连接到 Master: http://master:5000/hub",
  "master_url": "http://master:5000/hub"
}
```

#### 断开 Master 连接

```http
GET /disconnect-master
POST /disconnect-master
```

**响应示例:**
```json
{
  "success": true,
  "message": "已断开与 Master 的连接"
}
```

## 任务状态说明

### 任务状态 (state)

| 状态 | 说明 |
|------|------|
| idle | 空闲 |
| queued | 排队中 |
| transcribing | 转录中 |
| optimizing | 优化中 |
| translating | 翻译中 |
| completed | 完成 |
| failed | 失败 |
| cancelled | 已取消 |

### 进度值 (progress)

进度使用万分制表示：
- `0` - 0%
- `5000` - 50%
- `10000` - 100%

### 进度阶段划分

- **0-5000** (0-50%): 转录阶段
  - 0-500: 准备音频
  - 500-1000: 音频转换
  - 1000-5000: 语音转录
- **5000-6000** (50-60%): 字幕分割
- **6000-7000** (60-70%): 字幕优化（如启用）
- **7000-10000** (70-100%): 字幕翻译（如启用）

## 错误码

| 错误码 | 说明 |
|--------|------|
| -1 | 已有任务正在运行 |
| -2 | 参数无效 |
| -3 | 启动执行器失败 |

## 完整示例

### Python 示例

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# 1. 启动任务
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "/data/video.mp4",
        "raw_subtitle_path": "/data/video.srt",
        "translated_subtitle_path": "/data/video.translated.srt",
        "language": "en"
    }
)

result = response.json()
if result["success"]:
    task_id = result["task_id"]
    print(f"任务已启动: {task_id}")

    # 2. 轮询任务状态
    while True:
        status = requests.get(f"{BASE_URL}/api/rpc/get-status").json()

        if status["status"] == "idle":
            print("任务完成")
            break

        if status["status"] == "busy":
            task = status["current_task"]
            progress = task["progress"] / 100  # 转换为百分比
            print(f"进度: {progress:.1f}% - {task['state']}")

        time.sleep(2)
else:
    print(f"启动失败: {result['message']}")
```

### cURL 示例

```bash
# 启动任务
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/video.mp4",
    "raw_subtitle_path": "/data/video.srt",
    "translated_subtitle_path": "/data/video.translated.srt",
    "language": "Auto"
  }'

# 查询状态
curl http://localhost:5000/api/rpc/get-status

# 停止任务
curl -X POST http://localhost:5000/api/rpc/stop-subtitize \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

### JavaScript 示例

```javascript
const BASE_URL = 'http://localhost:5000';

// 启动任务
async function startTask(videoPath, language = 'Auto') {
  const response = await fetch(`${BASE_URL}/api/rpc/start-subtitize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_path: videoPath,
      raw_subtitle_path: `${videoPath}.srt`,
      translated_subtitle_path: `${videoPath}.translated.srt`,
      language: language
    })
  });

  return await response.json();
}

// 查询状态
async function getStatus() {
  const response = await fetch(`${BASE_URL}/api/rpc/get-status`);
  return await response.json();
}

// 使用示例
const result = await startTask('/data/video.mp4', 'en');
console.log('Task ID:', result.task_id);
```

## 注意事项

1. **单任务限制**: 同一时间只能运行一个字幕化任务
2. **路径要求**: 所有路径必须是容器内可访问的绝对路径
3. **语言参数**: 不提供 language 参数时，使用配置文件中的设置
4. **进度更新**: 建议每 1-2 秒查询一次状态，避免过于频繁

## 相关文档

- [语言参数详解](language-parameter-support.md)
- [错误处理指南](error-handling.md)
- [部署文档](../deployment/docker-deployment.md)
