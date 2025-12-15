#!/usr/bin/env python
# coding:utf-8
"""RPC 服务器独立启动脚本"""

import logging
import signal
import sys
import threading
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_PATH = Path(__file__).parent
sys.path.insert(0, str(ROOT_PATH))

from app.rpc import start_rpc_server, stop_rpc_server

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# 用于控制主线程退出的事件
shutdown_event = threading.Event()


def signal_handler(signum, frame):
    """处理退出信号"""
    logger.info("收到退出信号，正在关闭 RPC 服务器...")
    stop_rpc_server()
    shutdown_event.set()


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动 RPC 服务器
    host = "localhost"
    port = 5000

    logger.info("=" * 60)
    logger.info("VideoCaptioner RPC 服务器")
    logger.info("=" * 60)
    logger.info(f"Flask API 地址: http://{host}:{port}")
    logger.info(f"Swagger UI: http://{host}:{port}/api/docs")
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
        start_rpc_server(host=host, port=port)
        logger.info("RPC 服务器已启动，按 Ctrl+C 退出")

        # 保持主线程运行（跨平台方式）
        shutdown_event.wait()

    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
        stop_rpc_server()
    except Exception as e:
        logger.error(f"RPC 服务器启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
