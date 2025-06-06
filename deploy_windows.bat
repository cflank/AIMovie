@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🎬 AIMovie Cloud - Windows 一键部署
echo ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 管理员权限检查通过
) else (
    echo ❌ 需要管理员权限，请右键"以管理员身份运行"
    pause
    exit /b 1
)

:: 检查Python安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python已安装
    python --version
) else (
    echo ❌ Python未安装，正在安装Python 3.11...
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if %errorLevel% neq 0 (
        echo ❌ Python安装失败，请手动安装Python 3.8+
        pause
        exit /b 1
    )
    echo ✅ Python安装完成，请重新运行此脚本
    pause
    exit /b 0
)

:: 检查Git安装
echo 🔍 检查Git环境...
git --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Git已安装
    git --version
) else (
    echo ❌ Git未安装，正在安装Git...
    winget install Git.Git --accept-package-agreements --accept-source-agreements
    if %errorLevel% neq 0 (
        echo ❌ Git安装失败，请手动安装Git
        pause
        exit /b 1
    )
    echo ✅ Git安装完成
)

:: 设置项目目录
set PROJECT_DIR=%USERPROFILE%\AIMovie
echo 📁 项目将安装到: %PROJECT_DIR%

:: 克隆或更新项目
if exist "%PROJECT_DIR%" (
    echo 📂 项目目录已存在，正在更新...
    cd /d "%PROJECT_DIR%"
    git pull origin master
    if %errorLevel% neq 0 (
        echo ⚠️ 更新失败，将重新克隆项目
        cd /d "%USERPROFILE%"
        rmdir /s /q "%PROJECT_DIR%"
        git clone https://github.com/cflank/AIMovie.git
    )
) else (
    echo 📥 正在克隆项目...
    cd /d "%USERPROFILE%"
    git clone https://github.com/cflank/AIMovie.git
    if %errorLevel% neq 0 (
        echo ❌ 项目克隆失败，请检查网络连接
        pause
        exit /b 1
    )
)

cd /d "%PROJECT_DIR%"
echo ✅ 项目代码准备完成

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
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

:: 创建配置文件
echo ⚙️ 创建配置文件...
if not exist ".env" (
    copy env_template.txt .env
    echo ✅ 配置文件已创建: .env
    echo ⚠️ 请编辑 .env 文件，添加您的API密钥
) else (
    echo ✅ 配置文件已存在
)

:: 创建启动脚本
echo 📝 创建启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%PROJECT_DIR%"
echo call aimovie_env\Scripts\activate.bat
echo echo.
echo echo ========================================
echo echo 🎬 AIMovie Cloud 正在启动...
echo echo ========================================
echo echo.
echo echo 🌐 Web界面: http://127.0.0.1:8501
echo echo 🔧 API文档: http://127.0.0.1:8000/docs
echo echo.
echo python start.py
echo pause
) > "启动AIMovie.bat"

:: 创建桌面快捷方式
echo 🖥️ 创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\AIMovie Cloud.lnk'); $Shortcut.TargetPath = '%PROJECT_DIR%\启动AIMovie.bat'; $Shortcut.WorkingDirectory = '%PROJECT_DIR%'; $Shortcut.IconLocation = '%PROJECT_DIR%\启动AIMovie.bat'; $Shortcut.Save()"

:: 检查端口占用
echo 🔍 检查端口占用...
netstat -an | findstr ":8000" >nul
if %errorLevel% == 0 (
    echo ⚠️ 端口8000已被占用，请关闭占用该端口的程序
)

netstat -an | findstr ":8501" >nul
if %errorLevel% == 0 (
    echo ⚠️ 端口8501已被占用，请关闭占用该端口的程序
)

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
echo 🖥️ 桌面快捷方式已创建
echo.
echo 📋 下一步操作:
echo 1. 编辑配置文件: %PROJECT_DIR%\.env
echo 2. 添加至少一个LLM服务的API密钥
echo 3. 双击桌面的"AIMovie Cloud"快捷方式启动
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
    echo 💡 您可以稍后双击桌面的"AIMovie Cloud"快捷方式启动
)

echo.
echo 按任意键退出...
pause >nul 