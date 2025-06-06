# 🚀 AIMovie Cloud 快速部署指南

## 📋 部署选项

### 1. Windows 11 开发机 (推荐新手)

**一键部署脚本**:
```bash
# 下载并运行部署脚本
curl -O https://raw.githubusercontent.com/cflank/AIMovie/master/deploy_windows.bat
deploy_windows.bat
```

**手动部署**:
```bash
# 1. 克隆项目
git clone https://github.com/cflank/AIMovie.git
cd AIMovie

# 2. 创建虚拟环境
python -m venv aimovie_env
aimovie_env\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API密钥
copy env_template.txt .env
# 编辑 .env 文件

# 5. 启动服务
python start.py
```

### 2. 云端服务器 (Linux)

**一键部署脚本**:
```bash
# 下载并运行部署脚本
curl -O https://raw.githubusercontent.com/cflank/AIMovie/master/deploy_server.sh
chmod +x deploy_server.sh
./deploy_server.sh
```

**手动部署**:
```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl ffmpeg

# 2. 克隆项目
git clone https://github.com/cflank/AIMovie.git
cd AIMovie

# 3. 创建虚拟环境
python3 -m venv aimovie_env
source aimovie_env/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置API密钥
cp env_template.txt .env
# 编辑 .env 文件

# 6. 启动服务
python start.py
```

### 3. Docker 部署 (推荐生产环境)

```bash
# 1. 克隆项目
git clone https://github.com/cflank/AIMovie.git
cd AIMovie

# 2. 配置环境变量
cp env_template.txt .env
# 编辑 .env 文件，添加API密钥

# 3. 构建并启动
docker-compose up -d

# 4. 查看状态
docker-compose ps
docker-compose logs -f
```

## 🔑 必需配置

### 最小配置 (至少配置一个)
```env
# 通义千问 (推荐，性价比最高)
QWEN_API_KEY=your_qwen_api_key

# 或者文心一言
ERNIE_API_KEY=your_ernie_api_key
ERNIE_SECRET_KEY=your_ernie_secret_key

# 或者OpenAI
OPENAI_API_KEY=your_openai_api_key
```

### 推荐配置 (高性价比)
```env
# LLM服务 (解说生成)
QWEN_API_KEY=your_qwen_api_key

# TTS服务 (语音合成)
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 视频分析服务
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
```

## 🌐 访问地址

部署完成后，您可以通过以下地址访问：

- **Web界面**: http://127.0.0.1:8501 (本地) 或 http://your-server-ip:8501 (服务器)
- **API文档**: http://127.0.0.1:8000/docs (本地) 或 http://your-server-ip:8000/docs (服务器)

## 🔧 服务管理

### Windows
```bash
# 启动 (双击桌面快捷方式或运行)
启动AIMovie.bat

# 停止 (Ctrl+C 或关闭窗口)
```

### Linux (systemd服务)
```bash
# 启动服务
sudo systemctl start aimovie

# 停止服务
sudo systemctl stop aimovie

# 重启服务
sudo systemctl restart aimovie

# 查看状态
sudo systemctl status aimovie

# 查看日志
sudo journalctl -u aimovie -f
```

### Docker
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看状态
docker-compose ps
```

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # Windows
   netstat -an | findstr ":8000"
   netstat -an | findstr ":8501"
   
   # Linux
   netstat -tuln | grep :8000
   netstat -tuln | grep :8501
   ```

2. **API密钥配置错误**
   - 检查 `.env` 文件是否存在
   - 确认API密钥格式正确
   - 验证API密钥是否有效

3. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 清理缓存重新安装
   pip cache purge
   pip install -r requirements.txt
   ```

4. **服务启动失败**
   ```bash
   # 查看详细错误日志
   python start.py
   
   # 或查看日志文件
   tail -f logs/aimovie_cloud.log
   ```

### 获取帮助

- **GitHub Issues**: https://github.com/cflank/AIMovie/issues
- **详细文档**: [CLOUD_USAGE_GUIDE.md](CLOUD_USAGE_GUIDE.md)
- **API文档**: http://127.0.0.1:8000/docs (启动后访问)

## 💰 成本估算

### 单个5分钟视频处理成本
- **视频分析**: ¥0.05-0.10
- **解说生成**: ¥0.0004-0.0006
- **语音合成**: ¥0.01-0.015
- **总计**: 约 ¥0.06-0.12

### 推荐服务商和价格
- **通义千问**: ¥0.0008/1K tokens - [申请地址](https://dashscope.aliyuncs.com/)
- **阿里云TTS**: ¥0.00002/字符 - [申请地址](https://nls.console.aliyun.com/)
- **百度AI**: ¥0.002/图片 - [申请地址](https://ai.baidu.com/)

## 🎯 下一步

1. **配置API密钥**: 编辑 `.env` 文件
2. **测试功能**: 上传一个短视频测试
3. **查看文档**: 阅读 [完整使用指南](CLOUD_USAGE_GUIDE.md)
4. **加入社区**: 关注 [GitHub项目](https://github.com/cflank/AIMovie)

---

🎉 **部署完成！开始创建您的AI解说视频吧！** 🚀 