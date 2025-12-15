#!/usr/bin/env python
# coding:utf-8
"""测试 Python 版 Faster-Whisper"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_PATH = Path(__file__).parent
sys.path.insert(0, str(ROOT_PATH))

from app.common.config import cfg

# 加载配置
cfg.load('settings.json')

# 打印配置信息
print("=" * 60)
print("Python 版 Faster-Whisper 配置信息")
print("=" * 60)
print(f"转录模型: {cfg.get(cfg.transcribe_model)}")
print(f"Whisper 模型: {cfg.get(cfg.faster_whisper_model)}")
print(f"模型目录: {cfg.get(cfg.faster_whisper_model_dir)}")
print(f"设备: {cfg.get(cfg.faster_whisper_device)}")
print(f"VAD 过滤: {cfg.get(cfg.faster_whisper_vad_filter)}")
print(f"VAD 阈值: {cfg.get(cfg.faster_whisper_vad_threshold)}")
print("=" * 60)

# 检查模型目录是否存在
model_dir = cfg.get(cfg.faster_whisper_model_dir)
if model_dir:
    model_path = Path(model_dir)
    if model_path.exists():
        print(f"✓ 模型目录存在: {model_path}")
        print(f"  目录内容:")
        for item in model_path.iterdir():
            print(f"    - {item.name}")
    else:
        print(f"✗ 模型目录不存在: {model_path}")
        print(f"  请确保模型文件在此路径下")
else:
    print("⚠ 未配置模型目录，将使用模型名称自动下载")

print("=" * 60)

# 测试导入 faster-whisper
try:
    from faster_whisper import WhisperModel
    print("✓ faster-whisper 库导入成功")
    print(f"  版本: {WhisperModel.__module__}")
except ImportError as e:
    print(f"✗ faster-whisper 库导入失败: {e}")
    sys.exit(1)

# 测试导入 ASR 类
try:
    from app.core.asr.faster_whisper_python import FasterWhisperPythonASR
    print("✓ FasterWhisperPythonASR 类导入成功")
except ImportError as e:
    print(f"✗ FasterWhisperPythonASR 类导入失败: {e}")
    sys.exit(1)

print("=" * 60)
print("配置验证完成！")
print("=" * 60)
