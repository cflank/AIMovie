@echo off
chcp 65001 >nul
cd /d "D:\src\AIMovie"
echo 📁 当前目录: %CD%
echo 🔍 检查启动文件...
if exist "start.py" (
    echo ✅ 找到 start.py
    call aimovie_env\Scripts\activate.bat
    echo 🚀 启动 start.py...
    python start.py
) else if exist "start_cloud.py" (
    echo ✅ 找到 start_cloud.py
    call aimovie_env\Scripts\activate.bat
    echo 🚀 启动 start_cloud.py...
    python start_cloud.py
) else if exist "main.py" (
    echo ✅ 找到 main.py
    call aimovie_env\Scripts\activate.bat
    echo 🚀 启动 main.py...
    python main.py
) else if exist "app.py" (
    echo ✅ 找到 app.py
    call aimovie_env\Scripts\activate.bat
    echo 🚀 启动 app.py...
    python app.py
) else (
    echo ❌ 未找到启动文件 (start.py, start_cloud.py, main.py, app.py)
    echo 📋 当前目录文件列表:
    dir *.py
    echo.
    echo 💡 请手动运行您的Python应用
    echo    例如: python your_app.py
)
echo.
echo 按任意键退出...
pause
