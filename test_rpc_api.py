"""RPC API 测试脚本"""

import requests
import time

# 配置
BASE_URL = "http://localhost:5000"


def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_get_status():
    """测试获取状态"""
    print("\n=== 测试获取状态 ===")
    response = requests.get(f"{BASE_URL}/api/rpc/get-status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def test_start_subtitize():
    """测试启动字幕化任务"""
    print("\n=== 测试启动字幕化任务 ===")
    data = {
        "video_path": "D:\\test\\video.mp4",
        "raw_subtitle_path": "D:\\test\\raw.srt",
        "translated_subtitle_path": "D:\\test\\translated.srt",
    }
    response = requests.post(f"{BASE_URL}/api/rpc/start-subtitize", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            return result.get("task_id")
    return None


def test_stop_subtitize(task_id: int):
    """测试停止字幕化任务"""
    print(f"\n=== 测试停止字幕化任务 (task_id={task_id}) ===")
    data = {"task_id": task_id}
    response = requests.post(f"{BASE_URL}/api/rpc/stop-subtitize", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")


def main():
    print("RPC API 测试脚本")
    print(f"Base URL: {BASE_URL}")
    print(f"Swagger UI: {BASE_URL}/api/docs")

    try:
        # 1. 健康检查
        test_health()

        # 2. 获取状态
        test_get_status()

        # 3. 启动任务（如果需要）
        # task_id = test_start_subtitize()

        # 4. 停止任务（如果需要）
        # if task_id and task_id > 0:
        #     time.sleep(2)
        #     test_stop_subtitize(task_id)

        print("\n\n✅ 所有测试完成！")
        print(f"\n访问 Swagger UI 进行更多测试: {BASE_URL}/api/docs")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到服务器: {BASE_URL}")
        print("请确保 RPC 服务器正在运行")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


if __name__ == "__main__":
    main()
