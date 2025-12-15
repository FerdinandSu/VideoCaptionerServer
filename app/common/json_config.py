# coding:utf-8
"""基于 JSON 的配置管理系统，替代 qfluentwidgets 的 QConfig"""
import json
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Type, Union


class ConfigItem:
    """配置项基类"""

    def __init__(
        self,
        group: str,
        name: str,
        default: Any,
        validator: Optional[Callable[[Any], bool]] = None,
        serializer: Optional["ConfigSerializer"] = None,
        restart: bool = False,
    ):
        self.group = group
        self.name = name
        self.default = default
        self.validator = validator
        self.serializer = serializer
        self.restart = restart
        self._value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if self.validator and not self.validator.validate(val):
            val = self.validator.correct(val)
        self._value = val

    @property
    def key(self):
        return f"{self.group}.{self.name}"

    def serialize(self):
        """序列化配置值"""
        if self.serializer:
            return self.serializer.serialize(self._value)
        elif isinstance(self._value, Enum):
            return self._value.value
        elif isinstance(self._value, Path):
            return str(self._value)
        return self._value

    def deserialize(self, value):
        """反序列化配置值"""
        if self.serializer:
            return self.serializer.deserialize(value)
        elif self.default is not None and isinstance(self.default, Enum):
            enum_class = type(self.default)
            try:
                return enum_class(value)
            except (ValueError, KeyError):
                return self.default
        elif self.default is not None and isinstance(self.default, Path):
            return Path(value)
        return value


class OptionsConfigItem(ConfigItem):
    """选项配置项"""

    pass


class RangeConfigItem(ConfigItem):
    """范围配置项"""

    pass


class ConfigSerializer:
    """配置序列化器基类"""

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class EnumSerializer(ConfigSerializer):
    """枚举序列化器"""

    def __init__(self, enum_class: Type[Enum]):
        self.enum_class = enum_class

    def serialize(self, value):
        if isinstance(value, Enum):
            return value.value
        return value

    def deserialize(self, value):
        try:
            return self.enum_class(value)
        except (ValueError, KeyError):
            # 返回第一个枚举值作为默认值
            return list(self.enum_class)[0]


class Validator:
    """验证器基类"""

    def validate(self, value) -> bool:
        return True

    def correct(self, value):
        return value


class BoolValidator(Validator):
    """布尔值验证器"""

    def validate(self, value) -> bool:
        return isinstance(value, bool)

    def correct(self, value):
        return bool(value)


class RangeValidator(Validator):
    """范围验证器"""

    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, value) -> bool:
        return self.min_val <= value <= self.max_val

    def correct(self, value):
        return max(self.min_val, min(self.max_val, value))


class OptionsValidator(Validator):
    """选项验证器"""

    def __init__(self, options):
        if isinstance(options, type) and issubclass(options, Enum):
            self.options = list(options)
        else:
            self.options = options

    def validate(self, value) -> bool:
        return value in self.options

    def correct(self, value):
        return value if self.validate(value) else self.options[0]


class FolderValidator(Validator):
    """文件夹验证器"""

    def validate(self, value) -> bool:
        return True  # 不强制验证路径是否存在

    def correct(self, value):
        return value


class JsonConfig:
    """基于 JSON 的配置管理类"""

    def __init__(self):
        self._config_path = None
        self._config_data = {}

        # 收集所有 ConfigItem 类属性
        self._config_items = {}
        for name in dir(self):
            attr = getattr(type(self), name, None)
            if isinstance(attr, ConfigItem):
                self._config_items[name] = attr

        # 兼容性属性
        self.themeMode = type('ThemeMode', (), {'value': None})()
        self.themeColor = type('ThemeColor', (), {'value': None})()

        # 配置依赖关系 - 定义哪些配置项依赖于其他配置项的值
        self._config_dependencies = {}

    def get(self, item: ConfigItem, default=None):
        """获取配置项的值"""
        if isinstance(item, ConfigItem):
            return item.value
        return default

    def set(self, item: ConfigItem, value, save: bool = True):
        """设置配置项的值"""
        if isinstance(item, ConfigItem):
            item.value = value
            if save:
                self.save()

    def load(self, config_path: Union[str, Path]):
        """从 JSON 文件加载配置"""
        self._config_path = Path(config_path)

        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                raw_data = {}
        else:
            raw_data = {}

        # 将嵌套的 JSON 转换为扁平化的 key-value
        self._config_data = self._flatten_dict(raw_data)

        # 加载配置值到各个 ConfigItem
        for item in self._config_items.values():
            key = item.key
            if key in self._config_data:
                try:
                    item.value = item.deserialize(self._config_data[key])
                except Exception:
                    item.value = item.default

    def save(self):
        """保存配置到 JSON 文件（只保存相关的配置项）"""
        if self._config_path is None:
            return

        # 收集所有配置项的值，但只保存相关的
        flat_data = {}
        for item in self._config_items.values():
            # 检查这个配置项是否应该被保存
            if self._should_save_config(item):
                flat_data[item.key] = item.serialize()

        # 转换为嵌套的 JSON 格式
        nested_data = self._unflatten_dict(flat_data)

        # 确保目录存在
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存到 JSON 文件
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(nested_data, f, indent=2, ensure_ascii=False, sort_keys=True)

    def _should_save_config(self, item: ConfigItem) -> bool:
        """判断配置项是否应该被保存

        只保存以下配置项：
        1. 主选择配置项（如 LLMService, TranscribeModel）
        2. 与当前选择相关的配置项
        3. 通用配置项（如 Subtitle, Video, Save 等）
        """
        key = item.key
        group = item.group

        # 总是保存的组
        always_save_groups = {
            "Translate", "Subtitle", "Video", "SubtitleStyle",
            "Save", "MainWindow", "Update", "Cache", "RPC", "Transcribe"
        }

        if group in always_save_groups:
            return True

        # LLM 配置 - 只保存当前选择的服务
        if group == "LLM":
            if item.name == "LLMService":
                return True

            # 获取当前选择的服务
            llm_service_item = self._config_items.get("llm_service")
            if llm_service_item:
                service_value = llm_service_item.value
                service_name = service_value.name if hasattr(service_value, 'name') else str(service_value)

                # 检查配置项是否属于当前服务
                # 例如：如果服务是 OLLAMA，只保存 Ollama_ 开头的配置
                if service_name == "OLLAMA" and item.name.startswith("Ollama_"):
                    return True
                elif service_name == "OPENAI" and item.name.startswith("OpenAI_"):
                    return True
                elif service_name == "DEEPSEEK" and item.name.startswith("DeepSeek_"):
                    return True
                elif service_name == "SILICONCLOUD" and item.name.startswith("SiliconCloud_"):
                    return True
                elif service_name == "LM_STUDIO" and item.name.startswith("LmStudio_"):
                    return True
                elif service_name == "GEMINI" and item.name.startswith("Gemini_"):
                    return True
                elif service_name == "CHATGLM" and item.name.startswith("ChatGLM_"):
                    return True

            return False

        # Whisper 相关配置 - 根据转录模型决定
        if group in {"Whisper", "FasterWhisper", "WhisperAPI"}:
            transcribe_model_item = self._config_items.get("transcribe_model")
            if transcribe_model_item:
                model_value = transcribe_model_item.value
                model_name = model_value.name if hasattr(model_value, 'name') else str(model_value)

                # 根据转录模型保存对应的配置
                if group == "Whisper" and model_name == "WHISPER_CPP":
                    return True
                elif group == "FasterWhisper" and model_name in {"FASTER_WHISPER", "FASTER_WHISPER_PYTHON"}:
                    return True
                elif group == "WhisperAPI" and model_name == "WHISPER_API":
                    return True

            return False

        # 默认保存
        return True

    def _flatten_dict(self, nested_dict: dict) -> dict:
        """将嵌套的字典转换为扁平化的字典

        例如: {"LLM": {"Model": "gpt-4"}} -> {"LLM.Model": "gpt-4"}
        """
        flat_dict = {}

        def _flatten(d, parent_key=""):
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    _flatten(v, new_key)
                else:
                    flat_dict[new_key] = v

        _flatten(nested_dict)
        return flat_dict

    def _unflatten_dict(self, flat_dict: dict) -> dict:
        """将扁平化的字典转换为嵌套的字典

        例如: {"LLM.Model": "gpt-4"} -> {"LLM": {"Model": "gpt-4"}}
        """
        nested_dict = {}

        for key, value in flat_dict.items():
            parts = key.split(".")
            current = nested_dict

            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]

            current[parts[-1]] = value

        return nested_dict

    def toDict(self, serialize: bool = True):
        """转换为字典"""
        if serialize:
            flat_data = {item.key: item.serialize() for item in self._config_items.values()}
        else:
            flat_data = {item.key: item.value for item in self._config_items.values()}

        # 返回嵌套格式
        return self._unflatten_dict(flat_data)
