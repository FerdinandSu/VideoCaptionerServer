# coding:utf-8
"""RPC 服务 - 字幕化服务方法实现"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .rpc_handler import rpc_handler
from .subtitize_executor import subtitize_executor
from .task_manager import task_manager

logger = logging.getLogger(__name__)


class VideoCaptionerRPCService:
    """VideoCaptioner RPC 服务 - 提供给 Master 调用的方法"""

    def __init__(self):
        self._initialize_task_manager()
        self._register_methods()

    def _initialize_task_manager(self):
        """初始化任务管理器回调"""
        task_manager.set_callbacks(
            on_progress=self._on_subtitize_progress,
            on_completed=self._on_subtitize_completed,
            on_faulted=self._on_subtitize_faulted,
        )
        logger.info("任务管理器回调已设置")

    def _register_methods(self):
        """注册所有 RPC 方法"""
        # 注册方法到 RPC 处理器
        rpc_handler.register_method("GetInfo", self.get_info)
        rpc_handler.register_method("GetStatus", self.get_status)
        rpc_handler.register_method("StartSubtitize", self.start_subtitize)
        rpc_handler.register_method("StopSubtitize", self.stop_subtitize)

        logger.info("VideoCaptioner RPC 服务方法已注册")

    # ==================== RPC 回调方法 ====================

    def _on_subtitize_progress(
        self,
        task_id: int,
        current_progress: int,
        current_state: str,
        eta: Optional[datetime],
    ):
        """
        字幕化进度回调

        Args:
            task_id: 任务ID
            current_progress: 当前进度（万分制）
            current_state: 当前状态
            eta: 预计完成时间
        """
        try:
            logger.debug(
                f"进度更新: task_id={task_id}, progress={current_progress}, state={current_state}"
            )

            # 发送进度到 Master
            rpc_handler.send_callback(
                "SubtitizeProgress",
                {
                    "task_id": task_id,
                    "current_progress": current_progress,
                    "current_state": current_state,
                    "eta": eta.isoformat() if eta else None,
                },
            )
        except Exception as e:
            logger.error(f"发送进度回调失败: {e}", exc_info=True)

    def _on_subtitize_completed(
        self,
        task_id: int,
        video_path: str,
        raw_subtitle_path: str,
        translated_subtitle_path: str,
    ):
        """
        字幕化完成回调

        Args:
            task_id: 任务ID
            video_path: 视频路径
            raw_subtitle_path: 原始字幕路径
            translated_subtitle_path: 翻译字幕路径
        """
        try:
            logger.info(f"任务完成: task_id={task_id}")

            # 发送完成通知到 Master
            rpc_handler.send_callback(
                "SubtitizeCompleted",
                {
                    "task_id": task_id,
                    "video_path": video_path,
                    "raw_subtitle_path": raw_subtitle_path,
                    "translated_subtitle_path": translated_subtitle_path,
                },
            )

            # 清除任务
            task_manager.clear_task()

        except Exception as e:
            logger.error(f"发送完成回调失败: {e}", exc_info=True)

    def _on_subtitize_faulted(self, task_id: int, video_path: str, fault: str):
        """
        字幕化失败回调

        Args:
            task_id: 任务ID
            video_path: 视频路径
            fault: 错误信息
        """
        try:
            logger.error(f"任务失败: task_id={task_id}, fault={fault}")

            # 发送失败通知到 Master
            rpc_handler.send_callback(
                "SubtitizeFaulted",
                {
                    "task_id": task_id,
                    "video_path": video_path,
                    "fault": fault,
                },
            )

            # 清除任务
            task_manager.clear_task()

        except Exception as e:
            logger.error(f"发送失败回调失败: {e}", exc_info=True)

    # ==================== RPC 方法 ====================

    def get_info(self) -> Dict[str, str]:
        """
        获取应用信息

        Returns:
            应用信息字典
        """
        from app.config import APP_NAME, VERSION

        return {
            "app_name": APP_NAME,
            "version": VERSION,
            "description": "视频字幕生成和翻译工具",
        }

    def get_status(self) -> Dict[str, Any]:
        """
        获取应用状态

        Returns:
            应用状态字典
        """
        current_task = task_manager.get_current_task()

        if current_task is None:
            return {
                "status": "idle",
                "current_task": None,
            }

        return {
            "status": "busy",
            "current_task": {
                "task_id": current_task.task_id,
                "state": current_task.state.value,
                "progress": current_task.current_progress,
                "video_path": current_task.video_path,
                "created_at": current_task.created_at.isoformat(),
                "started_at": (
                    current_task.started_at.isoformat()
                    if current_task.started_at
                    else None
                ),
            },
        }

    def start_subtitize(
        self,
        video_path: str,
        raw_subtitle_path: str,
        translated_subtitle_path: str,
        language: Optional[str] = None,
    ) -> int:
        """
        启动字幕化任务

        Args:
            video_path: 视频文件路径
            raw_subtitle_path: 原始字幕输出路径
            translated_subtitle_path: 翻译字幕输出路径
            language: 转录语言（可选，ISO 语言代码如 'en', 'zh'，或语言名称如 '英语', '中文'）
                     如果不提供，将使用配置文件中的语言设置

        Returns:
            task_id: 正数表示任务ID，负数表示错误代码
                -1: 已有任务正在运行
                -2: 参数无效
                -3: 启动执行器失败
        """
        try:
            logger.info(
                f"收到 StartSubtitize 请求: video_path={video_path}, "
                f"raw_subtitle_path={raw_subtitle_path}, "
                f"translated_subtitle_path={translated_subtitle_path}, "
                f"language={language}"
            )

            # 创建任务
            task_id = task_manager.create_task(
                video_path=video_path,
                raw_subtitle_path=raw_subtitle_path,
                translated_subtitle_path=translated_subtitle_path,
                language=language,
            )

            if task_id < 0:
                logger.error(f"创建任务失败: error_code={task_id}")
                return task_id

            # 启动执行器
            success = subtitize_executor.execute(task_id)

            if not success:
                logger.error(f"启动执行器失败: task_id={task_id}")
                task_manager.clear_task()
                return -3  # 启动执行器失败

            logger.info(f"任务已启动: task_id={task_id}")
            return task_id

        except Exception as e:
            logger.exception(f"StartSubtitize 失败: {e}")
            return -2  # 参数无效或其他错误

    def stop_subtitize(self, task_id: int) -> Dict[str, Any]:
        """
        停止字幕化任务

        Args:
            task_id: 任务ID

        Returns:
            停止结果
        """
        try:
            logger.info(f"收到 StopSubtitize 请求: task_id={task_id}")

            success = task_manager.stop_task(task_id)

            if success:
                return {
                    "success": True,
                    "task_id": task_id,
                    "message": "任务已停止",
                }
            else:
                return {
                    "success": False,
                    "task_id": task_id,
                    "message": "停止任务失败（任务不存在或已结束）",
                }

        except Exception as e:
            logger.exception(f"StopSubtitize 失败: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
            }


# 全局服务实例
rpc_service = VideoCaptionerRPCService()
