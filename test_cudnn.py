#!/usr/bin/env python3
# coding: utf-8
"""测试 faster-whisper 和 cuDNN 是否正常工作"""

import sys
import os

def test_cudnn():
    """测试 cuDNN 是否可以导入"""
    print("=" * 60)
    print("测试 1: 检查 cuDNN 库")
    print("=" * 60)

    try:
        import nvidia.cudnn
        print(f"✓ cuDNN 导入成功")
        print(f"  版本: {nvidia.cudnn.__version__}")
        print(f"  路径: {nvidia.cudnn.__path__[0]}")

        # 检查库文件
        cudnn_lib_path = os.path.join(nvidia.cudnn.__path__[0], 'lib')
        if os.path.exists(cudnn_lib_path):
            libs = [f for f in os.listdir(cudnn_lib_path) if 'libcudnn' in f]
            print(f"  库文件数量: {len(libs)}")
            if libs:
                print(f"  示例: {libs[0]}")

        return True
    except Exception as e:
        print(f"✗ cuDNN 导入失败: {e}")
        return False


def test_cublas():
    """测试 cuBLAS 是否可以导入"""
    print("\n" + "=" * 60)
    print("测试 2: 检查 cuBLAS 库")
    print("=" * 60)

    try:
        import nvidia.cublas
        print(f"✓ cuBLAS 导入成功")
        print(f"  版本: {nvidia.cublas.__version__}")
        return True
    except Exception as e:
        print(f"✗ cuBLAS 导入失败: {e}")
        return False


def test_faster_whisper():
    """测试 faster-whisper 是否可以导入和初始化"""
    print("\n" + "=" * 60)
    print("测试 3: 检查 faster-whisper")
    print("=" * 60)

    try:
        from faster_whisper import WhisperModel
        print(f"✓ faster-whisper 导入成功")

        # 检查本地测试模型是否存在
        test_model_paths = [
            "/app/AppData/models/faster-whisper-tiny",  # Docker 环境
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
            print(f"⚠ 本地测试模型不存在，跳过模型加载测试")
            print(f"  搜索路径: {test_model_paths}")
            print(f"  提示: faster-whisper 库导入成功，基本功能正常")

        return True
    except Exception as e:
        print(f"✗ faster-whisper 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("faster-whisper + cuDNN 环境测试")
    print("=" * 60 + "\n")

    results = []

    # 测试 1: cuDNN
    results.append(("cuDNN", test_cudnn()))

    # 测试 2: cuBLAS
    results.append(("cuBLAS", test_cublas()))

    # 测试 3: faster-whisper
    results.append(("faster-whisper", test_faster_whisper()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:20} : {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 所有测试通过！环境配置正确。\n")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查配置。\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
