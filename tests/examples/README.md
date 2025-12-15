# 测试和示例脚本

本目录包含 VideoCaptioner 的测试和示例脚本。

## 示例脚本

### test_language_param.py
演示如何使用语言参数 API。

```bash
# 确保服务正在运行
uv run python tests/examples/test_language_param.py
```

### test_rpc_api.py
RPC API 的完整测试示例。

```bash
uv run python tests/examples/test_rpc_api.py
```

### test_faster_whisper_python.py
测试 FasterWhisper Python 库版本。

```bash
uv run python tests/examples/test_faster_whisper_python.py
```

### test_rpc.py
基础 RPC 功能测试。

```bash
uv run python tests/examples/test_rpc.py
```

## 使用说明

1. **启动服务**
   ```bash
   # Docker 环境
   docker compose up -d

   # 本地环境
   uv run python main.py
   ```

2. **运行测试**
   ```bash
   cd tests/examples
   uv run python test_language_param.py
   ```

3. **查看结果**
   测试脚本会输出详细的执行日志和结果。

## 注意事项

- 运行测试前确保服务已启动
- 某些测试需要准备测试视频文件
- 检查 settings.json 配置是否正确

## 相关文档

- [API 快速入门](../../docs/api/quickstart.md)
- [RPC API 参考](../../docs/api/rpc-api.md)
- [语言参数支持](../../docs/api/LANGUAGE_PARAMETER_SUPPORT.md)
