#!/usr/bin/env python
# coding:utf-8
"""测试 RPC API 的语言参数支持"""

import requests
import time

BASE_URL = "http://localhost:5000"


def start_task_with_language(video_path, language=None):
    """
    启动字幕化任务，可选指定语言

    Args:
        video_path: 视频文件路径
        language: 转录语言（可选）
                 - None: 使用配置文件中的语言
                 - "Auto" 或 None: 自动检测语言
                 - "en", "zh", "ja" 等: ISO 语言代码
                 - "英语", "中文", "日本語" 等: 语言名称
    """
    payload = {
        "video_path": video_path,
        "raw_subtitle_path": f"{video_path}.srt",
        "translated_subtitle_path": f"{video_path}.translated.srt",
    }

    # 如果指定了语言，添加到请求中
    if language:
        payload["language"] = language

    print(f"启动任务:")
    print(f"  - 视频路径: {video_path}")
    print(f"  - 语言: {language or '使用配置文件设置'}")
    print()

    response = requests.post(
        f"{BASE_URL}/api/rpc/start-subtitize",
        json=payload
    )

    result = response.json()
    if result["success"]:
        task_id = result["task_id"]
        print(f"✓ 任务已启动: task_id={task_id}")
        return task_id
    else:
        print(f"✗ 启动失败: {result['message']}")
        return None


def get_status():
    """获取任务状态"""
    response = requests.get(f"{BASE_URL}/api/rpc/get-status")
    return response.json()


def monitor_task(task_id):
    """监控任务进度"""
    print("\n监控任务进度...")
    print("-" * 60)

    while True:
        status = get_status()

        if status["status"] == "idle":
            print("任务已完成")
            break

        task = status.get("current_task")
        if task and task["task_id"] == task_id:
            progress = task["progress"] / 100  # 转换为百分比
            state = task["state"]
            print(f"进度: {progress:5.2f}% - {state}")

        time.sleep(2)


# 示例用法
if __name__ == "__main__":
    print("=" * 60)
    print("RPC API 语言参数测试")
    print("=" * 60)
    print()

    # 示例 1: 使用配置文件中的语言设置（Auto）
    print("示例 1: 使用默认语言（配置文件）")
    print("-" * 60)
    task_id = start_task_with_language("test_video_1.mp4")
    if task_id:
        monitor_task(task_id)

    print("\n" + "=" * 60 + "\n")

    # 示例 2: 明确指定使用英语
    print("示例 2: 明确指定英语 (en)")
    print("-" * 60)
    task_id = start_task_with_language("test_video_2.mp4", language="en")
    if task_id:
        monitor_task(task_id)

    print("\n" + "=" * 60 + "\n")

    # 示例 3: 使用中文名称
    print("示例 3: 使用中文语言名称")
    print("-" * 60)
    task_id = start_task_with_language("test_video_3.mp4", language="中文")
    if task_id:
        monitor_task(task_id)

    print("\n" + "=" * 60 + "\n")

    # 示例 4: 自动检测
    print("示例 4: 自动检测语言")
    print("-" * 60)
    task_id = start_task_with_language("test_video_4.mp4", language="Auto")
    if task_id:
        monitor_task(task_id)
