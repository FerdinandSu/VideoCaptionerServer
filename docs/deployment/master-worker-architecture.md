# Master-Worker 架构说明

## 架构概述

VideoCaptioner 支持 Master-Worker 分布式架构，通过 SignalR 实现任务调度和状态同步。

```
┌─────────────┐
│   Master    │  任务调度中心
│   (可选)    │  - 管理任务队列
└──────┬──────┘  - 分发任务到 Worker
       │          - 收集 Worker 状态
       │ SignalR
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐  ┌──▼──┐
│  W1 │ │  W2 │ │  W3 │  │  W4 │  Worker 节点
└─────┘ └─────┘ └─────┘  └─────┘  - 执行字幕化任务
                                    - 上报进度和结果
```

## 运行模式

VideoCaptioner 支持两种运行模式：

### 1. 独立模式（默认）

Worker 节点独立运行，通过 REST API 接收任务。

```yaml
# docker-compose.yml
services:
  videocaptioner:
    environment:
      - RPC_ENABLED=true
      - RPC_HOST=0.0.0.0
      - RPC_PORT=5000
```

**使用场景:**
- 单机部署
- 简单的任务处理
- 直接 API 调用

### 2. Master-Worker 模式

Worker 连接到 Master，由 Master 统一调度任务。

```yaml
# docker-compose.yml
services:
  videocaptioner:
    environment:
      - RPC_ENABLED=true
      - RPC_MASTER_URL=http://master:5000/signalrhub
```

**使用场景:**
- 分布式部署
- 任务负载均衡
- 统一任务管理

## Master 实现规约

### Master 职责

Master 服务需要实现以下功能：

#### 1. SignalR Hub

提供 SignalR Hub 用于与 Worker 通信。

**Hub 端点**: `/signalrhub`

**Hub 方法（Worker → Master）:**

```csharp
// Worker 注册
Task RegisterWorker(string workerId, string endpoint);

// Worker 状态更新
Task UpdateWorkerStatus(string workerId, WorkerStatus status);

// 任务进度更新
Task UpdateTaskProgress(int taskId, int progress, string state);

// 任务完成通知
Task TaskCompleted(int taskId, string rawSubtitlePath, string translatedSubtitlePath);

// 任务失败通知
Task TaskFailed(int taskId, string error);
```

**Hub 方法（Master → Worker）:**

```csharp
// 分发任务
Task StartSubtitize(int taskId, string videoPath, string rawSubtitlePath,
                    string translatedSubtitlePath, string language);

// 取消任务
Task StopSubtitize(int taskId);

// Ping/健康检查
Task Ping();
```

#### 2. Worker 注册管理

维护 Worker 注册表：

```json
{
  "workers": [
    {
      "worker_id": "worker-1",
      "endpoint": "http://worker1:5000",
      "status": "idle",
      "last_seen": "2025-12-15T12:00:00Z",
      "capabilities": {
        "gpu_available": true,
        "concurrent_tasks": 1
      }
    }
  ]
}
```

#### 3. 任务调度

实现任务队列和分发逻辑：

```python
class MasterScheduler:
    def enqueue_task(self, task):
        """添加任务到队列"""
        pass

    def assign_task_to_worker(self, task, worker):
        """分配任务给 Worker"""
        # 调用 Worker 的 StartSubtitize Hub 方法
        await hub.invoke("StartSubtitize", task)

    def on_worker_idle(self, worker_id):
        """Worker 空闲时触发"""
        # 从队列取任务分配给该 Worker
        pass
```

#### 4. 任务状态管理

维护任务状态表：

```json
{
  "tasks": [
    {
      "task_id": 1,
      "status": "processing",
      "worker_id": "worker-1",
      "video_path": "/data/video.mp4",
      "progress": 4500,
      "state": "transcribing",
      "created_at": "2025-12-15T12:00:00Z",
      "started_at": "2025-12-15T12:00:05Z"
    }
  ]
}
```

### Master API 端点

Master 应提供以下 REST API：

```
POST   /api/tasks                 # 创建任务
GET    /api/tasks/:id             # 查询任务状态
DELETE /api/tasks/:id             # 取消任务
GET    /api/workers               # 查询 Worker 列表
GET    /api/workers/:id           # 查询 Worker 状态
```

### Master 配置示例

```json
{
  "signalr": {
    "hub_url": "/signalrhub",
    "port": 5000
  },
  "scheduler": {
    "max_retries": 3,
    "task_timeout": 3600,
    "worker_timeout": 60
  }
}
```

## Worker 实现

Worker 端已在 VideoCaptioner 中实现，主要组件：

### SignalR 客户端

```python
# app/rpc/signalr_client.py
class SignalRClient:
    def connect(self, master_url: str) -> bool:
        """连接到 Master SignalR Hub"""

    def on_start_subtitize(self, callback):
        """注册任务开始回调"""

    def on_stop_subtitize(self, callback):
        """注册任务停止回调"""

    def send_progress(self, task_id, progress, state):
        """发送进度到 Master"""

    def send_completed(self, task_id, paths):
        """发送完成通知"""

    def send_failed(self, task_id, error):
        """发送失败通知"""
```

### RPC 服务

```python
# app/rpc/rpc_service.py
class RPCService:
    def start_subtitize(self, video_path, raw_subtitle_path,
                       translated_subtitle_path, language=None):
        """启动字幕化任务（可由 Master 或 API 调用）"""

    def stop_subtitize(self, task_id):
        """停止任务"""

    def get_status(self):
        """获取 Worker 状态"""
```

## 部署架构

### 单 Master + 多 Worker

```yaml
version: '3.8'

services:
  master:
    image: your-master-image
    ports:
      - "5000:5000"
    environment:
      - SIGNALR_HUB=/signalrhub

  worker1:
    image: videocaptioner:latest
    environment:
      - RPC_MASTER_URL=http://master:5000/signalrhub
    volumes:
      - ./data:/data
      - ./models:/app/AppData/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1

  worker2:
    image: videocaptioner:latest
    environment:
      - RPC_MASTER_URL=http://master:5000/signalrhub
    volumes:
      - ./data:/data
      - ./models:/app/AppData/models
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
```

### Worker 注册流程

```
1. Worker 启动
   ↓
2. 读取 RPC_MASTER_URL 配置
   ↓
3. 连接到 Master SignalR Hub
   ↓
4. 发送 RegisterWorker(worker_id, endpoint)
   ↓
5. Master 记录 Worker 信息
   ↓
6. Worker 进入待命状态
   ↓
7. Master 分发任务时调用 Worker.StartSubtitize()
   ↓
8. Worker 执行任务并持续上报进度
   ↓
9. 任务完成后通知 Master
```

## 通信协议

### 任务生命周期

```
Master                Worker
  │                    │
  ├──StartSubtitize──>│  1. Master 分发任务
  │                    │
  │<──UpdateProgress──│  2. Worker 上报进度（定时）
  │<──UpdateProgress──│
  │<──UpdateProgress──│
  │                    │
  │<──TaskCompleted───│  3. Worker 完成任务
  │                    │
  ├──Acknowledge────>│  4. Master 确认
```

### 错误处理

```
Master                Worker
  │                    │
  ├──StartSubtitize──>│
  │                    │
  │<──TaskFailed──────│  Worker 失败
  │                    │
  ├──Retry (Worker2)─>│  Master 重试（可选）
```

## API 对接示例

### 连接到 Master

```bash
# 启动 Worker 并连接 Master
curl -X GET "http://worker:5000/set-master?url=http://master:5000/signalrhub"
```

**响应:**
```json
{
  "success": true,
  "message": "已连接到 Master: http://master:5000/signalrhub",
  "master_url": "http://master:5000/signalrhub"
}
```

### 断开连接

```bash
curl -X POST http://worker:5000/disconnect-master
```

### 查询连接状态

```bash
curl http://worker:5000/status
```

**响应:**
```json
{
  "success": true,
  "is_connected": true,
  "master_url": "http://master:5000/signalrhub",
  "status": "idle"
}
```

## 监控和日志

### Worker 日志

Worker 会记录以下关键事件：

```
2025-12-15 12:00:00 - INFO - 连接到 Master: http://master:5000/signalrhub
2025-12-15 12:00:05 - INFO - 收到任务: task_id=1
2025-12-15 12:00:10 - INFO - 任务进度: 25% - transcribing
2025-12-15 12:05:00 - INFO - 任务完成: task_id=1
```

### Master 监控指标

建议 Master 监控以下指标：

- Worker 在线数量
- 任务队列长度
- 平均任务耗时
- Worker 失败率
- 任务重试次数

## 故障恢复

### Worker 断线重连

Worker 自动重连机制：

```python
# 自动重连配置
RECONNECT_INTERVAL = 5  # 秒
MAX_RECONNECT_ATTEMPTS = 10
```

### Master 故障

Master 故障时，Worker 可以：

1. **独立模式运行**: 继续接受 REST API 请求
2. **等待重连**: 定期尝试重新连接 Master
3. **任务保留**: 当前任务继续执行，完成后缓存结果

## 安全考虑

### 认证

建议在 Master-Worker 通信中使用认证：

```python
# Worker 连接时提供 Token
headers = {
    "Authorization": f"Bearer {WORKER_TOKEN}"
}
```

### 加密

生产环境建议使用 WSS（WebSocket Secure）：

```
wss://master:5000/signalrhub
```

## 示例实现

完整的 Master 示例实现请参考：
- [Master 示例项目](https://github.com/example/videocaptioner-master)（待补充）

## 相关文档

- [RPC API 参考](../api/rpc-api.md)
- [Docker 部署](docker-deployment.md)
- [配置说明](../configuration/settings.md)

---

**最后更新**: 2025-12-15
