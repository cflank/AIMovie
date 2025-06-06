print("🎬 AIMovie 简单启动测试")
print("✅ Python 运行正常")

import os
print(f"📁 当前目录: {os.getcwd()}")

# 检查关键文件
files = ['start.py', 'start_cloud.py', '.env', 'env_template.txt']
for f in files:
    if os.path.exists(f):
        print(f"✅ 找到文件: {f}")
    else:
        print(f"⚠️  未找到: {f}")

print("\n💡 建议:")
print("1. 如果要运行AIMovie，请先配置.env文件")
print("2. 安装依赖: pip install -r requirements_cloud.txt")
print("3. 运行: python start_cloud.py") 