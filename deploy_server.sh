#!/bin/bash

# AIMovie 云端服务器自动化部署脚本
# 支持 Ubuntu/CentOS/Debian 系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="AIMovie"
PROJECT_DIR="/opt/aimovie"
VENV_NAME="aimovie_env"
SERVICE_USER="aimovie"
PYTHON_VERSION="3.10"
DOMAIN=""  # 可选：域名配置

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# 检查系统类型
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    log_info "检测到系统: $OS $VER"
}

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
    log_success "Root权限检查通过"
}

# 更新系统包
update_system() {
    log_header "🔄 更新系统包..."
    
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        apt-get update -y
        apt-get upgrade -y
        apt-get install -y curl wget git build-essential software-properties-common
        apt-get install -y python3 python3-pip python3-venv python3-dev
        apt-get install -y nginx supervisor redis-server
        apt-get install -y ffmpeg libsm6 libxext6 libfontconfig1 libxrender1
    elif command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        yum update -y
        yum groupinstall -y "Development Tools"
        yum install -y curl wget git python3 python3-pip python3-devel
        yum install -y nginx supervisor redis
        yum install -y ffmpeg
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora
        dnf update -y
        dnf groupinstall -y "Development Tools"
        dnf install -y curl wget git python3 python3-pip python3-devel
        dnf install -y nginx supervisor redis
        dnf install -y ffmpeg
    else
        log_error "不支持的包管理器"
        exit 1
    fi
    
    log_success "系统包更新完成"
}

# 安装Python 3.10
install_python() {
    log_header "🐍 安装Python 3.10..."
    
    # 检查Python版本
    if command -v python3.10 >/dev/null 2>&1; then
        log_success "Python 3.10 已安装"
        return
    fi
    
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        add-apt-repository ppa:deadsnakes/ppa -y
        apt-get update -y
        apt-get install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
        
        # 创建软链接
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    else
        # 编译安装Python 3.10
        cd /tmp
        wget https://www.python.org/ftp/python/3.10.11/Python-3.10.11.tgz
        tar xzf Python-3.10.11.tgz
        cd Python-3.10.11
        ./configure --enable-optimizations
        make altinstall
        ln -sf /usr/local/bin/python3.10 /usr/bin/python3.10
    fi
    
    log_success "Python 3.10 安装完成"
}

# 创建项目用户
create_user() {
    log_header "👤 创建项目用户..."
    
    if id "$SERVICE_USER" &>/dev/null; then
        log_warning "用户 $SERVICE_USER 已存在"
    else
        useradd -r -s /bin/bash -d $PROJECT_DIR $SERVICE_USER
        log_success "用户 $SERVICE_USER 创建成功"
    fi
}

# 创建项目目录
setup_directories() {
    log_header "📁 设置项目目录..."
    
    # 创建主目录
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 创建子目录
    mkdir -p {uploads,outputs,temp,logs,static,config}
    
    # 设置权限
    chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    log_success "项目目录设置完成"
}

# 克隆或更新代码
setup_code() {
    log_header "📥 设置项目代码..."
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        log_info "更新现有代码..."
        cd $PROJECT_DIR
        sudo -u $SERVICE_USER git pull origin main
    else
        log_info "克隆项目代码..."
        # 如果有Git仓库，在这里克隆
        # sudo -u $SERVICE_USER git clone https://github.com/your-repo/aimovie.git $PROJECT_DIR
        
        # 临时：复制当前目录文件
        if [ "$PWD" != "$PROJECT_DIR" ]; then
            cp -r . $PROJECT_DIR/
            chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
        fi
    fi
    
    log_success "项目代码设置完成"
}

# 创建Python虚拟环境
setup_venv() {
    log_header "🏗️ 创建Python虚拟环境..."
    
    cd $PROJECT_DIR
    
    # 删除旧环境
    if [ -d "$VENV_NAME" ]; then
        rm -rf $VENV_NAME
    fi
    
    # 创建新环境
    sudo -u $SERVICE_USER python3.10 -m venv $VENV_NAME
    
    # 激活环境并安装依赖
    sudo -u $SERVICE_USER bash -c "
        source $VENV_NAME/bin/activate
        pip install --upgrade pip
        
        if [ -f requirements.txt ]; then
            pip install -r requirements.txt
        else
            pip install fastapi uvicorn streamlit requests opencv-python python-dotenv pydantic aiofiles
            pip install gunicorn supervisor redis celery
        fi
    "
    
    log_success "Python虚拟环境创建完成"
}

# 配置Nginx
setup_nginx() {
    log_header "🌐 配置Nginx..."
    
    # 备份原配置
    if [ -f /etc/nginx/sites-available/default ]; then
        cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
    fi
    
    # 创建AIMovie配置
    cat > /etc/nginx/sites-available/aimovie << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 500M;
    
    # 静态文件
    location /static/ {
        alias /opt/aimovie/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 上传文件
    location /uploads/ {
        alias /opt/aimovie/uploads/;
        expires 1d;
    }
    
    # 输出文件
    location /outputs/ {
        alias /opt/aimovie/outputs/;
        expires 1d;
    }
    
    # API服务
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Streamlit前端
    location / {
        proxy_pass http://127.0.0.1:8501/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF
    
    # 启用配置
    ln -sf /etc/nginx/sites-available/aimovie /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    systemctl enable nginx
    systemctl restart nginx
    
    log_success "Nginx配置完成"
}

# 配置Supervisor
setup_supervisor() {
    log_header "🔧 配置Supervisor..."
    
    # API服务配置
    cat > /etc/supervisor/conf.d/aimovie-api.conf << EOF
[program:aimovie-api]
command=$PROJECT_DIR/$VENV_NAME/bin/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 2
directory=$PROJECT_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/api.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=ENVIRONMENT=production
EOF
    
    # Streamlit前端配置
    cat > /etc/supervisor/conf.d/aimovie-frontend.conf << EOF
[program:aimovie-frontend]
command=$PROJECT_DIR/$VENV_NAME/bin/streamlit run src/frontend/app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
directory=$PROJECT_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/frontend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=ENVIRONMENT=production
EOF
    
    # 重新加载配置
    supervisorctl reread
    supervisorctl update
    systemctl enable supervisor
    systemctl restart supervisor
    
    log_success "Supervisor配置完成"
}

# 配置防火墙
setup_firewall() {
    log_header "🔥 配置防火墙..."
    
    if command -v ufw >/dev/null 2>&1; then
        # Ubuntu防火墙
        ufw --force enable
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
        log_success "UFW防火墙配置完成"
    elif command -v firewall-cmd >/dev/null 2>&1; then
        # CentOS防火墙
        systemctl enable firewalld
        systemctl start firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        log_success "Firewalld防火墙配置完成"
    else
        log_warning "未检测到防火墙，请手动配置"
    fi
}

# 创建管理脚本
create_management_scripts() {
    log_header "📝 创建管理脚本..."
    
    # 服务管理脚本
    cat > $PROJECT_DIR/manage.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/aimovie"
SERVICE_USER="aimovie"

case "$1" in
    start)
        echo "🚀 启动AIMovie服务..."
        supervisorctl start aimovie-api aimovie-frontend
        systemctl start nginx
        echo "✅ 服务启动完成"
        ;;
    stop)
        echo "⏹️ 停止AIMovie服务..."
        supervisorctl stop aimovie-api aimovie-frontend
        echo "✅ 服务停止完成"
        ;;
    restart)
        echo "🔄 重启AIMovie服务..."
        supervisorctl restart aimovie-api aimovie-frontend
        systemctl restart nginx
        echo "✅ 服务重启完成"
        ;;
    status)
        echo "📊 AIMovie服务状态:"
        supervisorctl status aimovie-api aimovie-frontend
        systemctl status nginx --no-pager -l
        ;;
    logs)
        echo "📋 查看日志:"
        echo "=== API日志 ==="
        tail -n 50 $PROJECT_DIR/logs/api.log
        echo "=== 前端日志 ==="
        tail -n 50 $PROJECT_DIR/logs/frontend.log
        ;;
    update)
        echo "🔄 更新AIMovie..."
        cd $PROJECT_DIR
        sudo -u $SERVICE_USER git pull origin main
        sudo -u $SERVICE_USER bash -c "source aimovie_env/bin/activate && pip install -r requirements.txt --upgrade"
        supervisorctl restart aimovie-api aimovie-frontend
        echo "✅ 更新完成"
        ;;
    backup)
        echo "💾 备份AIMovie数据..."
        BACKUP_DIR="/backup/aimovie_$(date +%Y%m%d_%H%M%S)"
        mkdir -p $BACKUP_DIR
        cp -r $PROJECT_DIR/uploads $BACKUP_DIR/
        cp -r $PROJECT_DIR/outputs $BACKUP_DIR/
        cp $PROJECT_DIR/.env $BACKUP_DIR/
        tar -czf $BACKUP_DIR.tar.gz -C /backup $(basename $BACKUP_DIR)
        rm -rf $BACKUP_DIR
        echo "✅ 备份完成: $BACKUP_DIR.tar.gz"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|update|backup}"
        exit 1
        ;;
esac
EOF
    
    chmod +x $PROJECT_DIR/manage.sh
    ln -sf $PROJECT_DIR/manage.sh /usr/local/bin/aimovie
    
    # 系统监控脚本
    cat > $PROJECT_DIR/monitor.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/aimovie"

echo "🖥️ AIMovie系统监控"
echo "==========================================="

# 系统资源
echo "💻 系统资源:"
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "内存使用: $(free -h | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
echo "磁盘使用: $(df -h $PROJECT_DIR | awk 'NR==2{print $5}')"
echo

# 服务状态
echo "🔧 服务状态:"
supervisorctl status aimovie-api aimovie-frontend | grep -E "(RUNNING|STOPPED|FATAL)"
echo "Nginx: $(systemctl is-active nginx)"
echo "Redis: $(systemctl is-active redis)"
echo

# 网络连接
echo "🌐 网络连接:"
echo "API端口8000: $(netstat -tlnp | grep :8000 | wc -l) 个连接"
echo "前端端口8501: $(netstat -tlnp | grep :8501 | wc -l) 个连接"
echo "HTTP端口80: $(netstat -tlnp | grep :80 | wc -l) 个连接"
echo

# 日志大小
echo "📋 日志文件:"
if [ -f "$PROJECT_DIR/logs/api.log" ]; then
    echo "API日志: $(du -h $PROJECT_DIR/logs/api.log | cut -f1)"
fi
if [ -f "$PROJECT_DIR/logs/frontend.log" ]; then
    echo "前端日志: $(du -h $PROJECT_DIR/logs/frontend.log | cut -f1)"
fi
echo

# 最近错误
echo "⚠️ 最近错误 (最近10条):"
if [ -f "$PROJECT_DIR/logs/api.log" ]; then
    grep -i "error\|exception\|failed" $PROJECT_DIR/logs/api.log | tail -5
fi
EOF
    
    chmod +x $PROJECT_DIR/monitor.sh
    
    # 自动备份脚本
    cat > $PROJECT_DIR/auto_backup.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/aimovie"
BACKUP_ROOT="/backup/aimovie"
KEEP_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_ROOT

# 创建备份
BACKUP_NAME="aimovie_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$BACKUP_ROOT/$BACKUP_NAME"

mkdir -p $BACKUP_DIR
cp -r $PROJECT_DIR/uploads $BACKUP_DIR/ 2>/dev/null || true
cp -r $PROJECT_DIR/outputs $BACKUP_DIR/ 2>/dev/null || true
cp $PROJECT_DIR/.env $BACKUP_DIR/ 2>/dev/null || true

# 压缩备份
cd $BACKUP_ROOT
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

# 清理旧备份
find $BACKUP_ROOT -name "aimovie_*.tar.gz" -mtime +$KEEP_DAYS -delete

echo "备份完成: $BACKUP_ROOT/$BACKUP_NAME.tar.gz"
EOF
    
    chmod +x $PROJECT_DIR/auto_backup.sh
    
    # 添加到crontab (每天凌晨2点备份)
    (crontab -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/auto_backup.sh") | crontab -
    
    log_success "管理脚本创建完成"
}

# 配置SSL证书 (可选)
setup_ssl() {
    if [ -n "$DOMAIN" ]; then
        log_header "🔒 配置SSL证书..."
        
        # 安装Certbot
        if command -v apt-get >/dev/null 2>&1; then
            apt-get install -y certbot python3-certbot-nginx
        elif command -v yum >/dev/null 2>&1; then
            yum install -y certbot python3-certbot-nginx
        fi
        
        # 获取证书
        certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
        
        # 自动续期
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        
        log_success "SSL证书配置完成"
    else
        log_warning "未配置域名，跳过SSL设置"
    fi
}

# 最终检查
final_check() {
    log_header "🧪 最终检查..."
    
    # 检查服务状态
    sleep 5
    
    if supervisorctl status aimovie-api | grep -q RUNNING; then
        log_success "API服务运行正常"
    else
        log_error "API服务启动失败"
    fi
    
    if supervisorctl status aimovie-frontend | grep -q RUNNING; then
        log_success "前端服务运行正常"
    else
        log_error "前端服务启动失败"
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx服务运行正常"
    else
        log_error "Nginx服务启动失败"
    fi
    
    # 检查端口
    if netstat -tlnp | grep -q :80; then
        log_success "HTTP端口80监听正常"
    else
        log_warning "HTTP端口80未监听"
    fi
}

# 主函数
main() {
    log_header "🎬 AIMovie 云端服务器自动化部署"
    log_header "=========================================="
    
    # 检查参数
    if [ "$1" = "--domain" ] && [ -n "$2" ]; then
        DOMAIN="$2"
        log_info "配置域名: $DOMAIN"
    fi
    
    # 执行部署步骤
    detect_os
    check_root
    update_system
    install_python
    create_user
    setup_directories
    setup_code
    setup_venv
    setup_nginx
    setup_supervisor
    setup_firewall
    create_management_scripts
    setup_ssl
    final_check
    
    # 完成信息
    log_header "🎉 部署完成！"
    log_header "=========================================="
    echo
    log_info "📋 服务信息:"
    echo "  🌐 Web访问: http://$(curl -s ifconfig.me || echo 'YOUR_SERVER_IP')"
    if [ -n "$DOMAIN" ]; then
        echo "  🌐 域名访问: https://$DOMAIN"
    fi
    echo "  📁 项目目录: $PROJECT_DIR"
    echo "  👤 服务用户: $SERVICE_USER"
    echo
    log_info "📋 管理命令:"
    echo "  aimovie start    - 启动服务"
    echo "  aimovie stop     - 停止服务"
    echo "  aimovie restart  - 重启服务"
    echo "  aimovie status   - 查看状态"
    echo "  aimovie logs     - 查看日志"
    echo "  aimovie update   - 更新项目"
    echo "  aimovie backup   - 备份数据"
    echo
    log_info "📋 配置文件:"
    echo "  ⚙️  环境配置: $PROJECT_DIR/.env"
    echo "  🌐 Nginx配置: /etc/nginx/sites-available/aimovie"
    echo "  🔧 Supervisor配置: /etc/supervisor/conf.d/aimovie-*.conf"
    echo
    log_warning "⚠️  重要提示:"
    echo "  1. 请配置 $PROJECT_DIR/.env 文件中的API密钥"
    echo "  2. 确保防火墙已正确配置"
    echo "  3. 定期检查日志和备份"
    echo
}

# 运行主函数
main "$@" 