# coding:utf-8
"""SignalR 客户端管理器 - 管理与 Master 的 SignalR 连接"""

import logging
import threading
from typing import Callable, Dict, Optional
from urllib.parse import urlparse

from signalrcore.hub_connection_builder import HubConnectionBuilder

logger = logging.getLogger(__name__)


class SignalRClientManager:
    """SignalR 客户端管理器（单例模式）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._connection: Optional[HubConnectionBuilder] = None
        self._master_url: Optional[str] = None
        self._is_connected = False
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()

        logger.info("SignalR 客户端管理器已初始化")

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._is_connected

    @property
    def master_url(self) -> Optional[str]:
        """Master 服务器 URL"""
        return self._master_url

    def connect(self, master_url: str) -> bool:
        """
        连接到 Master SignalR Hub

        Args:
            master_url: Master SignalR Hub 的 URL

        Returns:
            是否连接成功
        """
        with self._lock:
            try:
                # 如果已经连接到相同的 URL，直接返回
                if self._is_connected and self._master_url == master_url:
                    logger.info(f"已经连接到 {master_url}")
                    return True

                # 如果已连接但 URL 不同，先断开
                if self._is_connected:
                    logger.info(f"断开现有连接: {self._master_url}")
                    self.disconnect()

                # 解析 URL
                parsed_url = urlparse(master_url)
                if not parsed_url.scheme or not parsed_url.netloc:
                    logger.error(f"无效的 Master URL: {master_url}")
                    return False

                logger.info(f"正在连接到 Master: {master_url}")

                # 创建 SignalR 连接
                self._connection = (
                    HubConnectionBuilder()
                    .with_url(master_url)
                    .with_automatic_reconnect(
                        {
                            "type": "interval",
                            "keep_alive_interval": 10,
                            "intervals": [0, 2, 5, 10, 30],
                        }
                    )
                    .build()
                )

                # 注册连接事件
                self._connection.on_open(self._on_open)
                self._connection.on_close(self._on_close)
                self._connection.on_error(self._on_error)

                # 注册已有的处理器
                for method_name, handler in self._handlers.items():
                    self._connection.on(method_name, handler)

                # 启动连接
                self._connection.start()

                self._master_url = master_url
                self._is_connected = True

                logger.info(f"成功连接到 Master: {master_url}")
                return True

            except Exception as e:
                logger.error(f"连接 Master 失败: {e}", exc_info=True)
                self._is_connected = False
                return False

    def disconnect(self):
        """断开与 Master 的连接"""
        with self._lock:
            if self._connection:
                try:
                    logger.info("正在断开 SignalR 连接")
                    self._connection.stop()
                except Exception as e:
                    logger.error(f"断开连接时出错: {e}", exc_info=True)
                finally:
                    self._connection = None
                    self._is_connected = False
                    self._master_url = None
                    logger.info("SignalR 连接已断开")

    def on(self, method_name: str, handler: Callable):
        """
        注册 SignalR 方法处理器

        Args:
            method_name: 方法名称
            handler: 处理函数
        """
        self._handlers[method_name] = handler

        # 如果已连接，立即注册到连接上
        if self._connection:
            self._connection.on(method_name, handler)

        logger.info(f"已注册 SignalR 方法处理器: {method_name}")

    def send(self, method_name: str, *args):
        """
        发送消息到 Master

        Args:
            method_name: 方法名称
            *args: 参数
        """
        if not self._is_connected or not self._connection:
            logger.warning(f"未连接到 Master，无法发送消息: {method_name}")
            return

        try:
            self._connection.send(method_name, args)
            logger.debug(f"已发送消息到 Master: {method_name}")
        except Exception as e:
            logger.error(f"发送消息失败: {e}", exc_info=True)

    def invoke(self, method_name: str, *args):
        """
        调用 Master 的方法并等待返回

        Args:
            method_name: 方法名称
            *args: 参数

        Returns:
            返回值
        """
        if not self._is_connected or not self._connection:
            logger.warning(f"未连接到 Master，无法调用方法: {method_name}")
            return None

        try:
            result = self._connection.invoke(method_name, args)
            logger.debug(f"已调用 Master 方法: {method_name}, 结果: {result}")
            return result
        except Exception as e:
            logger.error(f"调用方法失败: {e}", exc_info=True)
            return None

    def _on_open(self):
        """连接打开事件"""
        logger.info("SignalR 连接已打开")
        self._is_connected = True

    def _on_close(self):
        """连接关闭事件"""
        logger.info("SignalR 连接已关闭")
        self._is_connected = False

    def _on_error(self, error):
        """连接错误事件"""
        logger.error(f"SignalR 连接错误: {error}")


# 全局单例实例
signalr_client = SignalRClientManager()
