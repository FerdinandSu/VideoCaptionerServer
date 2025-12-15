# VideoCaptioner 文档

> 视频自动字幕生成和翻译工具 - 纯后端 RPC 服务

## 📚 文档导航

### 快速开始

- [安装和部署](deployment/docker-deployment.md) - Docker 容器化部署指南
- [配置说明](configuration/settings.md) - 配置文件详解
- [API 使用](api/quickstart.md) - API 快速入门

### API 文档

- [RPC API 参考](api/rpc-api.md) - RPC 接口完整文档
- [语言参数支持](api/language-parameter-support.md) - 转录语言参数详解
- [错误处理](api/error-handling.md) - 错误码和异常处理

### 部署指南

- [Docker 部署](deployment/docker-deployment.md) - Docker Compose 部署
- [Master-Worker 架构](deployment/master-worker-architecture.md) - 分布式部署架构
- [生产环境部署](deployment/production.md) - 生产环境最佳实践
- [性能优化](deployment/performance.md) - 性能调优指南

### 开发文档

- [项目架构](development/architecture.md) - 系统架构说明
- [开发环境搭建](development/setup.md) - 本地开发环境
- [贡献指南](development/contributing.md) - 如何参与开发

### 配置参考

- [转录配置](configuration/transcribe.md) - FasterWhisper 配置
- [翻译配置](configuration/translate.md) - LLM 翻译配置
- [字幕配置](configuration/subtitle.md) - 字幕样式和格式

## 🚀 快速开始

### 使用 Docker（推荐）

```bash
# 克隆项目
git clone https://github.com/your-repo/VideoCaptioner.git
cd VideoCaptioner

# 准备配置
cp settings.json.docker settings.json

# 一键部署
bash deploy-docker.sh
```

### 访问服务

- **Swagger UI**: http://localhost:5000/api/docs
- **健康检查**: http://localhost:5000/health

### API 示例

```bash
# 启动字幕化任务
curl -X POST http://localhost:5000/api/rpc/start-subtitize \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/data/video.mp4",
    "raw_subtitle_path": "/data/video.srt",
    "translated_subtitle_path": "/data/video.translated.srt",
    "language": "en"
  }'

# 查看任务状态
curl http://localhost:5000/api/rpc/get-status
```

## 🔧 主要特性

### 转录引擎
- ✅ **FasterWhisper** - 本地 GPU 加速转录（推荐）
- ✅ **FasterWhisper Python** - Python 库版本
- ✅ **WhisperCpp** - C++ 实现
- ✅ **Whisper API** - OpenAI API

### 翻译服务
- ✅ **LLM 大模型翻译** - 支持 Ollama、DeepSeek、OpenAI 等
- ✅ **Google 翻译** - 免费在线翻译
- ✅ **微软翻译** - Bing 翻译服务
- ✅ **DeepLX** - DeepL 翻译代理

### 语言支持
- ✅ 自动语言检测
- ✅ 100+ 种语言转录
- ✅ 中文、英文、日语等主流语言
- ✅ 粤语、韩语等方言支持

### 字幕处理
- ✅ 智能分割断句
- ✅ 字幕优化（LLM）
- ✅ 翻译反思（提高翻译质量）
- ✅ 多种输出格式（SRT、ASS、VTT）

## 📖 系统架构

```
VideoCaptioner/
├── app/
│   ├── core/              # 核心功能
│   │   ├── asr/          # 语音识别
│   │   ├── translate/    # 翻译模块
│   │   ├── optimize/     # 字幕优化
│   │   └── split/        # 字幕分割
│   ├── rpc/              # RPC 服务
│   │   ├── flask_server.py    # Flask API
│   │   ├── rpc_service.py     # RPC 服务
│   │   ├── task_manager.py    # 任务管理
│   │   └── subtitize_executor.py  # 执行器
│   └── common/           # 公共模块
├── main.py               # 主程序入口
└── settings.json         # 配置文件
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

- [贡献指南](development/contributing.md)
- [问题反馈](https://github.com/your-repo/VideoCaptioner/issues)
- [Pull Request](https://github.com/your-repo/VideoCaptioner/pulls)

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

## 🔗 相关资源

- [GitHub 仓库](https://github.com/your-repo/VideoCaptioner)
- [FasterWhisper](https://github.com/guillaumekln/faster-whisper)
- [Ollama](https://ollama.ai/)
- [Docker](https://www.docker.com/)

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- GitHub Issues: https://github.com/your-repo/VideoCaptioner/issues
- Email: your-email@example.com

---

**最后更新**: 2025-12-15
