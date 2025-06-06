#!/bin/bash

# AIMovie Docker容器化部署脚本
# 支持开发和生产环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 项目配置
PROJECT_NAME="aimovie"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

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

# 显示帮助信息
show_help() {
    echo "AIMovie Docker部署脚本"
    echo
    echo "用法: $0 [选项] [命令]"
    echo
    echo "命令:"
    echo "  deploy     - 部署所有服务"
    echo "  start      - 启动服务"
    echo "  stop       - 停止服务"
    echo "  restart    - 重启服务"
    echo "  status     - 查看服务状态"
    echo "  logs       - 查看日志"
    echo "  update     - 更新服务"
    echo "  cleanup    - 清理资源"
    echo "  backup     - 备份数据"
    echo "  restore    - 恢复数据"
    echo
    echo "选项:"
    echo "  -e, --env ENV     环境 (dev/prod，默认: dev)"
    echo "  -f, --file FILE   Docker Compose文件 (默认: docker-compose.yml)"
    echo "  -h, --help        显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 deploy -e prod"
    echo "  $0 start"
    echo "  $0 logs aimovie-api"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 设置compose命令
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    log_success "依赖检查通过"
}

# 检查环境文件
check_env_file() {
    log_info "检查环境配置..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "环境文件 $ENV_FILE 不存在"
        log_info "创建示例环境文件..."
        
        cat > "$ENV_FILE" << 'EOF'
# AIMovie 环境配置

# 基础配置
ENVIRONMENT=development
DEBUG=true

# 数据库配置
POSTGRES_PASSWORD=aimovie123

# 监控配置
GRAFANA_PASSWORD=admin123

# API密钥配置 (请填入实际值)
QWEN_VL_API_KEY=your_qwen_api_key
BAIDU_API_KEY=your_baidu_api_key
BAIDU_SECRET_KEY=your_baidu_secret_key
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
MOONSHOT_API_KEY=your_moonshot_api_key

# 阿里云配置
ALIYUN_ACCESS_KEY_ID=your_aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=your_aliyun_access_key_secret

# 其他配置
MAX_FILE_SIZE=500
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp
EOF
        
        log_warning "请编辑 $ENV_FILE 文件，填入正确的API密钥"
        read -p "是否现在编辑配置文件? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} "$ENV_FILE"
        fi
    else
        log_success "环境文件已存在"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建项目目录..."
    
    mkdir -p {uploads,outputs,temp,logs,ssl}
    mkdir -p {nginx/conf.d,monitoring}
    
    log_success "目录创建完成"
}

# 创建Nginx配置
create_nginx_config() {
    log_info "创建Nginx配置..."
    
    mkdir -p nginx/conf.d
    
    cat > nginx/conf.d/default.conf << 'EOF'
upstream aimovie_api {
    server aimovie-api:8000;
}

upstream aimovie_frontend {
    server aimovie-frontend:8501;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 500M;
    
    # 静态文件
    location /uploads/ {
        alias /var/www/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    location /outputs/ {
        alias /var/www/outputs/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # API路由
    location /api/ {
        proxy_pass http://aimovie_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://aimovie_api/health;
        access_log off;
    }
    
    # 前端应用
    location / {
        proxy_pass http://aimovie_frontend/;
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
    
    log_success "Nginx配置创建完成"
}

# 创建监控配置
create_monitoring_config() {
    log_info "创建监控配置..."
    
    mkdir -p monitoring/grafana/{dashboards,datasources}
    
    # Prometheus配置
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aimovie-api'
    static_configs:
      - targets: ['aimovie-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
EOF
    
    # Grafana数据源配置
    cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    log_success "监控配置创建完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    $COMPOSE_CMD -f "$COMPOSE_FILE" build --no-cache
    
    log_success "镜像构建完成"
}

# 部署服务
deploy_services() {
    log_header "🚀 部署AIMovie服务..."
    
    check_dependencies
    check_env_file
    create_directories
    create_nginx_config
    create_monitoring_config
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        log_info "生产环境部署..."
        export ENVIRONMENT=production
        export DEBUG=false
    else
        log_info "开发环境部署..."
        export ENVIRONMENT=development
        export DEBUG=true
    fi
    
    # 停止现有服务
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    
    # 构建并启动服务
    build_images
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services_health
    
    log_success "部署完成！"
    show_access_info
}

# 启动服务
start_services() {
    log_info "启动服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" start
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" stop
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    $COMPOSE_CMD -f "$COMPOSE_FILE" restart
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "服务状态:"
    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
    echo
    
    log_info "容器资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# 查看日志
show_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        log_info "查看 $service 服务日志:"
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f "$service"
    else
        log_info "查看所有服务日志:"
        $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f
    fi
}

# 更新服务
update_services() {
    log_info "更新服务..."
    
    # 拉取最新代码
    if [ -d ".git" ]; then
        git pull origin main
    fi
    
    # 重新构建并部署
    build_images
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
    
    log_success "服务更新完成"
}

# 清理资源
cleanup_resources() {
    log_warning "这将删除所有容器、镜像和数据卷"
    read -p "确定要继续吗? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理Docker资源..."
        
        # 停止并删除容器
        $COMPOSE_CMD -f "$COMPOSE_FILE" down -v --remove-orphans
        
        # 删除镜像
        docker images | grep "$PROJECT_NAME" | awk '{print $3}' | xargs -r docker rmi -f
        
        # 清理未使用的资源
        docker system prune -f
        
        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份上传文件
    if [ -d "uploads" ]; then
        cp -r uploads "$BACKUP_DIR/"
    fi
    
    # 备份输出文件
    if [ -d "outputs" ]; then
        cp -r outputs "$BACKUP_DIR/"
    fi
    
    # 备份配置文件
    cp "$ENV_FILE" "$BACKUP_DIR/"
    
    # 备份数据库
    if docker ps | grep -q "aimovie-postgres"; then
        docker exec aimovie-postgres pg_dump -U aimovie aimovie > "$BACKUP_DIR/database.sql"
    fi
    
    # 压缩备份
    tar -czf "$BACKUP_DIR.tar.gz" -C backup "$(basename "$BACKUP_DIR")"
    rm -rf "$BACKUP_DIR"
    
    log_success "备份完成: $BACKUP_DIR.tar.gz"
}

# 恢复数据
restore_data() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        echo "用法: $0 restore <backup_file.tar.gz>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_info "恢复数据从: $backup_file"
    
    # 解压备份
    RESTORE_DIR="restore_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$RESTORE_DIR"
    tar -xzf "$backup_file" -C "$RESTORE_DIR" --strip-components=1
    
    # 恢复文件
    if [ -d "$RESTORE_DIR/uploads" ]; then
        cp -r "$RESTORE_DIR/uploads" ./
    fi
    
    if [ -d "$RESTORE_DIR/outputs" ]; then
        cp -r "$RESTORE_DIR/outputs" ./
    fi
    
    # 恢复数据库
    if [ -f "$RESTORE_DIR/database.sql" ] && docker ps | grep -q "aimovie-postgres"; then
        docker exec -i aimovie-postgres psql -U aimovie aimovie < "$RESTORE_DIR/database.sql"
    fi
    
    # 清理临时目录
    rm -rf "$RESTORE_DIR"
    
    log_success "数据恢复完成"
}

# 检查服务健康状态
check_services_health() {
    log_info "检查服务健康状态..."
    
    local services=("aimovie-api" "aimovie-frontend" "nginx")
    local healthy=true
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            log_success "$service 运行正常"
        else
            log_error "$service 运行异常"
            healthy=false
        fi
    done
    
    if [ "$healthy" = true ]; then
        log_success "所有服务运行正常"
    else
        log_warning "部分服务运行异常，请检查日志"
    fi
}

# 显示访问信息
show_access_info() {
    log_header "🎉 AIMovie 部署完成！"
    echo
    log_info "访问地址:"
    echo "  🌐 Web界面: http://localhost"
    echo "  📡 API文档: http://localhost/api/docs"
    echo "  📊 监控面板: http://localhost:3000 (admin/admin123)"
    echo "  🌸 任务监控: http://localhost:5555"
    echo "  📈 Prometheus: http://localhost:9090"
    echo
    log_info "管理命令:"
    echo "  查看状态: $0 status"
    echo "  查看日志: $0 logs [service]"
    echo "  重启服务: $0 restart"
    echo "  更新服务: $0 update"
    echo "  备份数据: $0 backup"
    echo
}

# 主函数
main() {
    # 默认参数
    ENVIRONMENT="dev"
    COMMAND=""
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -f|--file)
                COMPOSE_FILE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            deploy|start|stop|restart|status|logs|update|cleanup|backup|restore)
                COMMAND="$1"
                shift
                break
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查命令
    if [ -z "$COMMAND" ]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
    
    # 执行命令
    case "$COMMAND" in
        deploy)
            deploy_services
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$1"
            ;;
        update)
            update_services
            ;;
        cleanup)
            cleanup_resources
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$1"
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@" 