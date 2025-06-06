#!/usr/bin/env python3
"""
AIMovie Cloud 启动脚本
云端版本 - 使用云端API服务
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🌐 AIMovie Cloud                          ║
    ║                AI视频解说生成器 - 云端版                      ║
    ║                                                              ║
    ║  🌟 高性价比云端API组合                                       ║
    ║  💰 成本透明，按需付费                                        ║
    ║  🚀 无需GPU，云端处理                                         ║
    ║                                                              ║
    ║  Version: 2.0.0 (Cloud Edition)                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_environment():
    """检查环境配置"""
    print("\n🔧 检查环境配置...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到.env文件")
        print("📋 请复制cloud_env_template.txt为.env并配置API密钥")
        
        # 询问是否创建示例配置
        response = input("是否创建示例配置文件? (y/n): ").lower()
        if response == 'y':
            try:
                template_file = Path("cloud_env_template.txt")
                if template_file.exists():
                    import shutil
                    shutil.copy(template_file, env_file)
                    print(f"✅ 已创建.env文件，请编辑配置API密钥")
                    print(f"📝 配置文件位置: {env_file.absolute()}")
                else:
                    print("❌ 未找到配置模板文件")
            except Exception as e:
                print(f"❌ 创建配置文件失败: {e}")
        
        return False
    
    print("✅ 找到环境配置文件")
    
    # 检查关键配置
    from dotenv import load_dotenv
    load_dotenv()
    
    required_configs = []
    optional_configs = []
    
    # 检查LLM服务
    if os.getenv("QWEN_API_KEY"):
        required_configs.append("✅ 通义千问 API")
    elif os.getenv("ERNIE_API_KEY") and os.getenv("ERNIE_SECRET_KEY"):
        required_configs.append("✅ 文心一言 API")
    elif os.getenv("OPENAI_API_KEY"):
        required_configs.append("✅ OpenAI API")
    else:
        print("❌ 未配置任何LLM服务API密钥")
        print("💡 至少需要配置以下之一:")
        print("   - QWEN_API_KEY (推荐，性价比最高)")
        print("   - ERNIE_API_KEY + ERNIE_SECRET_KEY")
        print("   - OPENAI_API_KEY")
        return False
    
    # 检查TTS服务
    if os.getenv("ALIYUN_ACCESS_KEY_ID") and os.getenv("ALIYUN_ACCESS_KEY_SECRET"):
        optional_configs.append("✅ 阿里云TTS")
    if os.getenv("TENCENT_SECRET_ID") and os.getenv("TENCENT_SECRET_KEY"):
        optional_configs.append("✅ 腾讯云TTS")
    
    # 检查视频分析服务
    if os.getenv("BAIDU_API_KEY") and os.getenv("BAIDU_SECRET_KEY"):
        optional_configs.append("✅ 百度AI")
    if os.getenv("QWEN_VL_API_KEY"):
        optional_configs.append("✅ 通义千问-VL")
    
    print("📋 已配置的服务:")
    for config in required_configs + optional_configs:
        print(f"   {config}")
    
    if not optional_configs:
        print("⚠️  建议配置更多服务以获得更好的效果")
    
    return True

def install_dependencies():
    """安装依赖"""
    print("\n📦 检查并安装依赖...")
    
    requirements_file = Path("requirements_cloud.txt")
    if not requirements_file.exists():
        print("⚠️  未找到requirements_cloud.txt，使用requirements.txt")
        requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ 未找到依赖文件")
        return False
    
    try:
        print("🔄 安装Python依赖...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 依赖安装失败:")
            print(result.stderr)
            return False
        
        print("✅ 依赖安装完成")
        return True
        
    except Exception as e:
        print(f"❌ 安装依赖时出错: {e}")
        return False

def check_api_service():
    """检查API服务是否运行"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_api_service():
    """启动API服务"""
    print("\n🚀 启动API服务...")
    
    try:
        # 启动API服务
        api_process = subprocess.Popen([
            sys.executable, "-m", "src.api.cloud_main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        print("⏳ 等待API服务启动...")
        for i in range(30):  # 最多等待30秒
            if check_api_service():
                print("✅ API服务启动成功")
                print("🌐 API地址: http://127.0.0.1:8000")
                print("📚 API文档: http://127.0.0.1:8000/docs")
                return api_process
            
            time.sleep(1)
            print(f"   等待中... ({i+1}/30)")
        
        print("❌ API服务启动超时")
        api_process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ 启动API服务失败: {e}")
        return None

def start_frontend():
    """启动前端界面"""
    print("\n🎨 启动前端界面...")
    
    try:
        # 启动Streamlit前端
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/cloud_streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ])
        
        print("✅ 前端界面启动成功")
        print("🎬 访问地址: http://127.0.0.1:8501")
        return frontend_process
        
    except Exception as e:
        print(f"❌ 启动前端失败: {e}")
        return None

def show_usage_info():
    """显示使用说明"""
    print("\n" + "="*60)
    print("🎯 使用说明")
    print("="*60)
    print("1. 🌐 API服务: http://127.0.0.1:8000")
    print("   - 查看API文档: http://127.0.0.1:8000/docs")
    print("   - 健康检查: http://127.0.0.1:8000/health")
    print()
    print("2. 🎬 Web界面: http://127.0.0.1:8501")
    print("   - 完整流程: 一键生成解说视频")
    print("   - 视频分析: 智能分析视频内容")
    print("   - 解说生成: AI生成解说词")
    print("   - 语音合成: 多种语音风格")
    print("   - 文件管理: 下载和管理文件")
    print()
    print("3. 💰 成本控制:")
    print("   - 通义千问: ¥0.0008/1K tokens (推荐)")
    print("   - 阿里云TTS: ¥0.00002/字符")
    print("   - 百度AI: ¥0.002/图片")
    print("   - 预估5分钟视频: ¥0.06-0.12")
    print()
    print("4. 🔧 配置优化:")
    print("   - 减少帧采样频率节省成本")
    print("   - 使用Edge-TTS免费语音合成")
    print("   - 批量处理降低单次成本")
    print("="*60)

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 检查环境配置
    if not check_environment():
        print("\n❌ 环境配置不完整，请配置API密钥后重新运行")
        print("📖 配置帮助: 查看cloud_env_template.txt中的详细说明")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n❌ 依赖安装失败，请手动安装")
        return
    
    # 检查是否已有API服务运行
    if check_api_service():
        print("\n✅ 检测到API服务已在运行")
    else:
        # 启动API服务
        api_process = start_api_service()
        if not api_process:
            print("\n❌ API服务启动失败")
            return
    
    # 启动前端界面
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ 前端界面启动失败")
        return
    
    # 显示使用说明
    show_usage_info()
    
    try:
        print("\n🎉 AIMovie Cloud 启动完成!")
        print("💡 按 Ctrl+C 停止服务")
        
        # 等待用户中断
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        
        # 停止进程
        if 'frontend_process' in locals():
            frontend_process.terminate()
            print("✅ 前端服务已停止")
        
        if 'api_process' in locals():
            api_process.terminate()
            print("✅ API服务已停止")
        
        print("👋 感谢使用 AIMovie Cloud!")

if __name__ == "__main__":
    main() 