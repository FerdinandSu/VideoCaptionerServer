# coding:utf-8
"""字幕化执行器 - 执行转录和字幕处理的核心逻辑"""

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from app.common.config import cfg
from app.core.asr import transcribe
from app.core.asr.asr_data import ASRData
from app.core.entities import SubtitleConfig, TranscribeConfig
from app.core.optimize.optimize import SubtitleOptimizer
from app.core.split.split import SubtitleSplitter
from app.core.translate import BingTranslator, DeepLXTranslator, GoogleTranslator, LLMTranslator
from app.core.utils.logger import setup_logger
from app.core.utils.video_utils import video2audio

from .task_manager import SubtitizeTaskState, task_manager

logger = setup_logger("subtitize_executor")


class SubtitizeExecutor:
    """字幕化执行器 - 执行转录到字幕优化&翻译的完整流程"""

    def __init__(self):
        self._executor_thread: Optional[threading.Thread] = None

    def execute(self, task_id: int) -> bool:
        """
        执行字幕化任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功启动
        """
        task = task_manager.get_current_task()
        if task is None or task.task_id != task_id:
            logger.error(f"任务不存在: task_id={task_id}")
            return False

        # 在新线程中执行任务
        self._executor_thread = threading.Thread(
            target=self._run_task, args=(task_id,), daemon=True
        )
        self._executor_thread.start()

        return True

    def _run_task(self, task_id: int):
        """
        在独立线程中运行任务

        Args:
            task_id: 任务ID
        """
        try:
            task = task_manager.get_current_task()
            if task is None or task.task_id != task_id:
                logger.error(f"任务不存在: task_id={task_id}")
                return

            # 标记任务开始
            task.started_at = datetime.now()

            # 第一阶段：转录 (0-50%)
            logger.info(f"开始转录: task_id={task_id}")
            task_manager.update_progress(
                0, SubtitizeTaskState.TRANSCRIBING, message="准备开始转录"
            )

            raw_subtitle_path = self._transcribe(
                task.video_path, task.raw_subtitle_path, task_id
            )

            if task_manager.is_stop_requested():
                logger.info(f"任务被取消: task_id={task_id}")
                return

            if not raw_subtitle_path:
                task_manager.mark_failed("转录失败")
                return

            # 第二阶段：字幕处理 (50-100%)
            logger.info(f"开始字幕处理: task_id={task_id}")
            task_manager.update_progress(
                5000, SubtitizeTaskState.OPTIMIZING, message="转录完成，开始处理字幕"
            )

            translated_subtitle_path = self._process_subtitle(
                raw_subtitle_path,
                task.video_path,
                task.translated_subtitle_path,
                task_id,
            )

            if task_manager.is_stop_requested():
                logger.info(f"任务被取消: task_id={task_id}")
                return

            if not translated_subtitle_path:
                task_manager.mark_failed("字幕处理失败")
                return

            # 任务完成
            task_manager.mark_completed()

        except Exception as e:
            logger.exception(f"任务执行失败: task_id={task_id}, error={e}")
            task_manager.mark_failed(str(e))

    def _transcribe(
        self, video_path: str, output_path: str, task_id: int
    ) -> Optional[str]:
        """
        执行转录

        Args:
            video_path: 视频文件路径
            output_path: 输出字幕路径
            task_id: 任务ID

        Returns:
            生成的字幕文件路径，失败返回 None
        """
        import tempfile

        try:
            # 获取当前任务
            task = task_manager.get_current_task()
            if task is None or task.task_id != task_id:
                raise ValueError(f"任务不存在: task_id={task_id}")

            # 检查视频文件是否存在
            video_path_obj = Path(video_path)
            if not video_path_obj.exists():
                raise ValueError(f"视频文件不存在: {video_path}")

            # 创建转录配置（从全局配置读取）
            transcribe_config = TranscribeConfig(
                transcribe_model=cfg.get(cfg.transcribe_model),
                transcribe_language=(
                    task.language
                    if task.language
                    else cfg.get(cfg.transcribe_language).value
                ),
                need_word_time_stamp=True,
                output_format=cfg.get(cfg.transcribe_output_format),
                # Whisper Cpp 配置
                whisper_model=cfg.get(cfg.whisper_model),
                # Whisper API 配置
                whisper_api_key=cfg.get(cfg.whisper_api_key),
                whisper_api_base=cfg.get(cfg.whisper_api_base),
                whisper_api_model=cfg.get(cfg.whisper_api_model),
                whisper_api_prompt=cfg.get(cfg.whisper_api_prompt),
                # Faster Whisper 配置
                faster_whisper_program=cfg.get(cfg.faster_whisper_program),
                faster_whisper_model=cfg.get(cfg.faster_whisper_model),
                faster_whisper_model_dir=cfg.get(cfg.faster_whisper_model_dir),
                faster_whisper_device=cfg.get(cfg.faster_whisper_device),
                faster_whisper_vad_filter=cfg.get(cfg.faster_whisper_vad_filter),
                faster_whisper_vad_threshold=cfg.get(cfg.faster_whisper_vad_threshold),
                faster_whisper_vad_method=cfg.get(cfg.faster_whisper_vad_method),
                faster_whisper_ff_mdx_kim2=cfg.get(cfg.faster_whisper_ff_mdx_kim2),
                faster_whisper_one_word=cfg.get(cfg.faster_whisper_one_word),
                faster_whisper_prompt=cfg.get(cfg.faster_whisper_prompt),
            )

            logger.info(f"\n{transcribe_config.print_config()}")
            logger.info(f"faster_whisper_model_dir 配置值: '{transcribe_config.faster_whisper_model_dir}'")

            # 创建临时音频文件
            task_manager.update_progress(
                500, SubtitizeTaskState.TRANSCRIBING, message="准备音频文件"
            )
            temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_audio_path = temp_audio_file.name
            temp_audio_file.close()

            try:
                # 转换视频到音频
                logger.info("开始转换音频")
                is_success = video2audio(
                    video_path,
                    output=temp_audio_path,
                    audio_track_index=0
                )

                if not is_success:
                    raise RuntimeError("音频转换失败")

                if task_manager.is_stop_requested():
                    return None

                # 执行转录
                task_manager.update_progress(
                    1000, SubtitizeTaskState.TRANSCRIBING, message="开始语音转录"
                )
                logger.info("开始语音转录")

                def progress_callback(progress: int, message: str):
                    """进度回调"""
                    # 转录占 10-50%，所以进度映射到 1000-5000
                    current_progress = int(1000 + (progress / 100.0) * 4000)
                    task_manager.update_progress(
                        current_progress,
                        SubtitizeTaskState.TRANSCRIBING,
                        message=message,  # 传递状态消息
                    )

                # 调用转录函数
                asr_data = transcribe(
                    audio_path=temp_audio_path,
                    config=transcribe_config,
                    callback=progress_callback,
                )

                if task_manager.is_stop_requested():
                    return None

                # 保存字幕文件
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)

                # 保存为 SRT 格式
                asr_data.save(str(output_path_obj))

                if not output_path_obj.exists():
                    raise ValueError("转录未生成输出文件")

                logger.info(f"转录完成: {output_path_obj}")
                return str(output_path_obj)

            finally:
                # 清理临时音频文件
                Path(temp_audio_path).unlink(missing_ok=True)

        except Exception as e:
            logger.exception(f"转录失败: {e}")
            return None

    def _process_subtitle(
        self,
        subtitle_path: str,
        video_path: str,
        output_path: str,
        task_id: int,
    ) -> Optional[str]:
        """
        处理字幕（分割、优化和翻译）

        Args:
            subtitle_path: 输入字幕文件路径
            video_path: 视频文件路径
            output_path: 输出字幕文件路径
            task_id: 任务ID

        Returns:
            处理后的字幕文件路径，失败返回 None
        """
        try:
            # 检查字幕文件是否存在
            subtitle_path_obj = Path(subtitle_path)
            if not subtitle_path_obj.exists():
                raise ValueError(f"字幕文件不存在: {subtitle_path}")

            # 创建字幕处理配置（从全局配置读取）
            # 根据 LLM 服务选择对应的 API 配置
            llm_service = cfg.get(cfg.llm_service)

            # 选择对应的 API base 和 key
            if llm_service.value == "Ollama":
                api_base = cfg.get(cfg.ollama_api_base)
                api_key = cfg.get(cfg.ollama_api_key)
                llm_model = cfg.get(cfg.ollama_model)
            elif llm_service.value == "DeepSeek":
                api_base = cfg.get(cfg.deepseek_api_base)
                api_key = cfg.get(cfg.deepseek_api_key)
                llm_model = cfg.get(cfg.deepseek_model)
            elif llm_service.value == "SiliconCloud":
                api_base = cfg.get(cfg.silicon_cloud_api_base)
                api_key = cfg.get(cfg.silicon_cloud_api_key)
                llm_model = cfg.get(cfg.silicon_cloud_model)
            elif llm_service.value == "LM Studio":
                api_base = cfg.get(cfg.lm_studio_api_base)
                api_key = cfg.get(cfg.lm_studio_api_key)
                llm_model = cfg.get(cfg.lm_studio_model)
            elif llm_service.value == "Gemini":
                api_base = cfg.get(cfg.gemini_api_base)
                api_key = cfg.get(cfg.gemini_api_key)
                llm_model = cfg.get(cfg.gemini_model)
            elif llm_service.value == "ChatGLM":
                api_base = cfg.get(cfg.chatglm_api_base)
                api_key = cfg.get(cfg.chatglm_api_key)
                llm_model = cfg.get(cfg.chatglm_model)
            else:  # OpenAI (default)
                api_base = cfg.get(cfg.openai_api_base)
                api_key = cfg.get(cfg.openai_api_key)
                llm_model = cfg.get(cfg.openai_model)

            subtitle_config = SubtitleConfig(
                base_url=api_base,
                api_key=api_key,
                llm_model=llm_model,
                deeplx_endpoint=cfg.get(cfg.deeplx_endpoint),
                translator_service=cfg.get(cfg.translator_service),
                need_translate=cfg.get(cfg.need_translate),
                need_optimize=cfg.get(cfg.need_optimize),
                need_reflect=cfg.get(cfg.need_reflect_translate),
                thread_num=cfg.get(cfg.thread_num),
                batch_size=cfg.get(cfg.batch_size),
                subtitle_layout=cfg.get(cfg.subtitle_layout),
                max_word_count_cjk=cfg.get(cfg.max_word_count_cjk),
                max_word_count_english=cfg.get(cfg.max_word_count_english),
                need_split=cfg.get(cfg.need_split),
                target_language=cfg.get(cfg.target_language),
                subtitle_style=cfg.get(cfg.subtitle_style_name),
                custom_prompt_text=cfg.get(cfg.custom_prompt_text),
            )

            logger.info(f"\n{subtitle_config.print_config()}")

            # 设置环境变量（LLM 客户端需要）
            import os
            if subtitle_config.base_url:
                os.environ["OPENAI_BASE_URL"] = subtitle_config.base_url
            if subtitle_config.api_key:
                os.environ["OPENAI_API_KEY"] = subtitle_config.api_key

            # 加载字幕数据
            asr_data = ASRData.from_subtitle_file(subtitle_path)

            current_progress_base = 5000  # 50%

            # 1. 分割字幕 (50-60%)
            if subtitle_config.need_split:
                logger.info("开始分割字幕")
                task_manager.update_progress(
                    current_progress_base,
                    SubtitizeTaskState.OPTIMIZING,
                    message="开始分割字幕",
                )

                # 如果不是字词级时间戳，先分割
                if not asr_data.is_word_timestamp():
                    asr_data.split_to_word_segments()

                # 使用分割器断句
                splitter = SubtitleSplitter(
                    thread_num=subtitle_config.thread_num,
                    model=subtitle_config.llm_model,
                    max_word_count_cjk=subtitle_config.max_word_count_cjk,
                    max_word_count_english=subtitle_config.max_word_count_english,
                )
                asr_data = splitter.split_subtitle(asr_data)

                current_progress_base = 6000

                if task_manager.is_stop_requested():
                    return None

            # 2. 优化字幕 (60-70%)
            if subtitle_config.need_optimize:
                logger.info("开始优化字幕")
                task_manager.update_progress(
                    current_progress_base, SubtitizeTaskState.OPTIMIZING
                )

                # 记录总字幕数和已处理数
                total_segments = len(asr_data.segments)
                processed_segments = 0

                def optimize_progress_callback(result: List):
                    """优化进度回调 - 每处理完一个批次调用"""
                    nonlocal processed_segments
                    processed_segments += len(result)
                    if total_segments > 0:
                        progress = processed_segments / total_segments
                        current_prog = int(6000 + progress * 1000)  # 6000-7000
                        task_manager.update_progress(
                            current_prog, SubtitizeTaskState.OPTIMIZING
                        )

                optimizer = SubtitleOptimizer(
                    thread_num=subtitle_config.thread_num,
                    batch_num=subtitle_config.batch_size,
                    model=subtitle_config.llm_model,
                    custom_prompt=subtitle_config.custom_prompt_text or "",
                    update_callback=optimize_progress_callback,
                )

                asr_data = optimizer.optimize_subtitle(asr_data)

                current_progress_base = 7000

                if task_manager.is_stop_requested():
                    return None

            # 3. 翻译字幕 (70-100%)
            if subtitle_config.need_translate:
                logger.info("开始翻译字幕")
                task_manager.update_progress(
                    current_progress_base, SubtitizeTaskState.TRANSLATING
                )

                # 记录总字幕数和已处理数
                total_segments = len(asr_data.segments)
                processed_segments = 0

                def translate_progress_callback(result: List):
                    """翻译进度回调 - 每处理完一个批次调用"""
                    nonlocal processed_segments
                    processed_segments += len(result)
                    if total_segments > 0:
                        progress = processed_segments / total_segments
                        current_prog = int(7000 + progress * 3000)  # 7000-10000
                        task_manager.update_progress(
                            current_prog, SubtitizeTaskState.TRANSLATING
                        )

                # 根据配置创建翻译器
                if subtitle_config.translator_service == subtitle_config.translator_service.OPENAI:
                    translator = LLMTranslator(
                        thread_num=subtitle_config.thread_num,
                        batch_num=subtitle_config.batch_size,
                        target_language=subtitle_config.target_language,
                        model=subtitle_config.llm_model,
                        custom_prompt=subtitle_config.custom_prompt_text or "",
                        is_reflect=subtitle_config.need_reflect,
                        update_callback=translate_progress_callback,
                    )
                elif subtitle_config.translator_service == subtitle_config.translator_service.BING:
                    translator = BingTranslator(
                        thread_num=subtitle_config.thread_num,
                        batch_num=10,
                        target_language=subtitle_config.target_language,
                        update_callback=translate_progress_callback,
                    )
                elif subtitle_config.translator_service == subtitle_config.translator_service.GOOGLE:
                    translator = GoogleTranslator(
                        thread_num=subtitle_config.thread_num,
                        batch_num=5,
                        target_language=subtitle_config.target_language,
                        timeout=20,
                        update_callback=translate_progress_callback,
                    )
                elif subtitle_config.translator_service == subtitle_config.translator_service.DEEPLX:
                    import os
                    if subtitle_config.deeplx_endpoint:
                        os.environ["DEEPLX_ENDPOINT"] = subtitle_config.deeplx_endpoint
                    translator = DeepLXTranslator(
                        thread_num=subtitle_config.thread_num,
                        batch_num=5,
                        target_language=subtitle_config.target_language,
                        timeout=20,
                        update_callback=translate_progress_callback,
                    )
                else:
                    raise ValueError(f"不支持的翻译服务: {subtitle_config.translator_service}")

                asr_data = translator.translate_subtitle(asr_data)

                if task_manager.is_stop_requested():
                    return None

                current_progress_base = 10000

            # 保存最终字幕文件
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # 根据布局生成字幕
            asr_data.save(
                save_path=output_path,
                ass_style=subtitle_config.subtitle_style or "",
                layout=subtitle_config.subtitle_layout,
            )

            logger.info(f"字幕处理完成: {output_path}")
            return output_path

        except Exception as e:
            logger.exception(f"字幕处理失败: {e}")
            return None


# 全局执行器实例
subtitize_executor = SubtitizeExecutor()
