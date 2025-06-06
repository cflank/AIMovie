#!/bin/bash

# AIMovie Cloud - 云端服务器一键部署脚本
# 支持 Ubuntu/Debian/CentOS/RHEL

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo
    echo "========================================"
    echo "🎬 AIMovie Cloud - 云端服务器部署"
    echo "========================================"
    echo
}

print_success() {
    print_message "✅ $1" $GREEN
}

print_error() {
    print_message "❌ $1" $RED
}

print_warning() {
    print_message "⚠️ $1" $YELLOW
}

print_info() {
    print_message "🔍 $1" $BLUE
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "检测到root用户，建议使用普通用户运行"
        read -p "是否继续? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
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
    
    print_info "检测到操作系统: $OS $VER"
}

# 安装系统依赖
install_system_deps() {
    print_info "安装系统依赖..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv git curl wget unzip ffmpeg
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip git curl wget unzip epel-release
        sudo yum install -y ffmpeg
    elif [[ "$OS" == *"Fedora"* ]]; then
        sudo dnf update -y
        sudo dnf install -y python3 python3-pip git curl wget unzip ffmpeg
    else
        print_error "不支持的操作系统: $OS"
        exit 1
    fi
    
    print_success "系统依赖安装完成"
}

# 检查Python版本
check_python() {
    print_info "检查Python环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python已安装: $PYTHON_VERSION"
        
        # 检查版本是否满足要求 (3.8+)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python版本满足要求"
        else
            print_error "Python版本过低，需要3.8+，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python3未安装"
        exit 1
    fi
}

# 设置项目目录
setup_project() {
    PROJECT_DIR="$HOME/AIMovie"
    print_info "项目将安装到: $PROJECT_DIR"
    
    # 克隆或更新项目
    if [[ -d "$PROJECT_DIR" ]]; then
        print_info "项目目录已存在，正在更新..."
        cd "$PROJECT_DIR"
        git pull origin master || {
            print_warning "更新失败，将重新克隆项目"
            cd "$HOME"
            rm -rf "$PROJECT_DIR"
            git clone https://github.com/cflank/AIMovie.git
        }
    else
        print_info "正在克隆项目..."
        cd "$HOME"
        git clone https://github.com/cflank/AIMovie.git || {
            print_error "项目克隆失败，请检查网络连接"
            exit 1
        }
    fi
    
    cd "$PROJECT_DIR"
    print_success "项目代码准备完成"
}

# 创建虚拟环境
setup_venv() {
    print_info "创建Python虚拟环境..."
    
    if [[ -d "aimovie_env" ]]; then
        print_warning "虚拟环境已存在，将重新创建"
        rm -rf "aimovie_env"
    fi
    
    python3 -m venv aimovie_env || {
        print_error "虚拟环境创建失败"
        exit 1
    }
    
    # 激活虚拟环境
    source aimovie_env/bin/activate
    
    # 升级pip
    print_info "升级pip..."
    pip install --upgrade pip
    
    print_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    pip install -r requirements.txt || {
        print_error "依赖安装失败"
        exit 1
    }
    
    print_success "Python依赖安装完成"
}

# 创建配置文件
setup_config() {
    print_info "创建配置文件..."
    
    if [[ ! -f ".env" ]]; then
        cp env_template.txt .env
        print_success "配置文件已创建: .env"
        print_warning "请编辑 .env 文件，添加您的API密钥"
    else
        print_success "配置文件已存在"
    fi
}

# 创建系统服务
create_systemd_service() {
    print_info "创建系统服务..."
    
    # 创建服务文件
    sudo tee /etc/systemd/system/aimovie.service > /dev/null <<EOF
[Unit]
Description=AIMovie Cloud Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/aimovie_env/bin
ExecStart=$PROJECT_DIR/aimovie_env/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载systemd
    sudo systemctl daemon-reload
    sudo systemctl enable aimovie
    
    print_success "系统服务创建完成"
}

# 配置防火墙
setup_firewall() {
    print_info "配置防火墙..."
    
    # 检查防火墙状态
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW
        sudo ufw allow 8000/tcp
        sudo ufw allow 8501/tcp
        print_success "UFW防火墙规则已添加"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo firewall-cmd --permanent --add-port=8000/tcp
        sudo firewall-cmd --permanent --add-port=8501/tcp
        sudo firewall-cmd --reload
        print_success "firewalld防火墙规则已添加"
    else
        print_warning "未检测到防火墙，请手动开放端口8000和8501"
    fi
}

# 创建启动脚本
create_start_script() {
    print_info "创建启动脚本..."
    
    cat > start_aimovie.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="$HOME/AIMovie"
cd "$PROJECT_DIR"

echo
echo "========================================"
echo "🎬 AIMovie Cloud 正在启动..."
echo "========================================"
echo

# 激活虚拟环境
source aimovie_env/bin/activate

# 检查配置
if [[ ! -f ".env" ]]; then
    echo "❌ 配置文件不存在，请先配置API密钥"
    exit 1
fi

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")

echo "🌐 Web界面: http://$SERVER_IP:8501"
echo "🔧 API文档: http://$SERVER_IP:8000/docs"
echo

# 启动服务
python start.py
EOF

    chmod +x start_aimovie.sh
    print_success "启动脚本创建完成"
}

# 创建数据目录
create_directories() {
    print_info "创建数据目录..."
    
    mkdir -p data/{input,output,temp}
    mkdir -p logs
    
    print_success "数据目录创建完成"
}

# 检查端口占用
check_ports() {
    print_info "检查端口占用..."
    
    if netstat -tuln | grep -q ":8000 "; then
        print_warning "端口8000已被占用"
    fi
    
    if netstat -tuln | grep -q ":8501 "; then
        print_warning "端口8501已被占用"
    fi
}

# 显示部署完成信息
show_completion_info() {
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
    
    echo
    echo "========================================"
    echo "🎉 AIMovie Cloud 部署完成！"
    echo "========================================"
    echo
    echo "📍 项目位置: $PROJECT_DIR"
    echo "🌐 服务器IP: $SERVER_IP"
    echo
    echo "📋 下一步操作:"
    echo "1. 编辑配置文件: $PROJECT_DIR/.env"
    echo "2. 添加至少一个LLM服务的API密钥"
    echo "3. 启动服务:"
    echo "   方式1: ./start_aimovie.sh (前台运行)"
    echo "   方式2: sudo systemctl start aimovie (后台服务)"
    echo
    echo "💡 推荐配置 (高性价比):"
    echo "   - 通义千问: QWEN_API_KEY"
    echo "   - 阿里云TTS: ALIYUN_ACCESS_KEY_ID + ALIYUN_ACCESS_KEY_SECRET"
    echo "   - 百度AI: BAIDU_API_KEY + BAIDU_SECRET_KEY"
    echo
    echo "🌐 访问地址:"
    echo "   - Web界面: http://$SERVER_IP:8501"
    echo "   - API文档: http://$SERVER_IP:8000/docs"
    echo
    echo "🔧 服务管理命令:"
    echo "   - 启动: sudo systemctl start aimovie"
    echo "   - 停止: sudo systemctl stop aimovie"
    echo "   - 重启: sudo systemctl restart aimovie"
    echo "   - 状态: sudo systemctl status aimovie"
    echo "   - 日志: sudo journalctl -u aimovie -f"
    echo
    echo "📚 详细文档: $PROJECT_DIR/CLOUD_USAGE_GUIDE.md"
    echo "🌐 GitHub: https://github.com/cflank/AIMovie"
    echo
}

# 询问是否立即启动
ask_start_service() {
    read -p "是否现在启动AIMovie服务? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "正在启动AIMovie服务..."
        sudo systemctl start aimovie
        sleep 3
        
        if sudo systemctl is-active --quiet aimovie; then
            print_success "服务启动成功"
            print_info "您可以通过以下地址访问:"
            SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
            echo "   - Web界面: http://$SERVER_IP:8501"
            echo "   - API文档: http://$SERVER_IP:8000/docs"
        else
            print_error "服务启动失败，请检查日志: sudo journalctl -u aimovie -f"
        fi
    else
        print_info "您可以稍后使用以下命令启动服务:"
        echo "   sudo systemctl start aimovie"
    fi
}

# 主函数
main() {
    print_header
    
    check_root
    detect_os
    install_system_deps
    check_python
    setup_project
    setup_venv
    install_python_deps
    setup_config
    create_systemd_service
    setup_firewall
    create_start_script
    create_directories
    check_ports
    
    show_completion_info
    ask_start_service
    
    echo
    echo "部署完成！感谢使用 AIMovie Cloud 🚀"
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查上述输出"; exit 1' ERR

# 运行主函数
main "$@" 