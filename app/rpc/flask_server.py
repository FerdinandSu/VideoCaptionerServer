# coding:utf-8
"""Flask API 服务器 - 提供控制接口"""

import logging
import threading
from typing import Optional

from flasgger import Swagger
from flask import Flask, jsonify, request

from .signalr_client import signalr_client

logger = logging.getLogger(__name__)


class FlaskAPIServer:
    """Flask API 服务器（单例模式）"""

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
        self.app = Flask(__name__)
        self._server_thread: Optional[threading.Thread] = None
        self._is_running = False

        # 配置 Swagger
        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec",
                    "route": "/apispec.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/docs",
        }
        swagger_template = {
            "info": {
                "title": "VideoCaptioner RPC API",
                "description": "VideoCaptioner Worker 节点 RPC 接口",
                "version": "1.0.0",
            },
            "schemes": ["http", "https"],
        }
        Swagger(self.app, config=swagger_config, template=swagger_template)

        # 禁用 Flask 的默认日志输出
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)

        # 注册路由
        self._register_routes()

        logger.info("Flask API 服务器已初始化")

    def _register_routes(self):
        """注册 API 路由"""

        @self.app.route("/health", methods=["GET"])
        def health():
            """健康检查
            ---
            tags:
              - System
            responses:
              200:
                description: 服务健康
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    status:
                      type: string
            """
            return jsonify({"success": True, "status": "healthy"})

        @self.app.route("/set-master", methods=["GET"])
        def set_master():
            """设置 Master SignalR Hub URL
            ---
            tags:
              - SignalR
            parameters:
              - name: url
                in: query
                type: string
                required: true
                description: Master SignalR Hub 的 URL
            responses:
              200:
                description: 连接成功
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    message:
                      type: string
                    master_url:
                      type: string
              400:
                description: 缺少参数
              500:
                description: 连接失败
            """
            master_url = request.args.get("url")

            if not master_url:
                return jsonify({"success": False, "error": "缺少 url 参数"}), 400

            try:
                # 连接到 Master
                success = signalr_client.connect(master_url)

                if success:
                    return jsonify(
                        {
                            "success": True,
                            "message": f"已连接到 Master: {master_url}",
                            "master_url": master_url,
                        }
                    )
                else:
                    return jsonify(
                        {"success": False, "error": "连接 Master 失败"}
                    ), 500

            except Exception as e:
                logger.error(f"设置 Master 失败: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/disconnect-master", methods=["GET", "POST"])
        def disconnect_master():
            """断开与 Master 的连接
            ---
            tags:
              - SignalR
            responses:
              200:
                description: 断开成功
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    message:
                      type: string
              500:
                description: 断开失败
            """
            try:
                signalr_client.disconnect()
                return jsonify({"success": True, "message": "已断开与 Master 的连接"})
            except Exception as e:
                logger.error(f"断开连接失败: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/status", methods=["GET"])
        def status():
            """获取 Worker 状态
            ---
            tags:
              - RPC
            responses:
              200:
                description: 状态信息
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    is_connected:
                      type: boolean
                      description: 是否已连接到 Master
                    master_url:
                      type: string
                      description: Master URL
                    worker_status:
                      type: string
                      description: Worker 状态 (idle/busy)
                    current_task:
                      type: object
                      description: 当前任务信息（如果有）
            """
            from .rpc_service import rpc_service

            worker_status = rpc_service.get_status()
            return jsonify(
                {
                    "success": True,
                    "is_connected": signalr_client.is_connected,
                    "master_url": signalr_client.master_url,
                    **worker_status,
                }
            )

        @self.app.route("/api/rpc/start-subtitize", methods=["POST"])
        def start_subtitize():
            """启动字幕化任务
            ---
            tags:
              - RPC
            parameters:
              - name: body
                in: body
                required: true
                schema:
                  type: object
                  required:
                    - video_path
                    - raw_subtitle_path
                    - translated_subtitle_path
                  properties:
                    video_path:
                      type: string
                      description: 视频文件路径
                    raw_subtitle_path:
                      type: string
                      description: 原始字幕输出路径
                    translated_subtitle_path:
                      type: string
                      description: 翻译字幕输出路径
            responses:
              200:
                description: 任务已启动
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    task_id:
                      type: integer
                      description: 任务ID (>0 成功, -1 已有任务运行, -2 参数无效, -3 启动失败)
                    message:
                      type: string
              400:
                description: 参数错误
            """
            from .rpc_service import rpc_service

            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "缺少请求体"}), 400

            video_path = data.get("video_path")
            raw_subtitle_path = data.get("raw_subtitle_path")
            translated_subtitle_path = data.get("translated_subtitle_path")

            if not video_path or not raw_subtitle_path:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "缺少必要参数: video_path, raw_subtitle_path",
                        }
                    ),
                    400,
                )

            try:
                task_id = rpc_service.start_subtitize(
                    video_path, raw_subtitle_path, translated_subtitle_path
                )

                if task_id > 0:
                    return jsonify(
                        {
                            "success": True,
                            "task_id": task_id,
                            "message": f"任务已启动: task_id={task_id}",
                        }
                    )
                elif task_id == -1:
                    return jsonify(
                        {
                            "success": False,
                            "task_id": task_id,
                            "message": "已有任务正在运行",
                        }
                    )
                elif task_id == -2:
                    return jsonify(
                        {"success": False, "task_id": task_id, "message": "参数无效"}
                    )
                else:  # -3
                    return jsonify(
                        {
                            "success": False,
                            "task_id": task_id,
                            "message": "启动执行器失败",
                        }
                    )

            except Exception as e:
                logger.error(f"启动任务失败: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/rpc/stop-subtitize", methods=["POST"])
        def stop_subtitize():
            """停止字幕化任务
            ---
            tags:
              - RPC
            parameters:
              - name: body
                in: body
                required: true
                schema:
                  type: object
                  required:
                    - task_id
                  properties:
                    task_id:
                      type: integer
                      description: 任务ID
            responses:
              200:
                description: 停止结果
                schema:
                  type: object
                  properties:
                    success:
                      type: boolean
                    task_id:
                      type: integer
                    message:
                      type: string
              400:
                description: 参数错误
            """
            from .rpc_service import rpc_service

            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "缺少请求体"}), 400

            task_id = data.get("task_id")
            if task_id is None:
                return jsonify({"success": False, "error": "缺少参数: task_id"}), 400

            try:
                result = rpc_service.stop_subtitize(task_id)
                return jsonify(result)
            except Exception as e:
                logger.error(f"停止任务失败: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/rpc/get-status", methods=["GET"])
        def get_status():
            """获取任务状态
            ---
            tags:
              - RPC
            responses:
              200:
                description: 任务状态
                schema:
                  type: object
                  properties:
                    status:
                      type: string
                      description: Worker 状态 (idle/busy)
                    current_task:
                      type: object
                      description: 当前任务信息
            """
            from .rpc_service import rpc_service

            return jsonify(rpc_service.get_status())

    def start(self, host: str = "0.0.0.0", port: int = 5000):
        """
        启动 Flask 服务器

        Args:
            host: 监听地址
            port: 监听端口
        """
        if self._is_running:
            logger.warning("Flask 服务器已在运行")
            return

        def run_server():
            logger.info(f"Flask API 服务器正在启动: http://{host}:{port}")
            logger.info(f"Swagger UI: http://{host}:{port}/api/docs")
            self.app.run(host=host, port=port, debug=False, use_reloader=False)

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()
        self._is_running = True

        logger.info(f"Flask API 服务器已启动: http://{host}:{port}")
        logger.info(f"访问 Swagger UI: http://{host}:{port}/api/docs")

    def stop(self):
        """停止 Flask 服务器"""
        if not self._is_running:
            logger.warning("Flask 服务器未在运行")
            return

        # Flask 在生产环境中停止比较复杂，这里使用 daemon 线程
        # 当主程序退出时会自动停止
        self._is_running = False
        logger.info("Flask API 服务器已停止")


# 全局单例实例
flask_server = FlaskAPIServer()
