# coding:utf-8
"""字幕化任务管理器 - 管理单个字幕化任务的执行"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SubtitizeTaskState(Enum):
    """字幕化任务状态"""

    IDLE = "idle"  # 空闲
    QUEUED = "queued"  # 排队中
    TRANSCRIBING = "transcribing"  # 转录中
    OPTIMIZING = "optimizing"  # 优化中
    TRANSLATING = "translating"  # 翻译中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 取消


@dataclass
class SubtitizeTask:
    """字幕化任务"""

    task_id: int
    video_path: str
    raw_subtitle_path: str
    translated_subtitle_path: str
    language: Optional[str] = None  # 转录语言（可选）

    # 任务状态
    state: SubtitizeTaskState = SubtitizeTaskState.QUEUED
    current_progress: int = 0  # 万分制进度 (0-10000)
    current_message: str = ""  # 当前状态消息
    eta: Optional[datetime] = None  # 预计完成时间

    # 时间戳
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 错误信息
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SubtitizeTaskManager:
    """字幕化任务管理器（单例模式）- 每次只运行一个任务"""

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
        self._current_task: Optional[SubtitizeTask] = None
        self._task_id_counter = 0
        self._task_lock = threading.Lock()
        self._stop_event = threading.Event()

        # 回调函数
        self._on_progress: Optional[
            Callable[[int, int, str, Optional[datetime]], None]
        ] = None
        self._on_completed: Optional[Callable[[int, str, str, str], None]] = None
        self._on_faulted: Optional[Callable[[int, str, str], None]] = None

        logger.info("字幕化任务管理器已初始化")

    def set_callbacks(
            self,
            on_progress: Optional[Callable[[int, int, str, Optional[datetime]], None]],
            on_completed: Optional[Callable[[int, str, str, str], None]],
            on_faulted: Optional[Callable[[int, str, str], None]],
    ):
        """
        设置回调函数

        Args:
            on_progress: 进度回调 (task_id, current_progress, current_state, eta)
            on_completed: 完成回调 (task_id, video_path, raw_subtitle_path, translated_subtitle_path)
            on_faulted: 失败回调 (task_id, video_path, fault)
        """
        self._on_progress = on_progress
        self._on_completed = on_completed
        self._on_faulted = on_faulted

    def create_task(
            self,
            video_path: str,
            raw_subtitle_path: str,
            translated_subtitle_path: str,
            language: Optional[str] = None,
    ) -> int:
        """
        创建新任务

        Args:
            video_path: 视频文件路径
            raw_subtitle_path: 原始字幕输出路径
            translated_subtitle_path: 翻译字幕输出路径
            language: 转录语言（可选）

        Returns:
            task_id: 正数表示任务ID，负数表示错误代码
                -1: 已有任务正在运行
                -2: 参数无效
        """
        with self._task_lock:
            # 检查是否已有任务正在运行
            if self._current_task is not None and self._current_task.state not in [
                SubtitizeTaskState.COMPLETED,
                SubtitizeTaskState.FAILED,
                SubtitizeTaskState.CANCELLED,
            ]:
                logger.warning(f"已有任务正在运行: task_id={self._current_task.task_id}")
                return -1  # 已有任务正在运行

            # 验证参数
            if not video_path or not raw_subtitle_path:
                logger.error("参数无效: video_path 或 raw_subtitle_path 为空")
                return -2  # 参数无效

            # 生成新的任务ID
            self._task_id_counter += 1
            task_id = self._task_id_counter

            # 创建新任务
            self._current_task = SubtitizeTask(
                task_id=task_id,
                video_path=video_path,
                raw_subtitle_path=raw_subtitle_path,
                translated_subtitle_path=translated_subtitle_path,
                language=language,
            )

            # 重置停止事件
            self._stop_event.clear()

            logger.info(
                f"创建新任务: task_id={task_id}, video_path={video_path}, "
                f"raw_subtitle_path={raw_subtitle_path}, translated_subtitle_path={translated_subtitle_path}"
            )

            return task_id

    def get_current_task(self) -> Optional[SubtitizeTask]:
        """获取当前任务"""
        return self._current_task

    def stop_task(self, task_id: int) -> bool:
        """
        停止指定任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功停止
        """
        with self._task_lock:
            if self._current_task is None:
                logger.warning(f"没有任务正在运行")
                return False

            if self._current_task.task_id != task_id:
                logger.warning(
                    f"任务ID不匹配: 当前任务ID={self._current_task.task_id}, 请求停止ID={task_id}"
                )
                return False

            if self._current_task.state in [
                SubtitizeTaskState.COMPLETED,
                SubtitizeTaskState.FAILED,
                SubtitizeTaskState.CANCELLED,
            ]:
                logger.warning(f"任务已结束: state={self._current_task.state.value}")
                return False

            # 设置停止事件
            self._stop_event.set()

            # 更新任务状态
            self._current_task.state = SubtitizeTaskState.CANCELLED
            self._current_task.completed_at = datetime.now()

            logger.info(f"任务已停止: task_id={task_id}")

            # 触发失败回调（取消也算失败）
            if self._on_faulted:
                try:
                    self._on_faulted(
                        task_id, self._current_task.video_path, "任务已取消"
                    )
                except Exception as e:
                    logger.error(f"调用 on_faulted 回调失败: {e}", exc_info=True)

            return True

    def is_stop_requested(self) -> bool:
        """检查是否请求停止"""
        return self._stop_event.is_set()

    def update_progress(
            self,
            progress: int,
            state: SubtitizeTaskState,
            message: str = "",
            eta: Optional[datetime] = None,
    ):
        """
        更新任务进度

        Args:
            progress: 进度 (0-10000)
            state: 当前状态
            message: 状态消息
            eta: 预计完成时间
        """
        if self._current_task is None:
            return

        self._current_task.current_progress = progress
        self._current_task.state = state
        self._current_task.current_message = message
        self._current_task.eta = eta

        # 触发进度回调
        if self._on_progress:
            try:
                # 组合 state 和 message
                if message:
                    display_state = f"{state.value}: {message}"
                else:
                    display_state = state.value

                self._on_progress(
                    self._current_task.task_id, progress, display_state, eta)
            except Exception as e:
                logger.error(f"调用 on_progress 回调失败: {e}", exc_info=True)

    def mark_completed(self):
        """标记任务完成"""
        if self._current_task is None:
            return

        self._current_task.state = SubtitizeTaskState.COMPLETED
        self._current_task.current_progress = 10000
        self._current_task.completed_at = datetime.now()

        logger.info(f"任务完成: task_id={self._current_task.task_id}")

        # 触发完成回调
        if self._on_completed:
            try:
                self._on_completed(
                    self._current_task.task_id,
                    self._current_task.video_path,
                    self._current_task.raw_subtitle_path,
                    self._current_task.translated_subtitle_path,
                )
            except Exception as e:
                logger.error(f"调用 on_completed 回调失败: {e}", exc_info=True)

    def mark_failed(self, error: str):
        """
        标记任务失败

        Args:
            error: 错误信息
        """
        if self._current_task is None:
            return

        self._current_task.state = SubtitizeTaskState.FAILED
        self._current_task.error = error
        self._current_task.completed_at = datetime.now()

        logger.error(f"任务失败: task_id={self._current_task.task_id}, error={error}")

        # 触发失败回调
        if self._on_faulted:
            try:
                self._on_faulted(
                    self._current_task.task_id, self._current_task.video_path, error
                )
            except Exception as e:
                logger.error(f"调用 on_faulted 回调失败: {e}", exc_info=True)

    def clear_task(self):
        """清除当前任务（在任务完成或失败后调用）"""
        with self._task_lock:
            if self._current_task and self._current_task.state in [
                SubtitizeTaskState.COMPLETED,
                SubtitizeTaskState.FAILED,
                SubtitizeTaskState.CANCELLED,
            ]:
                logger.info(f"清除任务: task_id={self._current_task.task_id}")
                self._current_task = None


# 全局单例实例
task_manager = SubtitizeTaskManager()
