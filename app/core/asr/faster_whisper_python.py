"""Python 版 Faster-Whisper ASR 实现"""
import hashlib
import os
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

from faster_whisper import WhisperModel

from ..utils.logger import setup_logger
from .asr_data import ASRData, ASRDataSeg
from .base import BaseASR
from .status import ASRStatus

logger = setup_logger("faster_whisper_python")


class FasterWhisperPythonASR(BaseASR):
    """Python 版 Faster-Whisper ASR 实现.

    使用 faster-whisper Python 库进行本地语音识别。
    支持 CPU/CUDA 加速和多种 VAD 方法。
    """

    def __init__(
        self,
        audio_input: Union[str, bytes],
        whisper_model: str,
        model_dir: Optional[str] = None,
        language: str = "zh",
        device: str = "cpu",
        compute_type: str = "int8",
        use_cache: bool = False,
        need_word_time_stamp: bool = False,
        # VAD 相关参数
        vad_filter: bool = True,
        vad_threshold: float = 0.4,
        # 其他参数
        beam_size: int = 5,
        prompt: Optional[str] = None,
    ):
        super().__init__(audio_input, use_cache)

        # 基本参数
        self.model_name = whisper_model
        self.model_dir = model_dir
        self.need_word_time_stamp = need_word_time_stamp

        # 转换语言代码（如果需要）
        from ..entities import TranscribeLanguageEnum
        self.language = TranscribeLanguageEnum.to_language_code(language)

        self.device = device
        self.compute_type = compute_type

        # VAD 参数
        self.vad_filter = vad_filter
        self.vad_threshold = vad_threshold

        # 转录参数
        self.beam_size = beam_size
        self.prompt = prompt

        # 设置 compute_type
        if self.device == "cuda":
            # CUDA 使用 float16 以获得更好的性能
            self.compute_type = "float16"
        else:
            # CPU 使用 int8 以获得更快的速度
            self.compute_type = "int8"

    def _load_model(self) -> WhisperModel:
        """加载 Whisper 模型"""
        logger.info(
            f"Loading Whisper model: {self.model_name}, "
            f"device: {self.device}, "
            f"compute_type: {self.compute_type}"
        )

        # 如果指定了模型目录，使用本地路径
        if self.model_dir and Path(self.model_dir).exists():
            model_path = str(Path(self.model_dir).resolve())
            logger.info(f"Using local model: {model_path}")
        else:
            # 否则使用模型名称，会自动下载
            model_path = self.model_name
            logger.info(f"Will download model if not cached: {model_path}")

        model = WhisperModel(
            model_path,
            device=self.device,
            compute_type=self.compute_type,
        )

        logger.info("Model loaded successfully")
        return model

    def _make_segments(self, segments: List[tuple]) -> List[ASRDataSeg]:
        """将 faster-whisper 的输出转换为 ASRDataSeg 列表"""
        asr_segments = []

        # 幻觉文本关键词列表
        hallucination_keywords = [
            "请不吝点赞 订阅 转发",
            "打赏支持明镜",
        ]

        for segment in segments:
            text = segment.text.strip()

            # 跳过空文本
            if not text:
                continue

            # 跳过音乐标记
            if text.startswith(("【", "[", "(", "（")):
                continue

            # 跳过包含幻觉关键词的文本
            if any(keyword in text for keyword in hallucination_keywords):
                continue

            # 创建 ASRDataSeg
            seg = ASRDataSeg(
                text=text,
                start=segment.start,
                end=segment.end,
            )

            # 如果需要单词级时间戳
            if self.need_word_time_stamp and hasattr(segment, 'words'):
                seg.words = []
                for word in segment.words:
                    seg.words.append({
                        'word': word.word,
                        'start': word.start,
                        'end': word.end,
                    })

            asr_segments.append(seg)

        return asr_segments

    def _run(
        self, callback: Optional[Callable[[int, str], None]] = None, **kwargs: Any
    ) -> str:
        def _default_callback(x, y):
            pass

        if callback is None:
            callback = _default_callback

        try:
            # 加载模型
            callback(*ASRStatus.TRANSCRIBING.with_progress(5))
            model = self._load_model()

            # 准备音频输入
            if isinstance(self.audio_input, str):
                audio_path = self.audio_input
            else:
                # 如果是二进制数据，保存到临时文件
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                if self.file_binary:
                    temp_file.write(self.file_binary)
                else:
                    raise ValueError("No audio data available")
                temp_file.close()
                audio_path = temp_file.name

            logger.info(f"Transcribing audio: {audio_path}")
            callback(*ASRStatus.TRANSCRIBING.with_progress(10))

            # 执行转录
            segments_list = []
            total_duration = None

            # 使用 transcribe 方法
            segments_iter, info = model.transcribe(
                audio_path,
                language=self.language,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters={
                    "threshold": self.vad_threshold,
                } if self.vad_filter else None,
                initial_prompt=self.prompt,
                word_timestamps=self.need_word_time_stamp,
            )

            total_duration = info.duration
            logger.info(f"Audio duration: {total_duration:.2f}s, Language: {info.language}")

            # 迭代所有片段并更新进度
            for segment in segments_iter:
                segments_list.append(segment)

                # 计算进度 (10% - 95%)
                if total_duration and total_duration > 0:
                    progress = int(10 + (segment.end / total_duration) * 85)
                    progress = min(progress, 95)
                    callback(progress, f"转录中: {segment.end:.1f}s / {total_duration:.1f}s")

            # 转换为 ASRDataSeg
            callback(*ASRStatus.TRANSCRIBING.with_progress(95))
            asr_segments = self._make_segments(segments_list)

            # 创建 ASRData 并转换为 SRT 格式
            asr_data = ASRData(segments=asr_segments)
            srt_content = asr_data.to_srt()

            callback(*ASRStatus.COMPLETED.callback_tuple())
            logger.info(f"Transcription completed: {len(asr_segments)} segments")

            # 清理临时文件
            if not isinstance(self.audio_input, str) and os.path.exists(audio_path):
                os.unlink(audio_path)

            return srt_content

        except Exception as e:
            logger.exception(f"Transcription failed: {e}")
            raise RuntimeError(f"Python Faster-Whisper 转录失败: {e}")

    def _get_key(self):
        """获取缓存key"""
        params = f"{self.model_name}-{self.language}-{self.device}-{self.vad_filter}"
        param_hash = hashlib.md5(params.encode()).hexdigest()
        return f"{self.crc32_hex}-{param_hash}"
