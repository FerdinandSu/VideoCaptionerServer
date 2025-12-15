# API 快速入门

本指南将帮助你快速开始使用 VideoCaptioner RPC API。

## 前置条件

- VideoCaptioner 服务已启动（参见[部署指南](../deployment/docker-deployment.md)）
- 服务运行在 `http://localhost:5000`

## 步骤 1: 验证服务

首先确认服务正常运行：

```bash
# 健康检查
curl http://localhost:5000/health

# 期望输出
# {"success": true, "status": "healthy"}
```

## 步骤 2: 准备视频文件

将视频文件放置在挂载的数据目录中：

```bash
# Docker 环境
cp video.mp4 ./data/

# 本地环境
cp video.mp4 ./work/
```

## 步骤 3: 启动转录任务

### 基本用法

```bash
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/video.mp4",
    "raw_subtitle_path": "/data/video.srt",
    "translated_subtitle_path": "/data/video.translated.srt"
  }'
```

**响应:**
```json
{
  "success": true,
  "task_id": 1,
  "message": "任务已启动: task_id=1"
}
```

### 指定语言

```bash
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/video.mp4",
    "raw_subtitle_path": "/data/video.srt",
    "translated_subtitle_path": "/data/video.translated.srt",
    "language": "en"
  }'
```

## 步骤 4: 监控任务进度

### 查询状态

```bash
curl http://localhost:5000/api/rpc/get-status
```

**响应示例（进行中）:**
```json
{
  "status": "busy",
  "current_task": {
    "task_id": 1,
    "state": "transcribing",
    "progress": 2500,
    "video_path": "/data/video.mp4",
    "message": "正在转录"
  }
}
```

**响应示例（已完成）:**
```json
{
  "status": "idle"
}
```

### 持续监控

```bash
# 每 2 秒查询一次状态
watch -n 2 'curl -s http://localhost:5000/api/rpc/get-status | jq'
```

## 步骤 5: 获取结果

任务完成后，字幕文件会保存在指定路径：

```bash
# 查看原始字幕
cat ./data/video.srt

# 查看翻译字幕
cat ./data/video.translated.srt
```

## 完整 Python 示例

```python
#!/usr/bin/env python
# coding: utf-8
"""VideoCaptioner API 使用示例"""

import requests
import time
from pathlib import Path

class VideoCaptioner:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def start_task(self, video_path, language=None):
        """启动字幕化任务"""
        video_name = Path(video_path).stem

        payload = {
            "video_path": video_path,
            "raw_subtitle_path": f"{video_path}.srt",
            "translated_subtitle_path": f"{video_path}.translated.srt",
        }

        if language:
            payload["language"] = language

        response = requests.post(
            f"{self.base_url}/api/rpc/start-subtitize",
            json=payload
        )
        return response.json()

    def get_status(self):
        """获取任务状态"""
        response = requests.get(f"{self.base_url}/api/rpc/get-status")
        return response.json()

    def stop_task(self, task_id):
        """停止任务"""
        response = requests.post(
            f"{self.base_url}/api/rpc/stop-subtitize",
            json={"task_id": task_id}
        )
        return response.json()

    def wait_for_completion(self, check_interval=2):
        """等待任务完成"""
        while True:
            status = self.get_status()

            if status["status"] == "idle":
                print("✓ 任务完成")
                return True

            if status["status"] == "busy":
                task = status["current_task"]
                progress = task["progress"] / 100
                state = task.get("message", task["state"])
                print(f"进度: {progress:5.1f}% - {state}")

            time.sleep(check_interval)


def main():
    # 创建客户端
    client = VideoCaptioner("http://localhost:5000")

    # 健康检查
    health = client.health_check()
    print(f"服务状态: {health}")

    # 启动任务
    result = client.start_task(
        video_path="/data/video.mp4",
        language="en"  # 可选：指定语言
    )

    if result["success"]:
        task_id = result["task_id"]
        print(f"✓ 任务已启动: task_id={task_id}")

        # 等待完成
        client.wait_for_completion()

        print("\n字幕文件:")
        print("  - 原始字幕: /data/video.mp4.srt")
        print("  - 翻译字幕: /data/video.mp4.translated.srt")
    else:
        print(f"✗ 启动失败: {result['message']}")


if __name__ == "__main__":
    main()
```

## 完整 JavaScript 示例

```javascript
/**
 * VideoCaptioner API 客户端
 */
class VideoCaptionerClient {
  constructor(baseUrl = 'http://localhost:5000') {
    this.baseUrl = baseUrl;
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }

  /**
   * 启动字幕化任务
   */
  async startTask(videoPath, language = null) {
    const payload = {
      video_path: videoPath,
      raw_subtitle_path: `${videoPath}.srt`,
      translated_subtitle_path: `${videoPath}.translated.srt`,
    };

    if (language) {
      payload.language = language;
    }

    const response = await fetch(`${this.baseUrl}/api/rpc/start-subtitize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    return await response.json();
  }

  /**
   * 获取任务状态
   */
  async getStatus() {
    const response = await fetch(`${this.baseUrl}/api/rpc/get-status`);
    return await response.json();
  }

  /**
   * 停止任务
   */
  async stopTask(taskId) {
    const response = await fetch(`${this.baseUrl}/api/rpc/stop-subtitize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId })
    });

    return await response.json();
  }

  /**
   * 等待任务完成
   */
  async waitForCompletion(onProgress, checkInterval = 2000) {
    while (true) {
      const status = await this.getStatus();

      if (status.status === 'idle') {
        console.log('✓ 任务完成');
        return true;
      }

      if (status.status === 'busy') {
        const task = status.current_task;
        const progress = task.progress / 100;
        const state = task.message || task.state;

        if (onProgress) {
          onProgress(progress, state);
        } else {
          console.log(`进度: ${progress.toFixed(1)}% - ${state}`);
        }
      }

      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
  }
}

// 使用示例
async function main() {
  const client = new VideoCaptionerClient('http://localhost:5000');

  // 健康检查
  const health = await client.healthCheck();
  console.log('服务状态:', health);

  // 启动任务
  const result = await client.startTask('/data/video.mp4', 'en');

  if (result.success) {
    console.log(`✓ 任务已启动: task_id=${result.task_id}`);

    // 等待完成
    await client.waitForCompletion((progress, state) => {
      console.log(`进度: ${progress.toFixed(1)}% - ${state}`);
    });

    console.log('\n字幕文件:');
    console.log('  - 原始字幕: /data/video.mp4.srt');
    console.log('  - 翻译字幕: /data/video.mp4.translated.srt');
  } else {
    console.log(`✗ 启动失败: ${result.message}`);
  }
}

main().catch(console.error);
```

## 常见问题

### 1. 如何处理长视频？

长视频会自动分块处理，无需特殊配置。进度会实时更新。

### 2. 支持批量处理吗？

当前版本同时只能处理一个任务。如需批量处理，需要等待前一个任务完成后再提交下一个。

### 3. 如何自定义翻译语言？

在 settings.json 中配置 `Subtitle.TargetLanguage`：

```json
{
  "Subtitle": {
    "TargetLanguage": "English"
  }
}
```

### 4. 如何禁用翻译？

```json
{
  "Subtitle": {
    "NeedTranslate": false
  }
}
```

## 下一步

- [RPC API 完整参考](rpc-api.md)
- [语言参数详解](language-parameter-support.md)
- [配置文件说明](../configuration/settings.md)
- [部署指南](../deployment/docker-deployment.md)
