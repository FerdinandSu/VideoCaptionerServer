# RPC 系统快速开始指南

## 快速测试

### 1. 独立模式测试

终端 1 - 启动 RPC 服务器：
```bash
uv run python rpc_server.py
```

终端 2 - 运行测试：
```bash
uv run python test_rpc.py
```

### 2. 测试 API 端点

```bash
# 健康检查
curl http://localhost:5000/health

# 查看状态
curl http://localhost:5000/status

# 设置 Master URL (示例，会连接失败但不影响测试)
curl "http://localhost:5000/set-master?url=https://example.com/signalrhub"

# 断开连接
curl http://localhost:5000/disconnect-master
```

### 3. 在主应用中启用

编辑配置或通过界面启用：

```python
from app.common.config import cfg

# 启用 RPC
cfg.set(cfg.rpc_enabled, True)
cfg.set(cfg.rpc_host, "0.0.0.0")
cfg.set(cfg.rpc_port, 5000)

# 启动应用
# uv run python main.py
```

或直接修改 `AppData/settings.json`：

```json
{
  "RPC.Enabled": true,
  "RPC.Host": "0.0.0.0",
  "RPC.Port": 5000
}
```

## 使用流程

```
1. VideoCaptioner 启动 (RPC 已启用)
   └─> Flask API 在 http://0.0.0.0:5000 监听

2. SrcMan Master 调用 API
   GET http://videocaptioner:5000/set-master?url=https://master/signalrhub
   └─> VideoCaptioner 创建 SignalR 客户端连接到 Master

3. Master 通过 SignalR 调用 RPC 方法
   Master.invoke("GetInfo")
   └─> VideoCaptioner 返回应用信息

4. VideoCaptioner 发送实时反馈
   - Progress: 任务进度更新
   - Event: 自定义事件
   - Log: 日志消息

5. 断开连接 (可选)
   GET http://videocaptioner:5000/disconnect-master
   └─> SignalR 连接断开
```

## 示例代码

### Master 端 (SrcMan Master)

```python
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder

# 1. 让 VideoCaptioner 连接到 Master
response = requests.get(
    "http://videocaptioner:5000/set-master",
    params={"url": "https://master-server.com/signalrhub"}
)

# 2. 在 Master 的 SignalR Hub 中处理消息
class MasterHub:
    def on_progress(self, data):
        print(f"进度: {data['task_id']} - {data['progress']}%")

    def on_event(self, data):
        print(f"事件: {data['event']} - {data['data']}")

    def on_log(self, data):
        print(f"日志: [{data['level']}] {data['message']}")

# 3. 调用 VideoCaptioner 的方法
hub.invoke("ProcessVideo", "/path/to/video.mp4", None, {})
```

### VideoCaptioner 端 (添加自定义 RPC 方法)

```python
# app/rpc/rpc_service.py

def my_custom_method(self, param1: str, param2: int) -> Dict[str, Any]:
    """自定义 RPC 方法"""
    from .rpc_handler import rpc_handler

    try:
        # 发送日志
        rpc_handler.send_log("info", f"开始处理: {param1}")

        # 执行业务逻辑
        task_id = f"task_{param1}"

        # 发送进度
        rpc_handler.send_progress(task_id, 0, "初始化")
        rpc_handler.send_progress(task_id, 50, "处理中")
        rpc_handler.send_progress(task_id, 100, "完成")

        # 发送事件
        rpc_handler.send_event("task_completed", {"task_id": task_id})

        return {"success": True, "result": "处理完成"}

    except Exception as e:
        return {"success": False, "error": str(e)}

# 在 _register_methods() 中注册
rpc_handler.register_method("MyCustomMethod", self.my_custom_method)
```

## 常见问题

**Q: RPC 服务器无法启动？**

A: 检查端口是否被占用：
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

**Q: SignalR 连接失败？**

A:
1. 确认 Master URL 正确
2. 检查网络连接
3. 查看日志输出
4. 尝试手动测试连接

**Q: 如何查看详细日志？**

A: 在启动应用前设置日志级别：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Q: 如何在生产环境部署？**

A:
1. 使用专业的 WSGI 服务器（如 gunicorn）
2. 添加认证机制
3. 配置 HTTPS
4. 使用反向代理（如 nginx）

## 更多信息

详细文档请参考：[RPC_README.md](./RPC_README.md)
