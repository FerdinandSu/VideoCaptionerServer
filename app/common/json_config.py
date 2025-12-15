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
                    self._config_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config_data = {}
        else:
            self._config_data = {}

        # 加载配置值到各个 ConfigItem
        for item in self._config_items.values():
            key = item.key
            if key in self._config_data:
                try:
                    item.value = item.deserialize(self._config_data[key])
                except Exception:
                    item.value = item.default

    def save(self):
        """保存配置到 JSON 文件"""
        if self._config_path is None:
            return

        # 收集所有配置项的值
        for item in self._config_items.values():
            self._config_data[item.key] = item.serialize()

        # 确保目录存在
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存到 JSON 文件
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config_data, f, indent=2, ensure_ascii=False)

    def toDict(self, serialize: bool = True):
        """转换为字典"""
        if serialize:
            return {item.key: item.serialize() for item in self._config_items.values()}
        else:
            return {item.key: item.value for item in self._config_items.values()}
