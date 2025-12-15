# VideoCaptioner 文档索引

## 📚 文档目录

### 快速开始
- [README](README.md) - 项目概览和快速开始

### API 文档
- [API 快速入门](api/quickstart.md) - 5 分钟上手指南
- [RPC API 参考](api/rpc-api.md) - 完整的 API 接口文档
- [语言参数支持](api/LANGUAGE_PARAMETER_SUPPORT.md) - 转录语言参数详解

### 部署指南
- [Docker 部署](deployment/DOCKER_DEPLOYMENT.md) - 容器化部署完整指南
- [Master-Worker 架构](deployment/master-worker-architecture.md) - 分布式架构说明

### 配置参考
- [配置文件说明](configuration/settings.md) - settings.json 详细配置

## 🗂️ 文档结构

```
docs/
├── README.md                           # 主文档入口
├── INDEX.md                            # 文档索引（本文件）
├── api/                                # API 文档
│   ├── quickstart.md                  # 快速入门
│   ├── rpc-api.md                     # RPC API 参考
│   └── LANGUAGE_PARAMETER_SUPPORT.md  # 语言参数
├── deployment/                         # 部署文档
│   └── DOCKER_DEPLOYMENT.md           # Docker 部署
├── configuration/                      # 配置文档
│   └── settings.md                    # 配置说明
└── development/                        # 开发文档（待添加）
```

## 📖 推荐阅读顺序

### 新手入门
1. [README](README.md) - 了解项目
2. [Docker 部署](deployment/DOCKER_DEPLOYMENT.md) - 部署服务
3. [API 快速入门](api/quickstart.md) - 开始使用

### 深入使用
4. [RPC API 参考](api/rpc-api.md) - 详细 API
5. [配置文件说明](configuration/settings.md) - 自定义配置
6. [语言参数支持](api/LANGUAGE_PARAMETER_SUPPORT.md) - 高级功能

## 🔍 快速查找

### 我想...

**部署服务**
→ [Docker 部署](deployment/DOCKER_DEPLOYMENT.md)

**调用 API**
→ [API 快速入门](api/quickstart.md)
→ [RPC API 参考](api/rpc-api.md)

**修改配置**
→ [配置文件说明](configuration/settings.md)

**指定转录语言**
→ [语言参数支持](api/LANGUAGE_PARAMETER_SUPPORT.md)

**查看完整 API**
→ [RPC API 参考](api/rpc-api.md)

**了解支持的语言**
→ [语言参数支持](api/LANGUAGE_PARAMETER_SUPPORT.md#支持的语言代码)

## 📝 文档更新记录

- **2025-12-15**: 初始版本
  - 添加 Docker 部署文档
  - 添加 RPC API 参考
  - 添加语言参数支持文档
  - 添加配置文件说明
  - 添加 API 快速入门

## 🤝 贡献文档

如果发现文档有误或需要改进，欢迎：
- 提交 Issue
- 发起 Pull Request
- 通过邮件联系

---

**最后更新**: 2025-12-15
