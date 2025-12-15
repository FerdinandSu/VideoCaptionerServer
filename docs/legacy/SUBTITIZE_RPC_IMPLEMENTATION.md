# 字幕化 RPC 方法实现说明

## 概述

已实现完整的字幕化 Worker 节点功能，支持作为 Master 的 Worker 节点进行负载均衡处理。每个 Worker 节点一次只处理一个任务。

**支持两种调用方式**：
1. **SignalR RPC** - Master 通过 SignalR Hub 调用 Worker 方法
2. **REST API** - 通过 HTTP REST API 直接调用（方便调试和测试）

## 快速开始

### 启动 RPC 服务器

```bash
# 启动 RPC 服务器（默认端口 5000）
uv run python rpc_server.py
```

服务器启动后：
- **REST API**: http://localhost:5000
- **Swagger UI**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/health

### 使用 Swagger UI 测试

访问 http://localhost:5000/api/docs 可以看到完整的 API 文档和交互式测试界面。

主要 API 端点：
- `POST /api/rpc/start-subtitize` - 启动字幕化任务
- `POST /api/rpc/stop-subtitize` - 停止字幕化任务
- `GET /api/rpc/get-status` - 获取任务状态
- `GET /set-master?url=xxx` - 连接到 Master
- `GET /status` - 获取 Worker 状态

### 测试脚本

```bash
# 运行测试脚本
uv run python test_rpc_api.py
```

## 已实现的核心组件

### 1. 任务管理器 (task_manager.py)

**SubtitizeTaskManager** - 单例模式，管理单个正在运行的字幕化任务

- **状态管理**: 跟踪任务状态（空闲、排队、转录中、优化中、翻译中、完成、失败、取消）
- **进度跟踪**: 万分制进度（0-10000）
- **回调机制**: 支持进度、完成、失败回调

**任务状态**:
- `idle` - 空闲
- `queued` - 排队中
- `transcribing` - 转录中
- `optimizing` - 优化中
- `translating` - 翻译中
- `completed` - 完成
- `failed` - 失败
- `cancelled` - 取消

### 2. 字幕化执行器 (subtitize_executor.py)

**SubtitizeExecutor** - 执行字幕化任务的核心逻辑

执行流程：
1. **转录阶段** (0-50%):
   - 视频转音频
   - 调用 ASR 转录
   - 生成原始字幕

2. **字幕处理阶段** (50-100%):
   - 分割字幕 (50-60%)
   - 优化字幕 (60-70%)
   - 翻译字幕 (70-100%)

### 3. RPC 服务 (rpc_service.py)

**VideoCaptionerRPCService** - 提供 RPC 方法和回调

## RPC 方法

### StartSubtitize

启动字幕化任务。

**签名:**
```python
def start_subtitize(
    video_path: str,
    raw_subtitle_path: str,
    translated_subtitle_path: str
) -> int
```

**参数:**
- `video_path`: 视频文件路径
- `raw_subtitle_path`: 原始字幕输出路径
- `translated_subtitle_path`: 翻译字幕输出路径

**返回值:**
- **正数**: 任务 ID (成功)
- **-1**: 已有任务正在运行
- **-2**: 参数无效
- **-3**: 启动执行器失败

**示例 (Master 端调用):**
```python
task_id = hub.invoke("StartSubtitize",
    "/path/to/video.mp4",
    "/path/to/raw_subtitle.srt",
    "/path/to/translated_subtitle.srt"
)

if task_id > 0:
    print(f"任务已启动: task_id={task_id}")
elif task_id == -1:
    print("Worker 正忙，已有任务正在运行")
elif task_id == -2:
    print("参数无效")
elif task_id == -3:
    print("启动执行器失败")
```

### StopSubtitize

停止指定的字幕化任务。

**签名:**
```python
def stop_subtitize(task_id: int) -> Dict[str, Any]
```

**参数:**
- `task_id`: 任务 ID

**返回值:**
```python
{
    "success": bool,      # 是否成功停止
    "task_id": int,       # 任务 ID
    "message": str        # 消息或错误信息
}
```

**示例 (Master 端调用):**
```python
result = hub.invoke("StopSubtitize", 1)

if result["success"]:
    print(f"任务已停止: {result['message']}")
else:
    print(f"停止失败: {result['message']}")
```

### GetStatus

获取 Worker 当前状态。

**返回值:**
```python
# 空闲状态
{
    "status": "idle",
    "current_task": None
}

# 忙碌状态
{
    "status": "busy",
    "current_task": {
        "task_id": int,
        "state": str,          # 任务状态
        "progress": int,       # 进度（万分制）
        "video_path": str,
        "created_at": str,     # ISO 格式
        "started_at": str      # ISO 格式
    }
}
```

## RPC 回调

Worker 向 Master 发送的回调通知。

### SubtitizeProgress

任务进度更新回调。

**数据:**
```python
{
    "task_id": int,
    "current_progress": int,     # 万分制进度 (0-10000)
    "current_state": str,        # 当前状态
    "eta": str                   # 预计完成时间 (ISO 格式，可选)
}
```

**进度范围:**
- 0-5000: 转录阶段
- 5000-6000: 分割字幕
- 6000-7000: 优化字幕
- 7000-10000: 翻译字幕

**示例 (Master 端接收):**
```python
@hub.on("SubtitizeProgress")
def on_progress(data):
    task_id = data["task_id"]
    progress = data["current_progress"] / 100  # 转换为百分比
    state = data["current_state"]
    eta = data.get("eta")

    print(f"任务 {task_id}: {progress:.2f}% - {state}")
```

### SubtitizeCompleted

任务完成回调。

**数据:**
```python
{
    "task_id": int,
    "video_path": str,
    "raw_subtitle_path": str,
    "translated_subtitle_path": str
}
```

**示例 (Master 端接收):**
```python
@hub.on("SubtitizeCompleted")
def on_completed(data):
    task_id = data["task_id"]
    raw_path = data["raw_subtitle_path"]
    trans_path = data["translated_subtitle_path"]

    print(f"任务 {task_id} 完成!")
    print(f"原始字幕: {raw_path}")
    print(f"翻译字幕: {trans_path}")
```

### SubtitizeFaulted

任务失败回调。

**数据:**
```python
{
    "task_id": int,
    "video_path": str,
    "fault": str               # 错误信息
}
```

**示例 (Master 端接收):**
```python
@hub.on("SubtitizeFaulted")
def on_faulted(data):
    task_id = data["task_id"]
    video_path = data["video_path"]
    fault = data["fault"]

    print(f"任务 {task_id} 失败!")
    print(f"视频: {video_path}")
    print(f"错误: {fault}")
```

## Master 端完整示例

```python
from signalrcore.hub_connection_builder import HubConnectionBuilder
import requests

# 1. 创建 SignalR Hub 服务器
hub = HubConnectionBuilder() \
    .with_url("https://master-server.com/signalrhub") \
    .build()

# 2. 注册回调处理器
@hub.on("SubtitizeProgress")
def on_progress(data):
    progress = data["current_progress"] / 100
    print(f"进度: {progress:.2f}% - {data['current_state']}")

@hub.on("SubtitizeCompleted")
def on_completed(data):
    print(f"完成: {data['translated_subtitle_path']}")

@hub.on("SubtitizeFaulted")
def on_faulted(data):
    print(f"失败: {data['fault']}")

# 3. 启动 Hub
hub.start()

# 4. 让 Worker 连接到 Master
response = requests.get(
    "http://worker-ip:5000/set-master",
    params={"url": "https://master-server.com/signalrhub"}
)

# 5. 调用 RPC 方法
task_id = hub.invoke("StartSubtitize",
    "/videos/sample.mp4",
    "/output/raw_subtitle.srt",
    "/output/translated_subtitle.srt"
)

if task_id > 0:
    print(f"任务已启动: {task_id}")
    # 等待回调...
else:
    print(f"启动失败: 错误代码 {task_id}")
```

## REST API 使用示例

### 启动任务

```bash
# 使用 curl
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "D:\\test\\video.mp4",
    "raw_subtitle_path": "D:\\test\\raw.srt",
    "translated_subtitle_path": "D:\\test\\translated.srt"
  }'
```

```python
# 使用 Python requests
import requests

response = requests.post(
    "http://localhost:5000/api/rpc/start-subtitize",
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
```

### 获取状态

```bash
# 使用 curl
curl http://localhost:5000/api/rpc/get-status
```

```python
# 使用 Python requests
response = requests.get("http://localhost:5000/api/rpc/get-status")
status = response.json()
print(f"状态: {status['status']}")
if status.get("current_task"):
    print(f"当前任务: {status['current_task']}")
```

### 停止任务

```bash
# 使用 curl
curl -X POST http://localhost:5000/api/rpc/stop-subtitize \
  -H "Content-Type: application/json" \
  -d '{"task_id": 1}'
```

```python
# 使用 Python requests
response = requests.post(
    "http://localhost:5000/api/rpc/stop-subtitize",
    json={"task_id": 1}
)

result = response.json()
print(result["message"])
```

### 连接到 Master

```bash
# 使用 curl
curl "http://localhost:5000/set-master?url=https://master-server.com/signalrhub"
```

```python
# 使用 Python requests
response = requests.get(
    "http://localhost:5000/set-master",
    params={"url": "https://master-server.com/signalrhub"}
)

result = response.json()
if result["success"]:
    print(f"已连接到 Master: {result['master_url']}")
```

## 配置

Worker 节点的配置从全局配置读取，包括：

- **转录配置**: 模型、语言、API密钥等
- **字幕配置**: 是否优化、是否翻译、目标语言等

确保在启动 Worker 前正确配置 `app/common/config.py` 中的相关参数。

## 注意事项

1. **单任务限制**: 每个 Worker 节点同时只能运行一个任务
2. **进度精度**: 进度使用万分制（0-10000），提供更精确的进度信息
3. **状态跟踪**: 任务状态实时更新，便于监控
4. **错误处理**: 所有错误都会通过 SubtitizeFaulted 回调报告
5. **取消支持**: 支持中途取消任务
6. **配置依赖**: 转录和翻译功能依赖全局配置，确保正确设置

## 测试

```bash
# 启动 RPC 服务器
uv run python rpc_server.py

# 在另一个终端测试导入
uv run python -c "from app.rpc import task_manager, subtitize_executor, rpc_service; print('成功')"
```

## 文件结构

```
app/rpc/
├── __init__.py                 # 模块导出
├── flask_server.py             # Flask API 服务器
├── signalr_client.py           # SignalR 客户端管理器
├── rpc_handler.py              # RPC 处理器
├── rpc_service.py              # RPC 服务实现 ✨
├── task_manager.py             # 任务管理器 ✨
└── subtitize_executor.py       # 字幕化执行器 ✨
```

✨ 标记的是本次实现的核心文件。
