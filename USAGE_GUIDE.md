# 🎬 AIMovie 使用指南

## 📋 项目简介

AIMovie 是一个智能视频解说生成器，能够自动分析视频内容，生成解说词，并合成语音，最终输出带解说的短视频。

### 🌟 主要特性

- **🤖 智能分析**: 基于云端AI服务的视频内容分析
- **📝 自动解说**: 使用大语言模型生成专业解说词
- **🎵 语音合成**: 多种语音风格的TTS合成
- **🎞️ 视频编辑**: 自动剪辑和字幕添加
- **☁️ 云端服务**: 完全基于云端API，无需本地硬件

### 🏗️ 技术架构

- **前端**: Streamlit Web界面
- **后端**: FastAPI服务
- **AI服务**: 通义千问、百度AI、阿里云TTS等云端服务
- **视频处理**: MoviePy、OpenCV

## 🚀 快速开始

### 1. 环境准备

#### 1.1 基础环境

```bash
# Python 3.8+
python --version

# 克隆项目
git clone <repository-url>
cd AIMovie

# 创建虚拟环境
python -m venv aimovie_env
source aimovie_env/bin/activate  # Linux/macOS
# 或
aimovie_env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 1.2 API配置

配置云端服务API密钥：

```bash
# 复制配置模板
cp env_template.txt .env

# 编辑配置文件，添加API密钥
```

### 2. 一键启动

```bash
python start.py
```

启动后访问：
- **Web界面**: http://127.0.0.1:8501
- **API文档**: http://127.0.0.1:8000/docs

### 3. 开始使用

1. 打开Web界面
2. 上传视频文件
3. 选择解说风格和语音
4. 点击「🎯 开始智能分析」
5. 等待处理完成
6. 下载生成的解说视频

## 📖 详细使用

### 🎬 完整流程

#### 1. 视频上传
- 支持格式: MP4, AVI, MOV, MKV, WMV, FLV
- 文件大小: 最大500MB
- 时长建议: 1-30分钟

#### 2. 参数配置
- **解说风格**: 专业严肃、幽默风趣、情感丰富、悬疑紧张
- **目标观众**: 普通大众、年轻观众、专业人士、儿童观众
- **解说长度**: 简短、中等、详细
- **语音选择**: 多种男女声可选
- **语音参数**: 语速、音调、音量

#### 3. 处理过程
1. **视频分析**: 提取关键帧，识别场景和对象
2. **内容理解**: 分析视频主题和情节
3. **解说生成**: 基于分析结果生成解说词
4. **语音合成**: 将解说词转换为语音
5. **视频合成**: 合并原视频和解说音频

#### 4. 结果输出
- 带解说的完整视频
- 解说文本文件
- 语音音频文件

### 🔧 高级功能

#### API调用

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

#### 批量处理

```python
# 批量上传多个视频
video_files = ["video1.mp4", "video2.mp4", "video3.mp4"]
for video_file in video_files:
    # 处理每个视频
    process_video(video_file)
```

### 云端服务配置

#### 必需配置 (至少配置一个)
- `QWEN_API_KEY`: 通义千问API密钥 (推荐)
- `ERNIE_API_KEY` + `ERNIE_SECRET_KEY`: 文心一言
- `OPENAI_API_KEY`: OpenAI GPT

#### 推荐配置
- `ALIYUN_ACCESS_KEY_ID` + `ALIYUN_ACCESS_KEY_SECRET`: 阿里云TTS
- `BAIDU_API_KEY` + `BAIDU_SECRET_KEY`: 百度AI视觉

#### 备用配置
- `TENCENT_SECRET_ID` + `TENCENT_SECRET_KEY`: 腾讯云TTS
- `OPENAI_API_KEY`: 高质量备用服务

## 🔧 故障排除

### 常见问题

#### 1. API服务启动失败

**症状**: 运行启动脚本后服务无法访问

**解决方案**:
```bash
# 检查端口占用
netstat -an | grep 8000

# 手动启动服务
python -m src.api.cloud_main

# 查看日志
tail -f logs/aimovie.log
```

#### 2. API密钥配置错误

**症状**: 提示"未配置API密钥"

**解决方案**:
1. 确认 `.env` 文件存在
2. 检查API密钥格式
3. 验证API密钥有效性

#### 3. 视频上传失败

**症状**: 上传时提示文件过大或格式不支持

**解决方案**:
1. 检查文件大小 (限制500MB)
2. 确认文件格式支持
3. 尝试压缩视频文件

#### 4. 处理速度慢

**症状**: 视频处理时间过长

**解决方案**:
1. 检查网络连接
2. 减少视频分辨率
3. 缩短视频时长
4. 选择更快的云端服务

### 性能优化

#### 1. 网络优化
- 使用稳定的网络连接
- 配置多个API密钥轮询使用
- 选择就近的服务区域

#### 2. 成本控制
- 合理设置视频采样频率
- 使用免费额度较大的服务
- 监控API使用量

#### 3. 质量提升
- 选择高质量的语音模型
- 调整解说生成参数
- 使用专业的解说风格

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

## 💰 成本说明

### 云端服务费用

- **视频分析**: 约 ¥0.05-0.10/视频
- **解说生成**: 约 ¥0.0004-0.0006/500字
- **语音合成**: 约 ¥0.01-0.015/500字
- **总计**: 约 ¥0.06-0.12/5分钟视频

### 省钱技巧

- 使用免费额度
- 选择性价比高的服务
- 合理控制处理频率
- 批量处理降低成本

## 🔄 更新升级

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install --upgrade -r requirements_cloud.txt

# 重启服务
python cloud_start.py
```

## 📞 技术支持

- **文档**: 查看 `CLOUD_USAGE_GUIDE.md`
- **日志**: 检查 `logs/aimovie.log`
- **API**: 访问 http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health

---

🎉 **开始创建您的AI解说视频吧！** 🚀 