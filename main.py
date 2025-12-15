#!/usr/bin/env python
# coding:utf-8
"""
VideoCaptioner RPC Server - 纯后端服务
无 UI 版本，仅提供 RPC 接口
"""

import logging
import os
import signal
import sys
import threading
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
from app.core.utils.logger import setup_logger
from app.core.utils.cache import enable_cache, disable_cache
from app.common.config import cfg
from app.rpc import start_rpc_server, stop_rpc_server

logger = setup_logger("VideoCaptioner-RPC")


def exception_hook(exctype, value, tb):
    """全局异常处理"""
    import traceback
    logger.error("".join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = exception_hook

# 应用缓存配置
if cfg.get(cfg.cache_enabled):
    enable_cache()
    logger.info("缓存已启用")
else:
    disable_cache()
    logger.info("缓存已禁用")

# 用于控制主线程退出的事件
shutdown_event = threading.Event()


def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("收到退出信号，正在关闭 RPC 服务器...")
    stop_rpc_server()
    shutdown_event.set()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("VideoCaptioner RPC 服务器 (无 UI 版本)")
    logger.info("=" * 60)

    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 读取 RPC 配置
    rpc_host = cfg.get(cfg.rpc_host) or "localhost"
    rpc_port = cfg.get(cfg.rpc_port) or 5000

    logger.info(f"Flask API 地址: http://{rpc_host}:{rpc_port}")
    logger.info(f"Swagger UI: http://{rpc_host}:{rpc_port}/api/docs")
    logger.info("可用端点:")
    logger.info(f"  - GET  /health                    健康检查")
    logger.info(f"  - GET  /status                    获取连接状态")
    logger.info(f"  - GET  /set-master?url=           设置 Master URL")
    logger.info(f"  - GET  /disconnect-master         断开 Master 连接")
    logger.info(f"  - POST /api/rpc/start-subtitize   启动字幕化任务")
    logger.info(f"  - POST /api/rpc/stop-subtitize    停止字幕化任务")
    logger.info(f"  - GET  /api/rpc/get-status        获取任务状态")
    logger.info("=" * 60)

    try:
        # 启动 RPC 服务器
        start_rpc_server(host=rpc_host, port=rpc_port)
        logger.info("RPC 服务器已启动，按 Ctrl+C 退出")

        # 保持主线程运行（跨平台方式）
        shutdown_event.wait()

    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
        stop_rpc_server()
    except Exception as e:
        logger.error(f"RPC 服务器启动失败: {e}", exc_info=True)
        sys.exit(1)

    logger.info("RPC 服务器已关闭")


if __name__ == "__main__":
    main()
