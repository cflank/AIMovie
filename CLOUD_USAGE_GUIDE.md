# 🌐 AIMovie Cloud 使用指南

## 📋 目录
- [项目简介](#项目简介)
- [云端优势](#云端优势)
- [快速开始](#快速开始)
- [API配置](#api配置)
- [成本控制](#成本控制)
- [详细使用](#详细使用)
- [API文档](#api文档)
- [故障排除](#故障排除)
- [性能优化](#性能优化)

## 🎬 项目简介

AIMovie Cloud 是 AIMovie 的云端版本，完全基于云端API服务，无需GPU硬件，通过高性价比的云端AI服务组合实现视频解说生成。

### 🌟 主要特性
- **🚀 无GPU依赖**: 完全基于云端API，无需本地GPU
- **💰 成本透明**: 按需付费，成本可控可预测
- **🔧 高性价比**: 精选最优性价比的云端服务组合
- **⚡ 快速部署**: 配置API密钥即可使用
- **🌐 多服务支持**: 支持多个云端服务商，自动故障转移

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

## 🌟 云端优势

### 💰 成本优势
- **按需付费**: 只为实际使用的服务付费
- **无硬件成本**: 无需购买昂贵的GPU设备
- **透明定价**: 每个API调用成本清晰可见
- **成本预测**: 可提前估算处理成本

### 🚀 性能优势
- **无硬件限制**: 不受本地硬件性能限制
- **高可用性**: 云端服务高可用，稳定可靠
- **弹性扩展**: 可根据需求调整处理能力
- **快速部署**: 几分钟内即可开始使用

### 🔧 维护优势
- **免维护**: 无需维护本地AI模型和环境
- **自动更新**: 云端服务自动更新到最新版本
- **多重备份**: 多个服务商提供冗余保障
- **技术支持**: 享受云端服务商的技术支持

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd AIMovie

# 创建虚拟环境 (推荐)
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

# 编辑配置文件
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

#### 1. 通义千问 (解说生成主力)
```env
QWEN_API_KEY=your_qwen_api_key_here
```
- **价格**: ¥0.0008/1K tokens
- **申请**: https://dashscope.aliyuncs.com/
- **优势**: 性价比最高，中文效果好

#### 2. 阿里云TTS (语音合成主力)
```env
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_TTS_REGION=cn-shanghai
```
- **价格**: ¥0.00002/字符
- **申请**: https://nls.console.aliyun.com/
- **优势**: 音质好，价格便宜

#### 3. 百度AI (视频分析主力)
```env
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```
- **价格**: ¥0.002/图片
- **申请**: https://ai.baidu.com/
- **优势**: 识别准确，免费额度大

### 🔄 备用配置

#### 文心一言 (解说生成备用)
```env
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key
```

#### 腾讯云TTS (语音合成备用)
```env
TENCENT_SECRET_ID=your_secret_id
TENCENT_SECRET_KEY=your_secret_key
TENCENT_TTS_REGION=ap-beijing
```

#### OpenAI (高端备用)
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 📋 配置检查清单

**✅ 必需配置** (至少配置一个):
- [ ] `QWEN_API_KEY` (推荐，性价比最高)
- [ ] `ERNIE_API_KEY` + `ERNIE_SECRET_KEY`
- [ ] `OPENAI_API_KEY`

**🌟 推荐配置**:
- [ ] `ALIYUN_ACCESS_KEY_ID` + `ALIYUN_ACCESS_KEY_SECRET` (语音合成)
- [ ] `BAIDU_API_KEY` + `BAIDU_SECRET_KEY` (视频分析)
- [ ] `QWEN_VL_API_KEY` (图像理解)

**🔄 备用配置**:
- [ ] `TENCENT_SECRET_ID` + `TENCENT_SECRET_KEY` (备用TTS)
- [ ] `OPENAI_API_KEY` (高质量备用)

## 💰 成本控制

### 📊 成本估算

#### 单个5分钟视频处理成本:
- **视频分析** (50帧): ¥0.05-0.10
- **解说生成** (500字): ¥0.0004-0.0006
- **语音合成** (500字): ¥0.01-0.015
- **总计**: 约 ¥0.06-0.12

#### 月处理量成本预估:
- **10个视频/月**: ¥0.6-1.2
- **50个视频/月**: ¥3-6
- **100个视频/月**: ¥6-12
- **500个视频/月**: ¥30-60

### 💡 省钱技巧

#### 1. 优化采样频率
```env
FRAME_SAMPLE_INTERVAL=5  # 每5秒采样一帧 (默认3秒)
MAX_FRAMES_PER_VIDEO=30  # 最多分析30帧 (默认50帧)
```

#### 2. 使用免费服务
- 优先使用 Edge-TTS (免费语音合成)
- 利用各平台的免费额度

#### 3. 批量处理
- 批量上传多个视频
- 利用批量API降低单次成本

#### 4. 智能降级
- 系统自动选择最便宜的可用服务
- 失败时自动切换到备用服务

### 📈 成本监控

访问 `/cost/estimate` API 端点可实时估算成本:
```bash
curl "http://127.0.0.1:8000/cost/estimate?text_length=500&audio_length=500&frame_count=50"
```

## 📖 详细使用

### 🎬 完整流程

1. **访问Web界面**: http://127.0.0.1:8501
2. **选择"完整流程"选项卡**
3. **上传视频文件** (支持 mp4, avi, mov, mkv, wmv, flv)
4. **配置参数**:
   - 解说风格: 专业严肃/幽默风趣/情感丰富/悬疑紧张
   - 目标观众: 普通大众/年轻观众/专业人士/儿童观众
   - 解说长度: 简短/中等/详细
   - 语音风格: 多种男女声可选
   - 语音参数: 语速/音调/音量
5. **点击"开始完整处理"**
6. **等待处理完成** (显示实时进度)
7. **下载生成的解说视频**

### 🔍 分步处理

#### 1. 视频分析
- 上传视频文件
- 系统自动提取关键帧
- 使用云端AI分析视频内容
- 生成场景描述和关键时刻

#### 2. 解说生成
- 基于视频分析结果
- 使用大语言模型生成解说词
- 支持多种风格和观众定位
- 自动分段和时间戳

#### 3. 语音合成
- 将解说文本转换为语音
- 支持多种语音风格
- 可调节语速、音调、音量
- 批量处理多个段落

#### 4. 视频制作
- 将语音与原视频合成
- 可添加背景音乐
- 生成最终的解说视频

### 🎛️ 高级功能

#### API直接调用
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
# 批量语音合成
data = {
    "segments": narration_segments,
    "voice_style": "female_gentle",
    "speed": 1.0,
    "pitch": 1.0,
    "volume": 1.0
}
response = requests.post("http://127.0.0.1:8000/tts/batch", json=data)
```

## 📚 API文档

### 🌐 在线文档
访问 http://127.0.0.1:8000/docs 查看完整的API文档

### 🔧 主要端点

#### 系统信息
- `GET /` - 根路径信息
- `GET /health` - 健康检查
- `GET /services` - 可用服务列表
- `GET /cost/estimate` - 成本估算

#### 文件管理
- `POST /upload/video` - 上传视频
- `GET /files/list` - 文件列表
- `GET /files/download/{type}/{filename}` - 下载文件
- `DELETE /files/cleanup` - 清理临时文件

#### 视频分析
- `POST /analyze/video` - 分析视频
- `GET /analyze/video/summary` - 获取视频摘要

#### 解说生成
- `POST /narration/generate` - 生成解说

#### 语音合成
- `GET /tts/voices` - 可用语音列表
- `POST /tts/synthesize` - 单段语音合成
- `POST /tts/batch` - 批量语音合成
- `POST /tts/test` - 测试语音效果

#### 视频生成
- `POST /video/generate` - 生成带解说的视频

#### 任务管理
- `GET /task/{task_id}` - 获取任务状态
- `GET /tasks` - 列出所有任务
- `DELETE /task/{task_id}` - 删除任务记录

#### 完整流程
- `POST /process/complete` - 一键完整处理

## 🔧 故障排除

### 常见问题

#### 1. API服务启动失败
**问题**: 运行 `python start.py` 后API服务无法启动

**解决方案**:
```bash
# 检查端口是否被占用
netstat -an | grep 8000

# 手动启动API服务
python -m src.api.cloud_main

# 检查错误日志
tail -f logs/aimovie_cloud.log
```

#### 2. API密钥配置错误
**问题**: 提示"未配置任何LLM服务API密钥"

**解决方案**:
1. 确认 `.env` 文件存在
2. 检查API密钥格式是否正确
3. 验证API密钥是否有效:
```bash
# 测试通义千问API
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

#### 3. 视频上传失败
**问题**: 上传视频时提示文件过大或格式不支持

**解决方案**:
1. 检查文件大小 (默认限制500MB)
2. 确认文件格式 (支持 mp4, avi, mov, mkv, wmv, flv)
3. 调整配置:
```env
MAX_FILE_SIZE=1000  # 增加到1GB
```

#### 4. 语音合成失败
**问题**: TTS服务调用失败

**解决方案**:
1. 检查TTS服务配置
2. 验证API密钥权限
3. 使用Edge-TTS作为备用:
```env
# Edge-TTS无需配置，自动可用
```

#### 5. 成本过高
**问题**: API调用成本超出预期

**解决方案**:
1. 调整采样参数:
```env
FRAME_SAMPLE_INTERVAL=5  # 减少帧采样
MAX_FRAMES_PER_VIDEO=30  # 限制最大帧数
```
2. 使用免费服务
3. 监控API使用量

### 🔍 调试模式

启用调试模式获取更多信息:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

查看详细日志:
```bash
tail -f logs/aimovie_cloud.log
```

### 📞 获取帮助

1. **查看日志**: `logs/aimovie_cloud.log`
2. **API健康检查**: http://127.0.0.1:8000/health
3. **配置验证**: 启动时会自动验证配置
4. **在线文档**: http://127.0.0.1:8000/docs

## ⚡ 性能优化

### 🚀 系统优化

#### 1. 硬件建议
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: SSD硬盘
- **网络**: 稳定的宽带连接

#### 2. 系统配置
```env
# API调用优化
API_RETRY_TIMES=3        # API重试次数
API_TIMEOUT=60           # API超时时间
API_RATE_LIMIT=10        # 每秒最大请求数

# 文件处理优化
TEMP_FILE_RETENTION=24   # 临时文件保留时间(小时)
OUTPUT_QUALITY=medium    # 输出质量 (low/medium/high)
```

#### 3. 并发处理
```python
# 使用异步处理提高效率
import asyncio

async def process_multiple_videos(video_paths):
    tasks = []
    for path in video_paths:
        task = process_video(path)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### 🌐 网络优化

#### 1. API调用优化
- 使用连接池减少连接开销
- 实现智能重试机制
- 监控API响应时间

#### 2. 缓存策略
- 缓存视频分析结果
- 复用相似的解说模板
- 本地缓存常用语音

#### 3. 负载均衡
- 多个API密钥轮询使用
- 根据响应时间选择最快服务
- 实现故障自动切换

### 📊 监控和分析

#### 1. 性能监控
```python
# 监控API调用时间
import time

start_time = time.time()
result = await api_call()
duration = time.time() - start_time
print(f"API调用耗时: {duration:.2f}秒")
```

#### 2. 成本分析
```python
# 分析成本分布
cost_breakdown = {
    "video_analysis": 0.05,
    "narration_generation": 0.0004,
    "speech_synthesis": 0.01,
    "total": 0.0604
}
```

#### 3. 质量评估
- 监控解说质量评分
- 统计用户满意度
- 分析失败率和原因

---

## 🎉 开始使用

现在您已经了解了 AIMovie Cloud 的完整使用方法，可以开始创建您的AI解说视频了！

```bash
# 一键启动
python start.py

# 访问Web界面
# http://127.0.0.1:8501
```

如有任何问题，请查看故障排除部分或检查系统日志。祝您使用愉快！ 🚀 