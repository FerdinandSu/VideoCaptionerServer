# coding:utf-8
"""RPC 模块 - 基于 SignalR 的远程过程调用"""

from .flask_server import flask_server
from .rpc_handler import rpc_handler
from .rpc_service import rpc_service
from .signalr_client import signalr_client
from .subtitize_executor import subtitize_executor
from .task_manager import task_manager

__all__ = [
    "flask_server",
    "signalr_client",
    "rpc_handler",
    "rpc_service",
    "task_manager",
    "subtitize_executor",
]


def start_rpc_server(host: str = "0.0.0.0", port: int = 5000):
    """
    启动 RPC 服务器

    Args:
        host: Flask 服务器监听地址
        port: Flask 服务器监听端口
    """
    # 加载配置文件
    from app.common.config import cfg
    cfg.load('settings.json')

    # 初始化 RPC 处理器
    rpc_handler.initialize()

    # 启动 Flask API 服务器
    flask_server.start(host=host, port=port)


def stop_rpc_server():
    """停止 RPC 服务器"""
    # 断开 SignalR 连接
    signalr_client.disconnect()

    # 停止 Flask 服务器
    flask_server.stop()

