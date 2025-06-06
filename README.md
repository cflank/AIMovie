# 🎬 AIMovie Cloud

> 智能视频解说生成器 - 云端版本

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AIMovie Cloud 是一个基于云端AI服务的智能视频解说生成器，能够自动分析视频内容，生成专业解说词，并合成语音，最终输出带解说的短视频。

## ✨ 主要特性

- 🤖 **智能分析**: 基于云端AI服务的视频内容分析
- 📝 **自动解说**: 使用大语言模型生成专业解说词
- 🎵 **语音合成**: 多种语音风格的TTS合成
- 🎞️ **视频编辑**: 自动剪辑和字幕添加
- ☁️ **云端服务**: 完全基于云端API，无需本地硬件
- 💰 **成本透明**: 按需付费，成本可控可预测

## 🏗️ 技术架构

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

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/aimovie/aimovie-cloud.git
cd aimovie-cloud

# 创建虚拟环境
python -m venv aimovie_cloud
source aimovie_cloud/bin/activate  # Linux/macOS
# 或
aimovie_cloud\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制配置模板
cp env_template.txt .env

# 编辑配置文件，添加API密钥
# 至少配置一个LLM服务的API密钥
```

### 3. 一键启动

```bash
python start.py
```

### 4. 访问服务

- **Web界面**: http://127.0.0.1:8501
- **API文档**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health

## 🔑 API配置

### 🌟 推荐配置 (高性价比)

#### 通义千问 (解说生成主力)
```env
QWEN_API_KEY=your_qwen_api_key_here
```
- **价格**: ¥0.0008/1K tokens
- **申请**: https://dashscope.aliyuncs.com/

#### 阿里云TTS (语音合成主力)
```env
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
```
- **价格**: ¥0.00002/字符
- **申请**: https://nls.console.aliyun.com/

#### 百度AI (视频分析主力)
```env
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```
- **价格**: ¥0.002/图片
- **申请**: https://ai.baidu.com/

### 🔄 备用配置

- **文心一言**: `ERNIE_API_KEY` + `ERNIE_SECRET_KEY`
- **腾讯云TTS**: `TENCENT_SECRET_ID` + `TENCENT_SECRET_KEY`
- **OpenAI**: `OPENAI_API_KEY` (高质量备用)

## 💰 成本说明

### 单个5分钟视频处理成本
- **视频分析** (50帧): ¥0.05-0.10
- **解说生成** (500字): ¥0.0004-0.0006
- **语音合成** (500字): ¥0.01-0.015
- **总计**: 约 ¥0.06-0.12

### 月处理量成本预估
- **10个视频/月**: ¥0.6-1.2
- **50个视频/月**: ¥3-6
- **100个视频/月**: ¥6-12

## 📖 使用流程

1. **上传视频**: 支持 MP4, AVI, MOV, MKV, WMV, FLV
2. **选择风格**: 专业严肃/幽默风趣/情感丰富/悬疑紧张
3. **配置参数**: 目标观众、解说长度、语音风格
4. **开始处理**: 一键生成带解说的视频
5. **下载结果**: 获取完整的解说视频

## 🔧 API调用示例

```python
import requests

# 上传视频
files = {"file": open("video.mp4", "rb")}
response = requests.post("http://127.0.0.1:8000/upload/video", files=files)

# 分析视频
data = {"video_path": "/path/to/video.mp4"}
response = requests.post("http://127.0.0.1:8000/analyze/video", json=data)

# 生成解说
data = {
    "video_analysis": analysis_result,
    "style": "professional",
    "target_audience": "general",
    "narration_length": "medium"
}
response = requests.post("http://127.0.0.1:8000/narration/generate", json=data)
```

## 📁 项目结构

```
AIMovie/
├── src/
│   ├── agents/           # 云端AI代理
│   ├── api/             # API服务
│   ├── config/          # 配置管理
│   └── utils/           # 工具函数
├── frontend/            # Streamlit前端
├── data/               # 数据目录
├── logs/               # 日志文件
├── requirements.txt     # 项目依赖
├── env_template.txt     # 环境配置模板
├── start.py            # 启动脚本
└── CLOUD_USAGE_GUIDE.md # 详细使用指南
```

## 🛠️ 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
flake8 src/
```

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- **文档**: [CLOUD_USAGE_GUIDE.md](CLOUD_USAGE_GUIDE.md)
- **问题反馈**: [GitHub Issues](https://github.com/aimovie/aimovie-cloud/issues)
- **讨论**: [GitHub Discussions](https://github.com/aimovie/aimovie-cloud/discussions)

## 🌟 致谢

感谢以下云端服务提供商：
- [阿里云](https://www.aliyun.com/) - 通义千问、语音合成
- [百度AI](https://ai.baidu.com/) - 视觉AI服务
- [腾讯云](https://cloud.tencent.com/) - 语音合成
- [OpenAI](https://openai.com/) - GPT模型

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
