import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from app.core.translate.types import TargetLanguage


@dataclass
class SubtitleProcessData:
    """字幕处理数据（翻译/优化通用）"""

    index: int
    original_text: str
    translated_text: str = ""
    optimized_text: str = ""


class SupportedAudioFormats(Enum):
    """支持的音频格式"""

    AAC = "aac"
    AC3 = "ac3"
    AIFF = "aiff"
    AMR = "amr"
    APE = "ape"
    AU = "au"
    FLAC = "flac"
    M4A = "m4a"
    MP2 = "mp2"
    MP3 = "mp3"
    MKA = "mka"
    OGA = "oga"
    OGG = "ogg"
    OPUS = "opus"
    RA = "ra"
    WAV = "wav"
    WMA = "wma"


class SupportedVideoFormats(Enum):
    """支持的视频格式"""

    MP4 = "mp4"
    WEBM = "webm"
    OGM = "ogm"
    MOV = "mov"
    MKV = "mkv"
    AVI = "avi"
    WMV = "wmv"
    FLV = "flv"
    M4V = "m4v"
    TS = "ts"
    MPG = "mpg"
    MPEG = "mpeg"
    VOB = "vob"
    ASF = "asf"
    RM = "rm"
    RMVB = "rmvb"
    M2TS = "m2ts"
    MTS = "mts"
    DV = "dv"
    GXF = "gxf"
    TOD = "tod"
    MXF = "mxf"
    F4V = "f4v"


class SupportedSubtitleFormats(Enum):
    """支持的字幕格式"""

    SRT = "srt"
    ASS = "ass"
    VTT = "vtt"


class OutputSubtitleFormatEnum(Enum):
    """字幕输出格式"""

    SRT = "srt"
    ASS = "ass"
    VTT = "vtt"
    JSON = "json"
    TXT = "txt"


class TranscribeOutputFormatEnum(Enum):
    """转录输出格式"""

    SRT = "SRT"
    ASS = "ASS"
    VTT = "VTT"
    TXT = "TXT"
    ALL = "All"


class LLMServiceEnum(Enum):
    """LLM服务"""

    OPENAI = "OpenAI"
    SILICON_CLOUD = "SiliconCloud"
    DEEPSEEK = "DeepSeek"
    OLLAMA = "Ollama"
    LM_STUDIO = "LM Studio"
    GEMINI = "Gemini"
    CHATGLM = "ChatGLM"


class TranscribeModelEnum(Enum):
    """转录模型"""

    BIJIAN = "B 接口"
    JIANYING = "J 接口"
    WHISPER_API = "Whisper [API] ✨"
    FASTER_WHISPER = "FasterWhisper ✨"
    FASTER_WHISPER_PYTHON = "FasterWhisper [Python] 🐍"
    WHISPER_CPP = "WhisperCpp"


class TranslatorServiceEnum(Enum):
    """翻译器服务"""

    OPENAI = "LLM 大模型翻译"
    DEEPLX = "DeepLx 翻译"
    BING = "微软翻译"
    GOOGLE = "谷歌翻译"


class VadMethodEnum(Enum):
    """VAD方法"""

    SILERO_V3 = "silero_v3"  # 通常比 v4 准确性低，但没有 v4 的一些怪癖
    SILERO_V4 = (
        "silero_v4"  # 与 silero_v4_fw 相同。运行原始 Silero 的代码，而不是适配过的代码
    )
    SILERO_V5 = (
        "silero_v5"  # 与 silero_v5_fw 相同。运行原始 Silero 的代码，而不是适配过的代码)
    )
    SILERO_V4_FW = (
        "silero_v4_fw"  # 默认模型。最准确的 Silero 版本，有一些非致命的小问题
    )
    # SILERO_V5_FW = "silero_v5_fw"  # 准确性差。不是 VAD，而是某种语音的随机检测器，有各种致命的小问题。避免使用！
    PYANNOTE_V3 = "pyannote_v3"  # 最佳准确性，支持 CUDA
    PYANNOTE_ONNX_V3 = "pyannote_onnx_v3"  # pyannote_v3 的轻量版。与 Silero v4 的准确性相似，可能稍好，支持 CUDA
    WEBRTC = "webrtc"  # 准确性低，过时的 VAD。仅接受 'vad_min_speech_duration_ms' 和 'vad_speech_pad_ms'
    AUDITOK = "auditok"  # 实际上这不是 VAD，而是 AAD - 音频活动检测


class SubtitleLayoutEnum(Enum):
    """字幕布局"""

    TRANSLATE_ON_TOP = "译文在上"
    ORIGINAL_ON_TOP = "原文在上"
    ONLY_ORIGINAL = "仅原文"
    ONLY_TRANSLATE = "仅译文"


class VideoQualityEnum(Enum):
    """视频合成质量"""

    ULTRA_HIGH = "极高质量"
    HIGH = "高质量"
    MEDIUM = "中等质量"
    LOW = "低质量"

    def get_crf(self) -> int:
        """获取对应的 CRF 值（越小质量越高，文件越大）"""
        crf_map = {
            VideoQualityEnum.ULTRA_HIGH: 18,
            VideoQualityEnum.HIGH: 23,
            VideoQualityEnum.MEDIUM: 28,
            VideoQualityEnum.LOW: 32,
        }
        return crf_map[self]

    def get_preset(
        self,
    ) -> Literal[
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
    ]:
        """获取对应的 FFmpeg preset 值（影响编码速度）"""
        preset_map: dict[
            VideoQualityEnum,
            Literal[
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ],
        ] = {
            VideoQualityEnum.ULTRA_HIGH: "slow",
            VideoQualityEnum.HIGH: "medium",
            VideoQualityEnum.MEDIUM: "medium",
            VideoQualityEnum.LOW: "fast",
        }
        return preset_map[self]


class TranscribeLanguageEnum(Enum):
    """转录语言"""

    AUTO = "Auto"
    ENGLISH = "英语"
    CHINESE = "中文"
    JAPANESE = "日本語"
    KOREAN = "韩语"
    YUE = "粤语"
    FRENCH = "法语"
    GERMAN = "德语"
    SPANISH = "西班牙语"
    RUSSIAN = "俄语"
    PORTUGUESE = "葡萄牙语"
    TURKISH = "土耳其语"
    POLISH = "Polish"
    CATALAN = "Catalan"
    DUTCH = "Dutch"
    ARABIC = "Arabic"
    SWEDISH = "Swedish"
    ITALIAN = "Italian"
    INDONESIAN = "Indonesian"
    HINDI = "Hindi"
    FINNISH = "Finnish"
    VIETNAMESE = "Vietnamese"
    HEBREW = "Hebrew"
    UKRAINIAN = "Ukrainian"
    GREEK = "Greek"
    MALAY = "Malay"
    CZECH = "Czech"
    ROMANIAN = "Romanian"
    DANISH = "Danish"
    HUNGARIAN = "Hungarian"
    TAMIL = "Tamil"
    NORWEGIAN = "Norwegian"
    THAI = "Thai"
    URDU = "Urdu"
    CROATIAN = "Croatian"
    BULGARIAN = "Bulgarian"
    LITHUANIAN = "Lithuanian"
    LATIN = "Latin"
    MAORI = "Maori"
    MALAYALAM = "Malayalam"
    WELSH = "Welsh"
    SLOVAK = "Slovak"
    TELUGU = "Telugu"
    PERSIAN = "Persian"
    LATVIAN = "Latvian"
    BENGALI = "Bengali"
    SERBIAN = "Serbian"
    AZERBAIJANI = "Azerbaijani"
    SLOVENIAN = "Slovenian"
    KANNADA = "Kannada"
    ESTONIAN = "Estonian"
    MACEDONIAN = "Macedonian"
    BRETON = "Breton"
    BASQUE = "Basque"
    ICELANDIC = "Icelandic"
    ARMENIAN = "Armenian"
    NEPALI = "Nepali"
    MONGOLIAN = "Mongolian"
    BOSNIAN = "Bosnian"
    KAZAKH = "Kazakh"
    ALBANIAN = "Albanian"
    SWAHILI = "Swahili"
    GALICIAN = "Galician"
    MARATHI = "Marathi"
    PUNJABI = "Punjabi"
    SINHALA = "Sinhala"
    KHMER = "Khmer"
    SHONA = "Shona"
    YORUBA = "Yoruba"
    SOMALI = "Somali"
    AFRIKAANS = "Afrikaans"
    OCCITAN = "Occitan"
    GEORGIAN = "Georgian"
    BELARUSIAN = "Belarusian"
    TAJIK = "Tajik"

    @staticmethod
    def to_language_code(value) -> str:
        """将 TranscribeLanguageEnum 转换为 ISO 语言代码

        Args:
            value: TranscribeLanguageEnum 枚举值或字符串

        Returns:
            ISO 语言代码，如果无法识别则返回 None（自动检测）
        """
        # 语言名称到代码的映射
        language_map = {
            "Auto": None,
            "英语": "en",
            "中文": "zh",
            "日本語": "ja",
            "韩语": "ko",
            "粤语": "yue",
            "法语": "fr",
            "德语": "de",
            "西班牙语": "es",
            "俄语": "ru",
            "葡萄牙语": "pt",
            "土耳其语": "tr",
            "Polish": "pl",
            "Catalan": "ca",
            "Dutch": "nl",
            "Arabic": "ar",
            "Swedish": "sv",
            "Italian": "it",
            "Indonesian": "id",
            "Hindi": "hi",
            "Finnish": "fi",
            "Vietnamese": "vi",
            "Hebrew": "he",
            "Ukrainian": "uk",
            "Greek": "el",
            "Malay": "ms",
            "Czech": "cs",
            "Romanian": "ro",
            "Danish": "da",
            "Hungarian": "hu",
            "Tamil": "ta",
            "Norwegian": "no",
            "Thai": "th",
            "Urdu": "ur",
            "Croatian": "hr",
            "Bulgarian": "bg",
            "Lithuanian": "lt",
            "Latin": "la",
            "Maori": "mi",
            "Malayalam": "ml",
            "Welsh": "cy",
            "Slovak": "sk",
            "Telugu": "te",
            "Persian": "fa",
            "Latvian": "lv",
            "Bengali": "bn",
            "Serbian": "sr",
            "Azerbaijani": "az",
            "Slovenian": "sl",
            "Kannada": "kn",
            "Estonian": "et",
            "Macedonian": "mk",
            "Breton": "br",
            "Basque": "eu",
            "Icelandic": "is",
            "Armenian": "hy",
            "Nepali": "ne",
            "Mongolian": "mn",
            "Bosnian": "bs",
            "Kazakh": "kk",
            "Albanian": "sq",
            "Swahili": "sw",
            "Galician": "gl",
            "Marathi": "mr",
            "Punjabi": "pa",
            "Sinhala": "si",
            "Khmer": "km",
            "Shona": "sn",
            "Yoruba": "yo",
            "Somali": "so",
            "Afrikaans": "af",
            "Occitan": "oc",
            "Georgian": "ka",
            "Belarusian": "be",
            "Tajik": "tg",
        }

        # 如果是枚举，取其 value
        if isinstance(value, TranscribeLanguageEnum):
            value = value.value

        # 如果已经是语言代码（2-3个字母），直接返回
        if isinstance(value, str) and len(value) <= 3 and value.lower() in [
            "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs",
            "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi",
            "fo", "fr", "gl", "gu", "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy",
            "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb",
            "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt",
            "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru",
            "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw",
            "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi",
            "yi", "yo", "zh", "yue"
        ]:
            return value.lower()

        # 映射语言名称到代码
        return language_map.get(value, None)


class WhisperModelEnum(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE_V1 = "large-v1"
    LARGE_V2 = "large-v2"


class FasterWhisperModelEnum(Enum):
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE_V1 = "large-v1"
    LARGE_V2 = "large-v2"
    LARGE_V3 = "large-v3"
    LARGE_V3_TURBO = "large-v3-turbo"


LANGUAGES = {
    "英语": "en",
    "中文": "zh",
    "日本語": "ja",
    "德语": "de",
    "粤语": "yue",
    "西班牙语": "es",
    "俄语": "ru",
    "韩语": "ko",
    "法语": "fr",
    "葡萄牙语": "pt",
    "土耳其语": "tr",
    "English": "en",
    "Chinese": "zh",
    "German": "de",
    "Spanish": "es",
    "Russian": "ru",
    "Korean": "ko",
    "French": "fr",
    "Japanese": "ja",
    "Portuguese": "pt",
    "Turkish": "tr",
    "Polish": "pl",
    "Catalan": "ca",
    "Dutch": "nl",
    "Arabic": "ar",
    "Swedish": "sv",
    "Italian": "it",
    "Indonesian": "id",
    "Hindi": "hi",
    "Finnish": "fi",
    "Vietnamese": "vi",
    "Hebrew": "he",
    "Ukrainian": "uk",
    "Greek": "el",
    "Malay": "ms",
    "Czech": "cs",
    "Romanian": "ro",
    "Danish": "da",
    "Hungarian": "hu",
    "Tamil": "ta",
    "Norwegian": "no",
    "Thai": "th",
    "Urdu": "ur",
    "Croatian": "hr",
    "Bulgarian": "bg",
    "Lithuanian": "lt",
    "Latin": "la",
    "Maori": "mi",
    "Malayalam": "ml",
    "Welsh": "cy",
    "Slovak": "sk",
    "Telugu": "te",
    "Persian": "fa",
    "Latvian": "lv",
    "Bengali": "bn",
    "Serbian": "sr",
    "Azerbaijani": "az",
    "Slovenian": "sl",
    "Kannada": "kn",
    "Estonian": "et",
    "Macedonian": "mk",
    "Breton": "br",
    "Basque": "eu",
    "Icelandic": "is",
    "Armenian": "hy",
    "Nepali": "ne",
    "Mongolian": "mn",
    "Bosnian": "bs",
    "Kazakh": "kk",
    "Albanian": "sq",
    "Swahili": "sw",
    "Galician": "gl",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Sinhala": "si",
    "Khmer": "km",
    "Shona": "sn",
    "Yoruba": "yo",
    "Somali": "so",
    "Afrikaans": "af",
    "Occitan": "oc",
    "Georgian": "ka",
    "Belarusian": "be",
    "Tajik": "tg",
    "Sindhi": "sd",
    "Gujarati": "gu",
    "Amharic": "am",
    "Yiddish": "yi",
    "Lao": "lo",
    "Uzbek": "uz",
    "Faroese": "fo",
    "Haitian Creole": "ht",
    "Pashto": "ps",
    "Turkmen": "tk",
    "Nynorsk": "nn",
    "Maltese": "mt",
    "Sanskrit": "sa",
    "Luxembourgish": "lb",
    "Myanmar": "my",
    "Tibetan": "bo",
    "Tagalog": "tl",
    "Malagasy": "mg",
    "Assamese": "as",
    "Tatar": "tt",
    "Hawaiian": "haw",
    "Lingala": "ln",
    "Hausa": "ha",
    "Bashkir": "ba",
    "Javanese": "jw",
    "Sundanese": "su",
    "Cantonese": "yue",
}


@dataclass
class AudioStreamInfo:
    """音频流信息"""

    index: int  # 音轨在视频中的实际索引（如 0, 1, 2 或 2, 3, 4）
    codec: str  # 音频编解码器（如 aac, mp3, opus）
    language: str = ""  # 语言标签（如 eng, chi, deu）
    title: str = ""  # 音轨标题（可选）


@dataclass
class VideoInfo:
    """视频信息类"""

    file_name: str
    file_path: str
    width: int
    height: int
    fps: float
    duration_seconds: float
    bitrate_kbps: int
    video_codec: str
    audio_codec: str
    audio_sampling_rate: int
    thumbnail_path: str
    audio_streams: list[AudioStreamInfo] = field(default_factory=list)  # 音频流列表


@dataclass
class TranscribeConfig:
    """转录配置类"""

    transcribe_model: Optional[TranscribeModelEnum] = None
    transcribe_language: str = ""
    need_word_time_stamp: bool = True
    output_format: Optional[TranscribeOutputFormatEnum] = None
    # Whisper Cpp 配置
    whisper_model: Optional[WhisperModelEnum] = None
    # Whisper API 配置
    whisper_api_key: Optional[str] = None
    whisper_api_base: Optional[str] = None
    whisper_api_model: Optional[str] = None
    whisper_api_prompt: Optional[str] = None
    # Faster Whisper 配置
    faster_whisper_program: Optional[str] = None
    faster_whisper_model: Optional[FasterWhisperModelEnum] = None
    faster_whisper_model_dir: Optional[str] = None
    faster_whisper_device: str = "cuda"
    faster_whisper_vad_filter: bool = True
    faster_whisper_vad_threshold: float = 0.5
    faster_whisper_vad_method: Optional[VadMethodEnum] = VadMethodEnum.SILERO_V3
    faster_whisper_ff_mdx_kim2: bool = False
    faster_whisper_one_word: bool = True
    faster_whisper_prompt: Optional[str] = None

    def _mask_key(self, key: Optional[str]) -> str:
        """Mask sensitive key for display"""
        if not key or len(key) <= 12:
            return "****"
        return f"{key[:4]}...{key[-4:]}"

    def print_config(self) -> str:
        """Print transcription configuration"""
        lines = ["=========== Transcription Task ==========="]
        lines.append(
            f"Model: {self.transcribe_model.value if self.transcribe_model else 'None'}"
        )
        lines.append(f"Language: {self.transcribe_language or 'Auto'}")
        lines.append(f"Word Timestamp: {self.need_word_time_stamp}")
        lines.append(f"Output Format: {self.output_format.value if self.output_format else 'None'}")

        if self.transcribe_model == TranscribeModelEnum.WHISPER_API:
            lines.append(f"API Base: {self.whisper_api_base}")
            lines.append(f"API Key: {self._mask_key(self.whisper_api_key)}")
            lines.append(f"API Model: {self.whisper_api_model}")
            if self.whisper_api_prompt:
                lines.append(f"Prompt: {self.whisper_api_prompt[:30]}...")

        elif self.transcribe_model == TranscribeModelEnum.FASTER_WHISPER:
            lines.append(
                f"Model: {self.faster_whisper_model.value if self.faster_whisper_model else 'None'}"
            )
            lines.append(f"Device: {self.faster_whisper_device}")
            lines.append(f"VAD Filter: {self.faster_whisper_vad_filter}")
            if self.faster_whisper_vad_filter:
                lines.append(
                    f"VAD Method: {self.faster_whisper_vad_method.value if self.faster_whisper_vad_method else 'None'}"
                )
                lines.append(f"VAD Threshold: {self.faster_whisper_vad_threshold}")
            lines.append(f"One Word Per Segment: {self.faster_whisper_one_word}")

        elif self.transcribe_model == TranscribeModelEnum.WHISPER_CPP:
            lines.append(
                f"Model: {self.whisper_model.value if self.whisper_model else 'None'}"
            )

        lines.append("=" * 42)
        return "\n".join(lines)


@dataclass
class SubtitleConfig:
    """字幕处理配置类"""

    # 翻译配置
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    llm_model: Optional[str] = None
    deeplx_endpoint: Optional[str] = None
    # 翻译服务
    translator_service: Optional[TranslatorServiceEnum] = None
    need_translate: bool = False
    need_optimize: bool = False
    need_reflect: bool = False
    thread_num: int = 10
    batch_size: int = 10
    # 字幕布局和分割
    subtitle_layout: SubtitleLayoutEnum = SubtitleLayoutEnum.ORIGINAL_ON_TOP
    max_word_count_cjk: int = 12
    max_word_count_english: int = 18
    need_split: bool = True
    target_language: Optional["TargetLanguage"] = None
    subtitle_style: Optional[str] = None
    custom_prompt_text: Optional[str] = None

    def _mask_key(self, key: Optional[str]) -> str:
        """Mask sensitive key for display"""
        if not key or len(key) <= 8:
            return "****"
        return f"{key[:4]}...{key[-4:]}"

    def print_config(self) -> str:
        """Print subtitle processing configuration"""
        lines = ["=========== Subtitle Processing Task ==========="]

        if self.need_split:
            lines.append("Split: Yes")
            lines.append(f"  Max Words (CJK): {self.max_word_count_cjk}")
            lines.append(f"  Max Words (English): {self.max_word_count_english}")

        if self.need_optimize:
            lines.append("Optimize: Yes")
            lines.append(f"  Model: {self.llm_model or 'None'}")
            if self.custom_prompt_text:
                lines.append(f"  Custom Prompt: {self.custom_prompt_text[:30]}...")

        if self.need_translate:
            lines.append("Translate: Yes")
            lines.append(
                f"  Service: {self.translator_service.value if self.translator_service else 'None'}"
            )
            if self.translator_service == TranslatorServiceEnum.OPENAI:
                lines.append(f"  API Base: {self.base_url}")
                lines.append(f"  API Key: {self._mask_key(self.api_key)}")
                lines.append(f"  Model: {self.llm_model}")
                lines.append(f"  Reflect Translation: {self.need_reflect}")
            elif self.translator_service == TranslatorServiceEnum.DEEPLX:
                lines.append(f"  DeepLX Endpoint: {self.deeplx_endpoint}")
            lines.append(
                f"  Target Language: {self.target_language.value if self.target_language else 'None'}"
            )
            lines.append(f"  Concurrency: {self.thread_num}")
            lines.append(f"  Batch Size: {self.batch_size}")

        lines.append(f"Layout: {self.subtitle_layout.value}")
        lines.append("=" * 48)
        return "\n".join(lines)


@dataclass
class SynthesisConfig:
    """视频合成配置类"""

    need_video: bool = True
    soft_subtitle: bool = True
    video_quality: VideoQualityEnum = VideoQualityEnum.MEDIUM

    def print_config(self) -> str:
        """Print video synthesis configuration"""
        lines = ["=========== Video Synthesis Task ==========="]
        lines.append(f"Generate Video: {self.need_video}")
        if self.need_video:
            lines.append(f"Subtitle Type: {'Soft' if self.soft_subtitle else 'Hard'}")
            lines.append(f"Video Quality: {self.video_quality.value}")
            lines.append(f"  CRF: {self.video_quality.get_crf()}")
            lines.append(f"  Preset: {self.video_quality.get_preset()}")
        lines.append("=" * 44)
        return "\n".join(lines)


@dataclass
class TranscribeTask:
    """转录任务类"""

    queued_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    # 输入文件
    file_path: Optional[str] = None

    # 输出字幕文件
    output_path: Optional[str] = None

    # 是否需要执行下一个任务（字幕处理）
    need_next_task: bool = False

    # 选中的音轨索引
    selected_audio_track_index: int = 0

    transcribe_config: Optional[TranscribeConfig] = None


@dataclass
class SubtitleTask:
    """字幕任务类"""

    queued_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    # 输入原始字幕文件
    subtitle_path: str = ""
    # 输入原始视频文件
    video_path: Optional[str] = None

    # 输出 断句、优化、翻译 后的字幕文件
    output_path: Optional[str] = None

    # 是否需要执行下一个任务（视频合成）
    need_next_task: bool = True

    subtitle_config: Optional[SubtitleConfig] = None


@dataclass
class SynthesisTask:
    """视频合成任务类"""

    queued_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    # 输入
    video_path: Optional[str] = None
    subtitle_path: Optional[str] = None

    # 输出
    output_path: Optional[str] = None

    # 是否需要执行下一个任务（预留）
    need_next_task: bool = False

    synthesis_config: Optional[SynthesisConfig] = None


@dataclass
class TranscriptAndSubtitleTask:
    """转录和字幕任务类"""

    queued_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    # 输入
    file_path: Optional[str] = None

    # 输出
    output_path: Optional[str] = None

    transcribe_config: Optional[TranscribeConfig] = None
    subtitle_config: Optional[SubtitleConfig] = None


@dataclass
class FullProcessTask:
    """完整处理任务类(转录+字幕+合成)"""

    queued_at: Optional[datetime.datetime] = None
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None

    # 输入
    file_path: Optional[str] = None
    # 输出
    output_path: Optional[str] = None

    transcribe_config: Optional[TranscribeConfig] = None
    subtitle_config: Optional[SubtitleConfig] = None
    synthesis_config: Optional[SynthesisConfig] = None


class BatchTaskType(Enum):
    """批量处理任务类型"""

    TRANSCRIBE = "批量转录"
    SUBTITLE = "批量字幕"
    TRANS_SUB = "转录+字幕"
    FULL_PROCESS = "全流程处理"

    def __str__(self):
        return self.value


class BatchTaskStatus(Enum):
    """批量处理任务状态"""

    WAITING = "等待中"
    RUNNING = "处理中"
    COMPLETED = "已完成"
    FAILED = "失败"

    def __str__(self):
        return self.value
