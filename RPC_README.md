# VideoCaptioner RPC 系统

## 概述

VideoCaptioner 实现了基于 Flask + SignalR 的控制反转式 RPC 系统。应用作为被调用的服务启动，通过 Flask API 接收控制命令，并通过 SignalR 客户端连接到 Master 服务器进行双向通信。

## 架构

```
┌─────────────────┐         HTTP GET          ┌─────────────────┐
│                 │  /set-master?url=...      │                 │
│  SrcMan Master  │ ───────────────────────>  │ VideoCaptioner  │
│                 │                            │  Flask Server   │
└─────────────────┘                            └─────────────────┘
         │                                              │
         │                                              │
         │        SignalR Connection (WebSocket)        │
         │ <─────────────────────────────────────────> │
         │                                              │
         │  RPC Calls, Progress, Events, Logs          │
         └──────────────────────────────────────────────┘
```

## 启动 RPC 服务器

### 独立模式

```bash
# 启动独立的 RPC 服务器
uv run python rpc_server.py
```

服务器将在 `http://0.0.0.0:5000` 上监听。

### 集成模式

在主应用中启动 RPC 服务器：

```python
from app.rpc import start_rpc_server, stop_rpc_server
from app.common.config import cfg

# 启动 RPC 服务器
if cfg.rpc_enabled.value:
    start_rpc_server(
        host=cfg.rpc_host.value,
        port=cfg.rpc_port.value
    )

# 停止 RPC 服务器
stop_rpc_server()
```

## API 端点

### GET /health

健康检查端点。

**响应:**
```json
{
  "success": true,
  "status": "healthy"
}
```

### GET /status

获取当前连接状态。

**响应:**
```json
{
  "success": true,
  "is_connected": false,
  "master_url": null
}
```

### GET /set-master

设置 Master SignalR Hub URL 并建立连接。

**参数:**
- `url` (必需): Master SignalR Hub 的 URL

**示例:**
```bash
curl "http://localhost:5000/set-master?url=https://master-server.com/signalrhub"
```

**响应:**
```json
{
  "success": true,
  "message": "已连接到 Master: https://master-server.com/signalrhub",
  "master_url": "https://master-server.com/signalrhub"
}
```

### GET /disconnect-master

断开与 Master 的连接。

**响应:**
```json
{
  "success": true,
  "message": "已断开与 Master 的连接"
}
```

## SignalR RPC 方法

### Master 可调用的方法

应用提供以下 RPC 方法供 Master 调用：

#### GetInfo

获取应用信息。

**返回:**
```json
{
  "app_name": "VideoCaptioner",
  "version": "v1.4.0",
  "description": "视频字幕生成和翻译工具"
}
```

#### GetStatus

获取应用当前状态。

**返回:**
```json
{
  "status": "running",
  "tasks": {
    "active": 0,
    "queued": 0,
    "completed": 0
  }
}
```

#### ProcessVideo

处理视频（生成字幕）。

**参数:**
- `video_path` (string): 视频文件路径
- `output_path` (string, 可选): 输出路径
- `options` (object, 可选): 处理选项

**返回:**
```json
{
  "success": true,
  "task_id": "task_123456",
  "video_path": "/path/to/video.mp4",
  "output_path": "/path/to/video.mp4.srt"
}
```

#### GetTasks

获取任务列表。

**返回:**
```json
[]
```

#### CancelTask

取消指定任务。

**参数:**
- `task_id` (string): 任务 ID

**返回:**
```json
{
  "success": true,
  "task_id": "task_123456",
  "message": "任务已取消"
}
```

### 应用发送的事件

应用可以向 Master 发送以下类型的消息：

#### Progress

任务进度更新。

```json
{
  "task_id": "task_123456",
  "progress": 50.0,
  "message": "正在生成字幕"
}
```

#### Event

自定义事件。

```json
{
  "event": "task_completed",
  "data": {
    "task_id": "task_123456",
    "result": "success"
  }
}
```

#### Log

日志消息。

```json
{
  "level": "info",
  "message": "处理开始"
}
```

#### MethodResponse

RPC 方法调用响应。

```json
{
  "method": "ProcessVideo",
  "success": true,
  "result": { ... }
}
```

## 使用示例

### Master 端伪代码

```python
# 1. 告诉 VideoCaptioner 连接到 Master
requests.get("http://videocaptioner:5000/set-master?url=https://master/signalrhub")

# 2. 等待 VideoCaptioner 连接到 SignalR Hub

# 3. 通过 SignalR 调用 RPC 方法
result = hub.invoke("ProcessVideo", "/path/to/video.mp4", None, {})

# 4. 接收进度更新
@hub.on("Progress")
def on_progress(data):
    print(f"进度: {data['progress']}% - {data['message']}")

# 5. 接收完成事件
@hub.on("Event")
def on_event(data):
    if data['event'] == 'task_completed':
        print("任务完成!")
```

## 配置

在 `app/common/config.py` 中添加了以下配置项：

- `rpc_enabled`: 是否启用 RPC 服务器（默认: False）
- `rpc_host`: RPC 服务器监听地址（默认: "0.0.0.0"）
- `rpc_port`: RPC 服务器监听端口（默认: 5000）
- `rpc_master_url`: Master SignalR Hub URL（默认: ""）

## 测试

运行测试脚本：

```bash
# 终端 1: 启动 RPC 服务器
uv run python rpc_server.py

# 终端 2: 运行测试
uv run python test_rpc.py
```

## 扩展 RPC 方法

要添加新的 RPC 方法：

1. 在 `app/rpc/rpc_service.py` 的 `VideoCaptionerRPCService` 类中添加方法
2. 在 `_register_methods()` 中注册该方法
3. 使用 `rpc_handler.send_progress()`, `send_event()`, `send_log()` 等方法发送实时反馈

示例：

```python
def my_new_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """自定义 RPC 方法"""
    try:
        # 执行业务逻辑
        rpc_handler.send_log("info", f"开始处理: {param1}")

        # 发送进度
        rpc_handler.send_progress("task_id", 50, "处理中")

        # 返回结果
        return {"success": True, "result": "完成"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 在 _register_methods() 中注册
rpc_handler.register_method("MyNewMethod", self.my_new_method)
```

## 安全注意事项

1. **认证**: 当前实现不包含认证机制，建议在生产环境中添加 API 密钥或其他认证方式
2. **网络隔离**: 建议将 RPC 服务器部署在内网环境中
3. **输入验证**: 对所有 RPC 方法的输入参数进行严格验证
4. **日志审计**: 记录所有 RPC 调用和状态变更

## 故障排查

### 连接失败

检查：
- Master URL 是否正确
- 网络连接是否正常
- 防火墙是否阻止了连接

### SignalR 重连

客户端配置了自动重连机制：
- 初次重连: 立即
- 后续重连间隔: 2s, 5s, 10s, 30s

### 查看日志

RPC 服务器使用 Python logging 模块，可以通过配置日志级别查看详细信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
