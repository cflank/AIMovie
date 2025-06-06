# 🎬 AIMovie Cloud - 智能视频解说生成器

[![GitHub Stars](https://img.shields.io/github/stars/cflank/AIMovie?style=social)](https://github.com/cflank/AIMovie/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/cflank/AIMovie?style=social)](https://github.com/cflank/AIMovie/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/cflank/AIMovie)](https://github.com/cflank/AIMovie/issues)
[![GitHub License](https://img.shields.io/github/license/cflank/AIMovie)](https://github.com/cflank/AIMovie/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)

> 🌐 **完全基于云端API的智能视频解说生成器** - 无需GPU硬件，高性价比，一键部署

## 🌟 项目简介

AIMovie Cloud 是一个基于云端AI服务的智能视频解说生成器，能够自动分析视频内容、生成解说词、合成语音并制作带解说的短视频。完全基于云端API，无需昂贵的GPU硬件，成本透明可控。

### ✨ 核心特性

- 🚀 **无GPU依赖** - 完全基于云端API，无需本地GPU硬件
- 💰 **成本透明** - 按需付费，每个5分钟视频处理成本约¥0.06-0.12
- 🤖 **多AI集成** - 集成通义千问、文心一言、百度AI等多个云端服务
- 🎙️ **智能语音** - 支持阿里云TTS、腾讯云TTS、Edge-TTS等多种语音合成
- 📹 **自动化处理** - 一键完成视频分析→解说生成→语音合成→视频制作
- 🌐 **Web界面** - 直观的Streamlit前端 + 强大的FastAPI后端
- 🔧 **高可用性** - 多服务商冗余，自动故障转移
- 📚 **完整文档** - 详细的使用指南和API文档

### 🏗️ 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   FastAPI       │    │   Cloud APIs   │
│   前端界面      │◄──►│   后端服务      │◄──►│   云端服务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 │                                 │
                ┌──────▼──────┐                 ┌────────▼────────┐                ┌──────▼──────┐
                │  解说生成   │                 │    语音合成     │                │  视频分析   │
                │             │                 │                 │                │             │
                │ 通义千问    │                 │   阿里云TTS     │                │   百度AI    │
                │ 文心一言    │                 │   腾讯云TTS     │                │ 通义千问-VL │
                │ OpenAI      │                 │   Edge-TTS      │                │             │
                └─────────────┘                 └─────────────────┘                └─────────────┘
```

## 🚀 快速开始

### 📋 系统要求

- **操作系统**: Windows 10/11, macOS, Linux
- **Python**: 3.8+
- **内存**: 4GB+ (推荐8GB+)
- **网络**: 稳定的互联网连接
- **存储**: 2GB+ 可用空间

### ⚡ 一键部署

#### Windows 11 开发机
```bash
# 下载并运行一键部署脚本
curl -O https://raw.githubusercontent.com/cflank/AIMovie/master/deploy_windows.bat
deploy_windows.bat
```

#### 云端服务器 (Linux)
```bash
# 下载并运行一键部署脚本
curl -O https://raw.githubusercontent.com/cflank/AIMovie/master/deploy_server.sh
chmod +x deploy_server.sh
./deploy_server.sh
```

#### Docker 部署
```bash
# 克隆项目
git clone https://github.com/cflank/AIMovie.git
cd AIMovie

# 配置环境变量
cp env_template.txt .env
# 编辑 .env 文件，添加API密钥

# 构建并运行
docker-compose up -d
```

### 🔧 手动安装

1. **克隆项目**
```bash
git clone https://github.com/cflank/AIMovie.git
cd AIMovie
```

2. **创建虚拟环境**
```bash
python -m venv aimovie_cloud
source aimovie_cloud/bin/activate  # Linux/macOS
# 或
aimovie_cloud\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置API密钥**
```bash
cp env_template.txt .env
# 编辑 .env 文件，至少配置一个LLM服务的API密钥
```

5. **启动服务**
```bash
python start.py
```

6. **访问应用**
- Web界面: http://127.0.0.1:8501
- API文档: http://127.0.0.1:8000/docs

## 🔑 API配置

### 🌟 推荐配置 (高性价比)

```env
# 通义千问 (解说生成主力) - ¥0.0008/1K tokens
QWEN_API_KEY=your_qwen_api_key_here

# 阿里云TTS (语音合成主力) - ¥0.00002/字符
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 百度AI (视频分析主力) - ¥0.002/图片
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

### 📋 API申请链接

- **通义千问**: https://dashscope.aliyuncs.com/
- **阿里云TTS**: https://nls.console.aliyun.com/
- **百度AI**: https://ai.baidu.com/
- **文心一言**: https://cloud.baidu.com/product/wenxinworkshop
- **腾讯云**: https://console.cloud.tencent.com/
- **OpenAI**: https://platform.openai.com/

## 💰 成本估算

### 单个5分钟视频处理成本
- **视频分析** (50帧): ¥0.05-0.10
- **解说生成** (500字): ¥0.0004-0.0006  
- **语音合成** (500字): ¥0.01-0.015
- **总计**: 约 ¥0.06-0.12

### 月处理量成本预估
- **10个视频/月**: ¥0.6-1.2
- **50个视频/月**: ¥3-6
- **100个视频/月**: ¥6-12
- **500个视频/月**: ¥30-60

## 📖 使用指南

### 🎬 完整流程

1. 访问Web界面: http://127.0.0.1:8501
2. 上传视频文件 (支持 mp4, avi, mov, mkv, wmv, flv)
3. 配置参数:
   - 解说风格: 专业严肃/幽默风趣/情感丰富/悬疑紧张
   - 目标观众: 普通大众/年轻观众/专业人士/儿童观众
   - 语音风格: 多种男女声可选
4. 点击"开始完整处理"
5. 等待处理完成 (显示实时进度)
6. 下载生成的解说视频

### 🔍 分步处理

- **视频分析**: 自动提取关键帧，分析视频内容
- **解说生成**: 基于分析结果生成解说词
- **语音合成**: 将文本转换为自然语音
- **视频制作**: 合成最终的解说视频

### 📚 详细文档

- [📖 完整使用指南](CLOUD_USAGE_GUIDE.md)
- [🔧 API文档](http://127.0.0.1:8000/docs) (启动服务后访问)
- [🤝 贡献指南](CONTRIBUTING.md)
- [📋 更新日志](CHANGELOG.md)

## 🛠️ 开发

### 项目结构
```
AIMovie/
├── src/                    # 源代码
│   ├── agents/            # AI Agent模块
│   ├── api/               # FastAPI后端
│   └── config/            # 配置管理
├── frontend/              # Streamlit前端
├── tests/                 # 测试文件
├── docker/                # Docker配置
├── .github/               # GitHub配置
└── docs/                  # 文档
```

### 本地开发

```bash
# 克隆项目
git clone https://github.com/cflank/AIMovie.git
cd AIMovie

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 启动开发服务
python start.py
```

### 贡献代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 🤝 社区

- **GitHub**: https://github.com/cflank/AIMovie
- **Issues**: https://github.com/cflank/AIMovie/issues
- **Discussions**: https://github.com/cflank/AIMovie/discussions
- **Wiki**: https://github.com/cflank/AIMovie/wiki

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢以下开源项目和云服务提供商：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Streamlit](https://streamlit.io/) - 快速构建数据应用
- [阿里云](https://www.aliyun.com/) - 通义千问、语音合成服务
- [百度AI](https://ai.baidu.com/) - 视频分析、文心一言服务
- [腾讯云](https://cloud.tencent.com/) - 语音合成服务
- [OpenAI](https://openai.com/) - GPT系列模型

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=cflank/AIMovie&type=Date)](https://star-history.com/#cflank/AIMovie&Date)

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

[🚀 开始使用](https://github.com/cflank/AIMovie) | [📖 文档](CLOUD_USAGE_GUIDE.md) | [🐛 报告问题](https://github.com/cflank/AIMovie/issues) | [💡 功能建议](https://github.com/cflank/AIMovie/issues/new?template=feature_request.md)

</div>
