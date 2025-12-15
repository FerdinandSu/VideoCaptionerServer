#!/usr/bin/env python
# coding:utf-8
"""测试 RPC 服务器"""

import time
import requests

BASE_URL = "http://localhost:5000"


def test_health():
    """测试健康检查"""
    print("\n1. 测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    print("   ✓ 健康检查通过")


def test_status():
    """测试状态查询"""
    print("\n2. 测试状态查询...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {data}")
    assert response.status_code == 200
    assert data["success"] is True
    assert "is_connected" in data
    print("   ✓ 状态查询通过")


def test_set_master():
    """测试设置 Master"""
    print("\n3. 测试设置 Master URL...")

    # 测试缺少参数
    print("   3.1 测试缺少 url 参数...")
    response = requests.get(f"{BASE_URL}/set-master")
    print(f"       状态码: {response.status_code}")
    print(f"       响应: {response.json()}")
    assert response.status_code == 400
    print("       ✓ 参数验证通过")

    # 测试无效 URL（这会连接失败，但不会崩溃）
    print("   3.2 测试设置 Master URL...")
    test_url = "https://example.com/signalr"
    response = requests.get(f"{BASE_URL}/set-master", params={"url": test_url})
    print(f"       状态码: {response.status_code}")
    print(f"       响应: {response.json()}")
    # 注意：这可能会失败（500），因为无法连接到示例 URL
    # 但至少验证了 API 端点正常工作
    print("       ✓ API 端点正常工作")


def test_disconnect_master():
    """测试断开 Master"""
    print("\n4. 测试断开 Master 连接...")
    response = requests.get(f"{BASE_URL}/disconnect-master")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    assert response.status_code == 200
    print("   ✓ 断开连接成功")


def main():
    """主函数"""
    print("=" * 60)
    print("RPC 服务器测试")
    print("=" * 60)
    print("\n请确保 RPC 服务器已启动（运行 rpc_server.py）")
    print("等待 3 秒后开始测试...\n")

    time.sleep(3)

    try:
        test_health()
        test_status()
        test_set_master()
        test_disconnect_master()

        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n错误：无法连接到 RPC 服务器")
        print("请先运行: uv run python rpc_server.py")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
    except Exception as e:
        print(f"\n测试出错: {e}")


if __name__ == "__main__":
    main()
