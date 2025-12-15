# coding:utf-8
"""RPC 服务处理器 - 处理来自 Master 的 RPC 调用"""

import logging
from typing import Any, Callable, Dict

from .signalr_client import signalr_client

logger = logging.getLogger(__name__)


class RPCServiceHandler:
    """RPC 服务处理器"""

    def __init__(self):
        self._methods: Dict[str, Callable] = {}
        self._initialized = False

    def register_method(self, method_name: str, handler: Callable):
        """
        注册 RPC 方法

        Args:
            method_name: 方法名称
            handler: 处理函数
        """
        self._methods[method_name] = handler
        logger.info(f"已注册 RPC 方法: {method_name}")

    def initialize(self):
        """初始化 RPC 服务"""
        if self._initialized:
            return

        # 注册通用的请求处理器
        signalr_client.on("InvokeMethod", self._handle_invoke_method)

        # 注册心跳处理器
        signalr_client.on("Ping", self._handle_ping)

        # 注册其他已注册的方法
        for method_name, handler in self._methods.items():
            signalr_client.on(method_name, handler)

        self._initialized = True
        logger.info("RPC 服务处理器已初始化")

    def _handle_invoke_method(self, method_name: str, *args):
        """
        处理通用方法调用

        Args:
            method_name: 方法名称
            *args: 方法参数
        """
        try:
            logger.info(f"收到 RPC 调用: {method_name}, 参数: {args}")

            if method_name not in self._methods:
                error_msg = f"未知的 RPC 方法: {method_name}"
                logger.error(error_msg)
                self._send_response(method_name, success=False, error=error_msg)
                return

            # 调用处理函数
            handler = self._methods[method_name]
            result = handler(*args)

            # 发送响应
            self._send_response(method_name, success=True, result=result)

        except Exception as e:
            logger.error(f"处理 RPC 调用失败: {e}", exc_info=True)
            self._send_response(method_name, success=False, error=str(e))

    def _handle_ping(self):
        """处理心跳请求"""
        logger.debug("收到心跳请求")
        signalr_client.send("Pong")

    def _send_response(
        self, method_name: str, success: bool, result: Any = None, error: str = None
    ):
        """
        发送 RPC 响应

        Args:
            method_name: 方法名称
            success: 是否成功
            result: 返回结果
            error: 错误信息
        """
        response = {
            "method": method_name,
            "success": success,
        }

        if success:
            response["result"] = result
        else:
            response["error"] = error

        signalr_client.send("MethodResponse", response)

    def send_event(self, event_name: str, data: Any = None):
        """
        发送事件到 Master

        Args:
            event_name: 事件名称
            data: 事件数据
        """
        try:
            signalr_client.send("Event", {"event": event_name, "data": data})
            logger.debug(f"已发送事件: {event_name}")
        except Exception as e:
            logger.error(f"发送事件失败: {e}", exc_info=True)

    def send_callback(self, callback_name: str, data: Any = None):
        """
        发送回调到 Master

        Args:
            callback_name: 回调名称
            data: 回调数据
        """
        try:
            signalr_client.send(callback_name, data)
            logger.debug(f"已发送回调: {callback_name}")
        except Exception as e:
            logger.error(f"发送回调失败: {e}", exc_info=True)

    def send_progress(self, task_id: str, progress: float, message: str = ""):
        """
        发送任务进度

        Args:
            task_id: 任务 ID
            progress: 进度（0-100）
            message: 进度消息
        """
        try:
            signalr_client.send(
                "Progress",
                {"task_id": task_id, "progress": progress, "message": message},
            )
            logger.debug(f"已发送进度: {task_id} - {progress}%")
        except Exception as e:
            logger.error(f"发送进度失败: {e}", exc_info=True)

    def send_log(self, level: str, message: str):
        """
        发送日志到 Master

        Args:
            level: 日志级别（info/warning/error）
            message: 日志消息
        """
        try:
            signalr_client.send("Log", {"level": level, "message": message})
        except Exception as e:
            logger.error(f"发送日志失败: {e}", exc_info=True)


# 全局单例实例
rpc_handler = RPCServiceHandler()
