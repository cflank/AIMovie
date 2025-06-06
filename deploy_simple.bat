@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🎬 AIMovie Cloud - 简化部署
echo ========================================
echo.

:: 设置项目目录
set PROJECT_DIR=%CD%
echo 📁 项目目录: %PROJECT_DIR%

:: 检查Python安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python已安装
    python --version
) else (
    echo ❌ Python未安装，请先安装Python 3.8+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 创建虚拟环境
echo 🔧 创建Python虚拟环境...
if exist "aimovie_env" (
    echo ⚠️ 虚拟环境已存在，将重新创建
    rmdir /s /q "aimovie_env"
)

python -m venv aimovie_env
if %errorLevel% neq 0 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
call aimovie_env\Scripts\activate.bat

:: 升级pip
echo 📦 升级pip...
python -m pip install --upgrade pip

:: 安装依赖
echo 📦 安装项目依赖...
echo 🔄 使用手动安装方式（避免编码问题）...
pip install fastapi uvicorn streamlit pydantic python-dotenv requests httpx aiofiles pillow python-multipart edge-tts tqdm colorama

if %errorLevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

:: 创建配置文件
echo ⚙️ 创建配置文件...
if not exist ".env" (
    if exist "env_template.txt" (
        copy env_template.txt .env
        echo ✅ 配置文件已创建: .env
        echo ⚠️ 请编辑 .env 文件，添加您的API密钥
    ) else (
        echo ⚠️ 未找到 env_template.txt，跳过配置文件创建
        echo 💡 您可以手动创建 .env 文件来配置API密钥
    )
) else (
    echo ✅ 配置文件已存在
)

:: 创建启动脚本
echo 📝 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%PROJECT_DIR%"
echo echo 📁 当前目录: %%CD%%
echo echo 🔍 检查启动文件...
echo if exist "start.py" ^(
echo     echo ✅ 找到 start.py
echo     call aimovie_env\Scripts\activate.bat
echo     echo 🚀 启动 start.py...
echo     python start.py
echo ^) else if exist "start_cloud.py" ^(
echo     echo ✅ 找到 start_cloud.py
echo     call aimovie_env\Scripts\activate.bat
echo     echo 🚀 启动 start_cloud.py...
echo     python start_cloud.py
echo ^) else if exist "main.py" ^(
echo     echo ✅ 找到 main.py
echo     call aimovie_env\Scripts\activate.bat
echo     echo 🚀 启动 main.py...
echo     python main.py
echo ^) else if exist "app.py" ^(
echo     echo ✅ 找到 app.py
echo     call aimovie_env\Scripts\activate.bat
echo     echo 🚀 启动 app.py...
echo     python app.py
echo ^) else ^(
echo     echo ❌ 未找到启动文件 ^(start.py, start_cloud.py, main.py, app.py^)
echo     echo 📋 当前目录文件列表:
echo     dir *.py
echo     echo.
echo     echo 💡 请手动运行您的Python应用
echo     echo    例如: python your_app.py
echo ^)
echo echo.
echo echo 按任意键退出...
echo pause
) > "启动AIMovie.bat"

:: 创建数据目录
echo 📁 创建数据目录...
if not exist "data\input" mkdir "data\input"
if not exist "data\output" mkdir "data\output"
if not exist "data\temp" mkdir "data\temp"
if not exist "logs" mkdir "logs"

echo.
echo ========================================
echo 🎉 AIMovie Cloud 部署完成！
echo ========================================
echo.
echo 📍 项目位置: %PROJECT_DIR%
echo 📝 启动脚本: 启动AIMovie.bat
echo.
echo 📋 下一步操作:
echo 1. 编辑配置文件: %PROJECT_DIR%\.env
echo 2. 添加至少一个LLM服务的API密钥
echo 3. 双击"启动AIMovie.bat"启动应用
echo.
echo 💡 推荐配置 (高性价比):
echo    - 通义千问: QWEN_API_KEY
echo    - 阿里云TTS: ALIYUN_ACCESS_KEY_ID + ALIYUN_ACCESS_KEY_SECRET
echo    - 百度AI: BAIDU_API_KEY + BAIDU_SECRET_KEY
echo.
echo 📚 详细文档: %PROJECT_DIR%\CLOUD_USAGE_GUIDE.md
echo 🌐 GitHub: https://github.com/cflank/AIMovie
echo.

:: 询问是否立即启动
set /p choice="是否现在启动AIMovie? (y/n): "
if /i "%choice%"=="y" (
    echo 🚀 正在启动AIMovie...
    start "" "%PROJECT_DIR%\启动AIMovie.bat"
) else (
    echo 💡 您可以稍后双击"启动AIMovie.bat"启动应用
)

echo.
echo 按任意键退出...
pause >nul 