#!/usr/bin/env python3
"""
AIMovie Cloud 启动脚本
支持多种大模型组合配置的云端版本
"""

import os
import sys
import subprocess
import time
import logging
import signal
from pathlib import Path
from typing import Optional, Dict, Any
import multiprocessing as mp

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.preset_configs import preset_manager, PresetType
from src.config.cloud_settings import get_cloud_settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/startup.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 全局进程列表
processes = []


def signal_handler(signum, frame):
    """信号处理器，优雅关闭所有进程"""
    logger.info("接收到关闭信号，正在关闭所有服务...")
    for process in processes:
        if process.poll() is None:  # 进程仍在运行
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    logger.info("所有服务已关闭")
    sys.exit(0)


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        sys.exit(1)
    logger.info(f"Python版本: {sys.version}")


def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'requests', 
        'python-dotenv', 'pydantic', 'aiofiles'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
        
        # 检查可用的requirements文件
        req_files = []
        if Path('requirements_cloud.txt').exists():
            req_files.append('requirements_cloud.txt')
        if Path('requirements_cloud_minimal.txt').exists():
            req_files.append('requirements_cloud_minimal.txt')
        if Path('requirements.txt').exists():
            req_files.append('requirements.txt')
        
        if req_files:
            logger.info(f"请选择安装依赖:")
            for i, req_file in enumerate(req_files, 1):
                logger.info(f"  {i}. pip install -r {req_file}")
            logger.info("推荐使用 requirements_cloud_minimal.txt 进行最小化安装")
        else:
            logger.info("请手动安装缺少的依赖包")
        
        sys.exit(1)
    
    logger.info("依赖包检查通过")


def create_directories():
    """创建必要的目录"""
    directories = [
        'logs',
        'temp',
        'uploads',
        'outputs',
        'cache'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    logger.info("目录结构检查完成")


def check_env_file():
    """检查环境配置文件"""
    env_file = Path('.env')
    env_template = Path('env_template.txt')
    
    if not env_file.exists():
        if env_template.exists():
            logger.warning(".env文件不存在，正在从模板创建...")
            env_file.write_text(env_template.read_text(encoding='utf-8'), encoding='utf-8')
            logger.info("已创建.env文件，请编辑配置API密钥")
        else:
            logger.error("环境配置文件不存在，请创建.env文件")
            sys.exit(1)
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    logger.info("环境配置文件检查完成")


def validate_configuration():
    """验证配置"""
    try:
        settings = get_cloud_settings()
        preset_info = settings.get_preset_info()
        
        logger.info(f"当前配置: {preset_info['name']}")
        logger.info(f"预估成本: {preset_info['estimated_cost']}")
        
        # 检查可用服务
        available_llm = preset_info['available_llm']
        available_tts = preset_info['available_tts']
        available_vision = preset_info['available_vision']
        
        if available_llm == 0:
            logger.error("没有可用的LLM服务，请配置API密钥")
            show_configuration_help()
            return False
        
        logger.info(f"可用服务: LLM({available_llm}) TTS({available_tts}) Vision({available_vision})")
        
        # 显示成本估算
        cost_estimate = settings.estimate_cost()
        logger.info(f"预估单视频成本: ¥{cost_estimate['total_cost']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        return False


def show_configuration_help():
    """显示配置帮助信息"""
    logger.info("=" * 60)
    logger.info("🔧 配置帮助")
    logger.info("=" * 60)
    
    # 显示预设方案
    presets = preset_manager.list_presets()
    logger.info("📋 可用的预设方案:")
    for preset in presets:
        logger.info(f"  {preset['name']}: {preset['description']}")
        logger.info(f"    预估成本: {preset['estimated_cost']}")
    
    logger.info("")
    logger.info("🔑 配置步骤:")
    logger.info("1. 编辑 .env 文件")
    logger.info("2. 设置 PRESET_CONFIG=cost_effective (或其他方案)")
    logger.info("3. 根据选择的方案配置对应的API密钥")
    logger.info("4. 重新启动应用")
    logger.info("")
    logger.info("📖 详细配置指南: https://github.com/cflank/AIMovie/blob/master/SUPPORTED_MODELS.md")
    logger.info("=" * 60)


def start_api_server():
    """启动API服务器"""
    logger.info("启动API服务器...")
    
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = int(os.getenv("API_PORT", "8000"))
    
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.cloud_main:app",
        "--host", api_host,
        "--port", str(api_port),
        "--reload",
        "--log-level", "info"
    ]
    
    try:
        process = subprocess.Popen(cmd, cwd=project_root)
        processes.append(process)
        logger.info(f"API服务器已启动: http://{api_host}:{api_port}")
        return process
    except Exception as e:
        logger.error(f"启动API服务器失败: {e}")
        return None


def start_streamlit_app():
    """启动Streamlit应用"""
    logger.info("启动Streamlit前端...")
    
    streamlit_port = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "frontend/cloud_streamlit_app.py",
        "--server.port", str(streamlit_port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        process = subprocess.Popen(cmd, cwd=project_root)
        processes.append(process)
        logger.info(f"Streamlit应用已启动: http://localhost:{streamlit_port}")
        return process
    except Exception as e:
        logger.error(f"启动Streamlit应用失败: {e}")
        return None


def wait_for_api_ready(host="127.0.0.1", port=8000, timeout=30):
    """等待API服务就绪"""
    import requests
    
    url = f"http://{host}:{port}/health"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("API服务已就绪")
                return True
        except:
            pass
        time.sleep(1)
    
    logger.warning("API服务启动超时")
    return False


def show_startup_info():
    """显示启动信息"""
    settings = get_cloud_settings()
    preset_info = settings.get_preset_info()
    
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = int(os.getenv("API_PORT", "8000"))
    streamlit_port = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    logger.info("=" * 60)
    logger.info("🎬 AIMovie Cloud 启动成功!")
    logger.info("=" * 60)
    logger.info(f"📋 当前配置: {preset_info['name']}")
    logger.info(f"💰 预估成本: {preset_info['estimated_cost']}")
    logger.info(f"🔗 前端界面: http://localhost:{streamlit_port}")
    logger.info(f"🔗 API文档: http://{api_host}:{api_port}/docs")
    logger.info(f"🔗 健康检查: http://{api_host}:{api_port}/health")
    logger.info("=" * 60)
    logger.info("💡 使用提示:")
    logger.info("  - 在前端界面上传视频文件开始处理")
    logger.info("  - 可在'配置选择'选项卡中切换大模型组合")
    logger.info("  - 查看'成本管理'选项卡监控API使用情况")
    logger.info("  - 按 Ctrl+C 停止所有服务")
    logger.info("=" * 60)


def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎬 AIMovie Cloud 启动中...")
    
    # 系统检查
    check_python_version()
    check_dependencies()
    create_directories()
    check_env_file()
    
    # 配置验证
    if not validate_configuration():
        logger.error("配置验证失败，请检查配置后重试")
        sys.exit(1)
    
    # 启动服务
    api_process = start_api_server()
    if not api_process:
        logger.error("API服务器启动失败")
        sys.exit(1)
    
    # 等待API服务就绪
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = int(os.getenv("API_PORT", "8000"))
    
    if not wait_for_api_ready(api_host, api_port):
        logger.error("API服务启动超时")
        signal_handler(None, None)
        sys.exit(1)
    
    # 启动前端
    streamlit_process = start_streamlit_app()
    if not streamlit_process:
        logger.error("Streamlit应用启动失败")
        signal_handler(None, None)
        sys.exit(1)
    
    # 等待前端就绪
    time.sleep(3)
    
    # 显示启动信息
    show_startup_info()
    
    # 监控进程
    try:
        while True:
            # 检查进程状态
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    logger.error(f"进程 {i} 意外退出，退出码: {process.returncode}")
                    signal_handler(None, None)
                    sys.exit(1)
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main() 