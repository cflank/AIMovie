# AIMovie 自动化部署指南

本文档详细介绍了AIMovie项目的各种部署方式，包括Windows 11开发环境、Linux云端服务器和Docker容器化部署。

## 📋 目录

- [Windows 11 开发环境部署](#windows-11-开发环境部署)
- [Linux 云端服务器部署](#linux-云端服务器部署)
- [Docker 容器化部署](#docker-容器化部署)
- [一键启动脚本](#一键启动脚本)
- [配置管理](#配置管理)
- [故障排除](#故障排除)

## 🖥️ Windows 11 开发环境部署

### 自动化部署

运行自动化部署脚本（**推荐**）：

```bash
# 右键"以管理员身份运行"
deploy_win11.bat
```

### 手动部署步骤

1. **安装Python 3.10+**
   ```bash
   # 下载并安装Python 3.10+
   # 确保勾选"Add Python to PATH"
   ```

2. **克隆项目**
   ```bash
   git clone <repository-url>
   cd AIMovie
   ```

3. **创建虚拟环境**
   ```bash
   python -m venv aimovie_env
   aimovie_env\Scripts\activate
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

5. **配置环境变量**
   ```bash
   # 复制并编辑配置文件
   copy .env.example .env
   notepad .env
   ```

### 可用脚本

部署完成后，将生成以下管理脚本：

- `start_dev.bat` - 开发环境启动
- `start_prod.bat` - 生产环境启动
- `service_manager.bat` - Windows服务管理
- `update.bat` - 更新项目
- `check_env.bat` - 环境检查
- `cleanup.bat` - 清理临时文件

## 🌐 Linux 云端服务器部署

### 自动化部署

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/aimovie/main/deploy_server.sh
chmod +x deploy_server.sh

# 运行部署（需要root权限）
sudo ./deploy_server.sh

# 可选：配置域名和SSL
sudo ./deploy_server.sh --domain your-domain.com
```

### 支持的系统

- Ubuntu 18.04+
- CentOS 7+
- Debian 10+
- Fedora 30+

### 部署内容

自动化部署脚本将安装和配置：

- Python 3.10
- Nginx (反向代理)
- Supervisor (进程管理)
- Redis (缓存)
- 防火墙配置
- SSL证书 (可选)

### 管理命令

部署完成后可使用以下命令：

```bash
# 服务管理
aimovie start      # 启动服务
aimovie stop       # 停止服务
aimovie restart    # 重启服务
aimovie status     # 查看状态
aimovie logs       # 查看日志
aimovie update     # 更新项目
aimovie backup     # 备份数据

# 监控
/opt/aimovie/monitor.sh    # 系统监控
```

## 🐳 Docker 容器化部署

### 快速启动

```bash
# 克隆项目
git clone <repository-url>
cd AIMovie

# 使用部署脚本
chmod +x deploy_docker.sh
./deploy_docker.sh deploy

# 或直接使用Docker Compose
docker-compose up -d
```

### 服务架构

Docker部署包含以下服务：

- **aimovie-api** - API服务 (端口8000)
- **aimovie-frontend** - 前端服务 (端口8501)
- **nginx** - 反向代理 (端口80/443)
- **redis** - 缓存服务 (端口6379)
- **postgres** - 数据库 (端口5432)
- **prometheus** - 监控 (端口9090)
- **grafana** - 可视化 (端口3000)
- **flower** - 任务监控 (端口5555)

### Docker管理命令

```bash
# 部署服务
./deploy_docker.sh deploy -e prod

# 服务管理
./deploy_docker.sh start
./deploy_docker.sh stop
./deploy_docker.sh restart
./deploy_docker.sh status

# 查看日志
./deploy_docker.sh logs
./deploy_docker.sh logs aimovie-api

# 更新服务
./deploy_docker.sh update

# 数据备份
./deploy_docker.sh backup
./deploy_docker.sh restore backup_file.tar.gz

# 清理资源
./deploy_docker.sh cleanup
```

## 🚀 一键启动脚本

### Windows 一键启动

双击运行 `一键启动.bat`，提供以下选项：

1. **快速启动** - 开发模式启动
2. **生产模式启动** - 生产环境启动
3. **Docker容器启动** - 容器化启动
4. **Windows服务启动** - 系统服务启动
5. **环境检查** - 检查运行环境
6. **查看日志** - 查看各种日志
7. **配置管理** - 管理配置文件

### Linux 一键启动

```bash
# 开发模式
./start.sh dev

# 生产模式
./start.sh prod

# Docker模式
./start.sh docker
```

## ⚙️ 配置管理

### 环境变量配置

创建 `.env` 文件并配置以下变量：

```env
# 基础配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API密钥
QWEN_VL_API_KEY=your_qwen_api_key
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
MOONSHOT_API_KEY=your_moonshot_api_key

# 阿里云配置
ALIYUN_ACCESS_KEY_ID=your_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret

# 文件配置
MAX_FILE_SIZE=500
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp

# 数据库配置 (Docker部署)
POSTGRES_PASSWORD=aimovie123
DATABASE_URL=postgresql://aimovie:aimovie123@postgres:5432/aimovie

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

### 配置验证

```bash
# Windows
check_env.bat

# Linux
python -c "from src.config.cloud_settings import get_cloud_settings; print('配置验证成功')"
```

## 🔧 故障排除

### 常见问题

#### 1. Python环境问题

**问题**: `python: command not found`

**解决方案**:
```bash
# Windows: 重新安装Python并勾选"Add to PATH"
# Linux: 安装Python
sudo apt-get install python3.10 python3.10-venv  # Ubuntu
sudo yum install python3.10                       # CentOS
```

#### 2. 依赖安装失败

**问题**: `pip install` 失败

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装核心依赖
pip install fastapi uvicorn streamlit requests opencv-python
```

#### 3. 端口占用

**问题**: `Address already in use`

**解决方案**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux
sudo lsof -i :8000
sudo kill -9 <PID>
```

#### 4. Docker问题

**问题**: Docker容器启动失败

**解决方案**:
```bash
# 查看日志
docker-compose logs aimovie-api

# 重新构建
docker-compose build --no-cache

# 清理并重启
docker-compose down -v
docker-compose up -d
```

#### 5. 权限问题

**问题**: Linux权限不足

**解决方案**:
```bash
# 修改文件权限
sudo chown -R $USER:$USER /opt/aimovie
chmod +x deploy_server.sh

# 添加用户到docker组
sudo usermod -aG docker $USER
```

### 日志查看

#### Windows
```bash
# 查看应用日志
type logs\api.log
type logs\frontend.log

# 查看系统日志
eventvwr.msc
```

#### Linux
```bash
# 应用日志
tail -f /opt/aimovie/logs/api.log
tail -f /opt/aimovie/logs/frontend.log

# 系统日志
sudo journalctl -u aimovie-api -f
sudo journalctl -u nginx -f
```

#### Docker
```bash
# 容器日志
docker-compose logs -f aimovie-api
docker-compose logs -f aimovie-frontend

# 系统资源
docker stats
```

### 性能优化

#### 1. 系统资源

```bash
# 监控资源使用
htop                    # Linux
taskmgr                 # Windows
docker stats            # Docker
```

#### 2. 数据库优化

```sql
-- PostgreSQL优化
VACUUM ANALYZE;
REINDEX DATABASE aimovie;
```

#### 3. 缓存配置

```bash
# Redis内存优化
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## 📞 技术支持

如果遇到部署问题，请：

1. 查看相关日志文件
2. 检查系统资源使用情况
3. 验证网络连接和防火墙设置
4. 确认API密钥配置正确
5. 提交Issue并附上详细的错误信息

## 🔄 更新升级

### 自动更新

```bash
# Windows
update.bat

# Linux
aimovie update

# Docker
./deploy_docker.sh update
```

### 手动更新

```bash
# 1. 备份数据
cp -r uploads uploads_backup
cp .env .env_backup

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
pip install -r requirements.txt --upgrade

# 4. 重启服务
# 根据部署方式选择相应的重启命令
```

---

**注意**: 请根据实际部署环境选择合适的部署方式，并确保所有API密钥配置正确。 