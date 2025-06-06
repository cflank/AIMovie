# 📦 依赖安装指南

## 🎯 依赖文件说明

AIMovie Cloud 提供了多种依赖安装选项，您可以根据需求选择合适的方案：

### 📋 可用的依赖文件

| 文件名 | 说明 | 适用场景 | 安装大小 |
|--------|------|----------|----------|
| `requirements_cloud_minimal.txt` | 最小化依赖 | 快速体验，按需安装 | ~50MB |
| `requirements_cloud.txt` | 完整云端依赖 | 一次性安装所有服务 | ~200MB |
| `requirements.txt` | 标准依赖 | 兼容原版本 | ~150MB |

## 🚀 推荐安装方式

### 方式一：最小化安装 (推荐)

**适合**: 新用户、快速体验、网络较慢的环境

```bash
# 1. 安装核心依赖
pip install -r requirements_cloud_minimal.txt

# 2. 根据选择的大模型组合，按需安装SDK
# 例如：最高性价比组合
pip install dashscope baidu-aip

# 3. 启动应用
python start_cloud.py
```

### 方式二：完整安装

**适合**: 想要使用多种服务、网络较好的环境

```bash
# 一次性安装所有依赖
pip install -r requirements_cloud.txt

# 启动应用
python start_cloud.py
```

### 方式三：自动选择

**适合**: 使用部署脚本的用户

部署脚本会自动按以下优先级选择依赖文件：
1. `requirements_cloud_minimal.txt` (优先)
2. `requirements_cloud.txt` (备选)
3. `requirements.txt` (兼容)

## 🔧 按需安装SDK

### 🏆 最高性价比组合

```bash
# 核心依赖
pip install -r requirements_cloud_minimal.txt

# 通义千问 (解说生成)
pip install dashscope

# 阿里云TTS (语音合成) - 可选，有免费的Edge-TTS
pip install alibabacloud-nls20190301

# 百度AI (视频分析)
pip install baidu-aip
```

### 💎 质量最高组合

```bash
# 核心依赖
pip install -r requirements_cloud_minimal.txt

# OpenAI GPT-4 (解说生成)
pip install openai

# Azure TTS (语音合成)
pip install azure-cognitiveservices-speech

# OpenAI Vision (视频分析)
# 使用同一个openai包
```

### 💰 最经济组合

```bash
# 核心依赖 (已包含Edge-TTS)
pip install -r requirements_cloud_minimal.txt

# 文心一言 (解说生成)
pip install requests  # 使用HTTP API

# 百度AI (视频分析)
pip install baidu-aip

# Edge-TTS (免费语音合成) - 已包含在核心依赖中
```

## 🛠️ 开发环境安装

### 完整开发环境

```bash
# 安装完整依赖
pip install -r requirements_cloud.txt

# 安装开发工具
pip install pytest black flake8 pytest-asyncio

# 运行测试
python -m pytest tests/
```

### 最小开发环境

```bash
# 最小依赖
pip install -r requirements_cloud_minimal.txt

# 基础开发工具
pip install pytest black

# 按需安装要测试的服务SDK
```

## 🐳 Docker 安装

### 使用预构建镜像

```bash
# 拉取镜像
docker pull aimovie/cloud:latest

# 运行容器
docker run -d \
  --name aimovie-cloud \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/.env:/app/.env \
  aimovie/cloud:latest
```

### 本地构建

```bash
# 构建镜像
docker build -t aimovie-cloud .

# 运行容器
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

#### 1. 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像源
pip install -r requirements_cloud_minimal.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 2. 特定SDK安装失败

```bash
# 单独安装失败的包
pip install --upgrade setuptools wheel
pip install 包名 --no-cache-dir

# 或使用conda
conda install 包名
```

#### 3. 版本冲突

```bash
# 创建新的虚拟环境
python -m venv fresh_env
source fresh_env/bin/activate  # Linux/Mac
# 或
fresh_env\Scripts\activate  # Windows

# 重新安装
pip install -r requirements_cloud_minimal.txt
```

#### 4. 网络问题

```bash
# 使用代理
pip install -r requirements_cloud_minimal.txt --proxy http://proxy.example.com:8080

# 使用国内镜像
pip install -r requirements_cloud_minimal.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 验证安装

```bash
# 检查核心包
python -c "import fastapi, streamlit, requests; print('核心包安装成功')"

# 检查特定SDK
python -c "import dashscope; print('通义千问SDK安装成功')"
python -c "import baidu_aip; print('百度AI SDK安装成功')"
python -c "import openai; print('OpenAI SDK安装成功')"
```

## 📊 安装大小对比

| 安装方式 | 下载大小 | 安装大小 | 安装时间 |
|----------|----------|----------|----------|
| 最小化 | ~20MB | ~50MB | 1-2分钟 |
| 最小化+性价比SDK | ~40MB | ~100MB | 2-3分钟 |
| 完整安装 | ~80MB | ~200MB | 5-10分钟 |

## 💡 最佳实践

### 1. 生产环境

```bash
# 使用固定版本
pip install -r requirements_cloud.txt --no-deps

# 生成锁定文件
pip freeze > requirements.lock

# 使用锁定文件部署
pip install -r requirements.lock
```

### 2. 开发环境

```bash
# 使用虚拟环境
python -m venv aimovie_dev
source aimovie_dev/bin/activate

# 安装开发依赖
pip install -r requirements_cloud.txt
pip install -e .  # 可编辑安装
```

### 3. CI/CD 环境

```bash
# 缓存依赖
pip install --cache-dir .pip-cache -r requirements_cloud_minimal.txt

# 并行安装
pip install -r requirements_cloud_minimal.txt --use-feature=fast-deps
```

## 🔗 相关链接

- [支持的大模型服务](SUPPORTED_MODELS.md)
- [快速部署指南](QUICK_DEPLOY.md)
- [完整使用指南](CLOUD_USAGE_GUIDE.md)
- [故障排除](TROUBLESHOOTING.md)

---

**💡 提示**: 建议先使用最小化安装快速体验，然后根据实际使用的服务按需安装对应的SDK。 