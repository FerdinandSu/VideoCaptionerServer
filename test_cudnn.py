#!/usr/bin/env python3
# coding: utf-8
"""测试 faster-whisper 和 cuDNN 是否正常工作（运行时测试）"""

import sys
import os

def test_faster_whisper():
    """测试 faster-whisper 是否可以导入和初始化"""
    print("=" * 60)
    print("测试: 检查 faster-whisper + GPU")
    print("=" * 60)

    try:
        from faster_whisper import WhisperModel
        print(f"✓ faster-whisper 导入成功")

        # 检查本地测试模型是否存在
        test_model_paths = [
            "/test/faster-whisper-tiny/",
            "/app/AppData/models/faster-whisper-tiny/",  # Docker 环境
            "resource/models/faster-whisper-tiny",      # 本地开发环境
            "AppData/models/faster-whisper-tiny",       # 备选路径
        ]

        model_path = None
        for path in test_model_paths:
            if os.path.exists(path):
                model_path = path
                break

        if model_path:
            print(f"  使用本地模型: {model_path}")
            model = WhisperModel(model_path, device="cuda", compute_type="float16")
            print(f"✓ 模型初始化成功")
            print(f"  设备: cuda")
            print(f"  计算类型: float16")
            del model
        else:
            print(f"  本地测试模型不存在")
            print(f"  搜索路径: {model_path}")
            print(f"  尝试下载 tiny 模型进行测试...")

            # 使用在线 tiny 模型进行测试
            model = WhisperModel("tiny", device="cuda", compute_type="float16")
            print(f"✓ 模型下载并初始化成功")
            print(f"  模型: tiny (在线下载)")
            print(f"  设备: cuda")
            print(f"  计算类型: float16")
            del model

        return True
    except Exception as e:
        print(f"✗ faster-whisper 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("faster-whisper GPU 环境测试")
    print("=" * 60 + "\n")

    passed = test_faster_whisper()

    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)

    if passed:
        print("\n🎉 测试通过！GPU 环境配置正确。\n")
        return 0
    else:
        print("\n❌ 测试失败，请检查 GPU 驱动和配置。\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
