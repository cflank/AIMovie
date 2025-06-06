@echo off
chcp 65001 >nul
echo.
echo 🎬 AIMovie 智能视频解说生成器
echo ==========================================
echo.

:: 检查是否在项目目录
if not exist "frontend\cloud_streamlit_app.py" (
    echo ❌ 请在AIMovie项目根目录运行此脚本
    pause
    exit /b 1
)

:: 激活虚拟环境
echo 🔄 激活虚拟环境...
if exist "aimovie_env\Scripts\activate.bat" (
    call aimovie_env\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ❌ 未找到虚拟环境，请先运行 deploy_final.bat
    pause
    exit /b 1
)

:: 检查依赖
echo.
echo 🔍 检查依赖包...
python -c "import streamlit, fastapi, requests" 2>nul
if errorlevel 1 (
    echo ⚠️  检测到缺失依赖，正在自动安装...
    echo 📦 安装核心依赖包...
    python -m pip install streamlit fastapi uvicorn requests python-dotenv pydantic aiofiles
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
)

:: 启动应用
echo.
echo 🚀 启动 AIMovie 应用...
echo 🌐 应用将在浏览器中打开: http://localhost:8501
echo 📚 API文档地址: http://localhost:8000/docs
echo 按 Ctrl+C 停止应用
echo.

python start.py

echo.
echo 👋 应用已停止
pause
