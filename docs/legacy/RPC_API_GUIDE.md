# RPC API 使用指南

## 快速开始

### 1. 启动 RPC 服务器

```bash
# 方式 1: 使用独立的 RPC 服务器
uv run python rpc_server.py

# 方式 2: 在配置中启用 RPC，然后启动主程序
# 在 settings.json 中设置:
# "RPC": {
#   "Enabled": true,
#   "Host": "0.0.0.0",
#   "Port": 5000
# }
uv run python main.py
```

服务器启动后会显示：
```
Flask API 服务器已启动: http://0.0.0.0:5000
访问 Swagger UI: http://0.0.0.0:5000/api/docs
```

### 2. 访问 Swagger UI

在浏览器中打开 http://localhost:5000/api/docs

你会看到一个交互式的 API 文档界面，可以直接在浏览器中测试所有 API。

### 3. 使用 API

#### 方式 A: 通过 Swagger UI（推荐用于调试）

1. 打开 http://localhost:5000/api/docs
2. 找到你想调用的 API（如 `POST /api/rpc/start-subtitize`）
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

#### 方式 B: 通过 Python 脚本

```bash
# 运行提供的测试脚本
uv run python test_rpc_api.py
```

#### 方式 C: 通过 curl 命令

```bash
# 健康检查
curl http://localhost:5000/health

# 获取状态
curl http://localhost:5000/api/rpc/get-status

# 启动任务
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "D:\\test\\video.mp4",
    "raw_subtitle_path": "D:\\test\\raw.srt",
    "translated_subtitle_path": "D:\\test\\translated.srt"
  }'
```

## API 端点列表

### 系统相关

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status` | GET | 获取 Worker 和连接状态 |

### SignalR 连接

| 端点 | 方法 | 描述 |
|------|------|------|
| `/set-master` | GET | 连接到 Master SignalR Hub |
| `/disconnect-master` | GET/POST | 断开与 Master 的连接 |

### RPC 方法

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/rpc/start-subtitize` | POST | 启动字幕化任务 |
| `/api/rpc/stop-subtitize` | POST | 停止字幕化任务 |
| `/api/rpc/get-status` | GET | 获取任务状态 |

## API 详细说明

### POST /api/rpc/start-subtitize

启动一个新的字幕化任务。

**请求体:**
```json
{
  "video_path": "视频文件路径",
  "raw_subtitle_path": "原始字幕输出路径",
  "translated_subtitle_path": "翻译字幕输出路径"
}
```

**响应:**
```json
{
  "success": true,
  "task_id": 1,
  "message": "任务已启动: task_id=1"
}
```

**task_id 说明:**
- `> 0`: 成功启动，返回任务 ID
- `-1`: 已有任务正在运行
- `-2`: 参数无效
- `-3`: 启动执行器失败

### POST /api/rpc/stop-subtitize

停止一个正在运行的任务。

**请求体:**
```json
{
  "task_id": 1
}
```

**响应:**
```json
{
  "success": true,
  "task_id": 1,
  "message": "任务已停止"
}
```

### GET /api/rpc/get-status

获取当前任务状态。

**响应:**
```json
{
  "status": "busy",
  "current_task": {
    "task_id": 1,
    "state": "transcribing",
    "progress": 2500,
    "video_path": "D:\\test\\video.mp4",
    "created_at": "2024-01-01T12:00:00",
    "started_at": "2024-01-01T12:00:05"
  }
}
```

**status 值:**
- `idle`: 空闲，没有任务
- `busy`: 忙碌，有任务正在运行

**progress 说明:**
- 使用万分制 (0-10000)
- 0-5000: 转录阶段
- 5000-6000: 分割字幕
- 6000-7000: 优化字幕
- 7000-10000: 翻译字幕

## 完整示例

### Python 示例

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# 1. 检查服务器健康
response = requests.get(f"{BASE_URL}/health")
print(f"Health: {response.json()}")

# 2. 启动任务
response = requests.post(
    f"{BASE_URL}/api/rpc/start-subtitize",
    json={
        "video_path": "D:\\test\\video.mp4",
        "raw_subtitle_path": "D:\\test\\raw.srt",
        "translated_subtitle_path": "D:\\test\\translated.srt",
    }
)

result = response.json()
if result["success"]:
    task_id = result["task_id"]
    print(f"任务已启动: {task_id}")

    # 3. 轮询任务状态
    while True:
        status_response = requests.get(f"{BASE_URL}/api/rpc/get-status")
        status = status_response.json()

        if status["status"] == "idle":
            print("任务已完成")
            break

        task = status.get("current_task")
        if task:
            progress = task["progress"] / 100  # 转换为百分比
            state = task["state"]
            print(f"进度: {progress:.2f}% - {state}")

        time.sleep(2)
else:
    print(f"启动失败: {result['message']}")
```

### JavaScript 示例

```javascript
const BASE_URL = 'http://localhost:5000';

// 启动任务
async function startTask() {
  const response = await fetch(`${BASE_URL}/api/rpc/start-subtitize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      video_path: 'D:\\test\\video.mp4',
      raw_subtitle_path: 'D:\\test\\raw.srt',
      translated_subtitle_path: 'D:\\test\\translated.srt',
    }),
  });

  const result = await response.json();
  if (result.success) {
    console.log(`任务已启动: ${result.task_id}`);
    return result.task_id;
  } else {
    console.error(`启动失败: ${result.message}`);
    return null;
  }
}

// 获取状态
async function getStatus() {
  const response = await fetch(`${BASE_URL}/api/rpc/get-status`);
  const status = await response.json();
  return status;
}

// 使用
startTask().then(async (taskId) => {
  if (taskId) {
    // 轮询状态
    const interval = setInterval(async () => {
      const status = await getStatus();
      if (status.status === 'idle') {
        console.log('任务已完成');
        clearInterval(interval);
      } else if (status.current_task) {
        const progress = status.current_task.progress / 100;
        console.log(`进度: ${progress.toFixed(2)}% - ${status.current_task.state}`);
      }
    }, 2000);
  }
});
```

## 注意事项

1. **单任务限制**: Worker 节点同时只能运行一个任务
2. **进度精度**: 进度使用万分制（0-10000）
3. **状态轮询**: 建议每 1-2 秒轮询一次状态
4. **路径格式**: Windows 路径需要使用双反斜杠 `\\` 或单正斜杠 `/`
5. **配置依赖**: 确保在配置文件中正确设置了转录和翻译相关参数

## 故障排查

### 问题：无法连接到服务器

**解决方案:**
1. 确认服务器已启动
2. 检查端口是否被占用
3. 检查防火墙设置

### 问题：任务启动失败（task_id = -2）

**解决方案:**
检查请求参数是否正确，必须提供：
- `video_path`: 有效的视频文件路径
- `raw_subtitle_path`: 原始字幕输出路径

### 问题：已有任务运行（task_id = -1）

**解决方案:**
1. 等待当前任务完成
2. 或使用 `/api/rpc/stop-subtitize` 停止当前任务

## 更多信息

详细的实现说明请参考：[SUBTITIZE_RPC_IMPLEMENTATION.md](SUBTITIZE_RPC_IMPLEMENTATION.md)
