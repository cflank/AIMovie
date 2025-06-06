#!/usr/bin/env python3
"""
环境测试脚本
"""

import sys
import os

def test_environment():
    print("🔍 环境测试")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    print(f"Python路径: {sys.executable}")
    
    # 测试基本模块
    modules_to_test = [
        'os', 'sys', 'pathlib', 'subprocess'
    ]
    
    print("\n📦 测试基本模块:")
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
    
    # 测试可选模块
    optional_modules = [
        'requests', 'streamlit', 'fastapi', 'uvicorn', 'dotenv'
    ]
    
    print("\n📦 测试可选模块:")
    for module in optional_modules:
        try:
            if module == 'dotenv':
                from dotenv import load_dotenv
            else:
                __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"⚠️  {module}: 未安装")
    
    # 检查文件
    print("\n📁 检查项目文件:")
    files_to_check = [
        'start.py', 'start_cloud.py', 'main.py', 'app.py',
        '.env', 'env_template.txt',
        'requirements.txt', 'requirements_cloud.txt'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file}: 不存在")
    
    print("\n🎉 环境测试完成!")

if __name__ == "__main__":
    test_environment() 