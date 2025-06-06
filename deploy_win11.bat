@echo off
chcp 65001 >nul
echo.
echo 🚀 AIMovie Windows 11 开发环境自动化部署
echo ==========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ 管理员权限已获取
) else (
    echo ❌ 需要管理员权限，请右键"以管理员身份运行"
    pause
    exit /b 1
)

:: 设置变量
set PROJECT_NAME=AIMovie
set VENV_NAME=aimovie_env
set PYTHON_VERSION=3.10
set PROJECT_DIR=%~dp0

echo 📍 项目目录: %PROJECT_DIR%
echo.

:: 检查Python安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python已安装
    python --version
) else (
    echo ❌ Python未安装，正在下载安装...
    echo 📥 下载Python %PYTHON_VERSION%...
    
    :: 创建临时目录
    if not exist "%TEMP%\aimovie_setup" mkdir "%TEMP%\aimovie_setup"
    cd /d "%TEMP%\aimovie_setup"
    
    :: 下载Python安装包
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile 'python-installer.exe'"
    
    if exist "python-installer.exe" (
        echo 🔧 安装Python...
        python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        echo ✅ Python安装完成
        
        :: 刷新环境变量
        call refreshenv
    ) else (
        echo ❌ Python下载失败，请手动安装Python 3.10+
        pause
        exit /b 1
    )
    
    cd /d "%PROJECT_DIR%"
)

:: 检查Git安装
echo.
echo 🔍 检查Git环境...
git --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Git已安装
    git --version
) else (
    echo ❌ Git未安装，正在下载安装...
    echo 📥 下载Git...
    
    cd /d "%TEMP%\aimovie_setup"
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git-installer.exe'"
    
    if exist "git-installer.exe" (
        echo 🔧 安装Git...
        git-installer.exe /VERYSILENT /NORESTART
        echo ✅ Git安装完成
        
        :: 刷新环境变量
        call refreshenv
    ) else (
        echo ❌ Git下载失败，请手动安装Git
        pause
        exit /b 1
    )
    
    cd /d "%PROJECT_DIR%"
)

:: 检查Node.js (可选，用于某些工具)
echo.
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Node.js已安装
    node --version
) else (
    echo ⚠️  Node.js未安装 (可选组件)
    echo 💡 如需完整功能，建议安装Node.js
)

:: 创建虚拟环境
echo.
echo 🏗️  创建Python虚拟环境...
if exist "%VENV_NAME%" (
    echo ⚠️  虚拟环境已存在，正在重新创建...
    rmdir /s /q "%VENV_NAME%"
)

python -m venv %VENV_NAME%
if %errorLevel% == 0 (
    echo ✅ 虚拟环境创建成功
) else (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)

:: 激活虚拟环境
echo.
echo 🔄 激活虚拟环境...
call %VENV_NAME%\Scripts\activate.bat

:: 升级pip
echo.
echo 📦 升级pip...
python -m pip install --upgrade pip

:: 安装依赖包
echo.
echo 📦 安装项目依赖...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo ✅ 依赖安装成功
    ) else (
        echo ⚠️  部分依赖安装失败，尝试安装核心包...
        pip install fastapi uvicorn streamlit requests opencv-python python-dotenv pydantic aiofiles
    )
) else (
    echo ⚠️  requirements.txt不存在，安装核心包...
    pip install fastapi uvicorn streamlit requests opencv-python python-dotenv pydantic aiofiles
)

:: 创建必要目录
echo.
echo 📁 创建项目目录...
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs
echo ✅ 目录创建完成

:: 检查配置文件
echo.
echo ⚙️  检查配置文件...
if exist ".env" (
    echo ✅ 配置文件已存在
) else (
    echo ⚠️  配置文件不存在
    echo 💡 请确保.env文件包含必要的API密钥
    echo 📝 参考env.example文件进行配置
)

:: 创建Windows服务注册脚本
echo.
echo 🔧 创建Windows服务脚本...
(
echo @echo off
echo :: AIMovie Windows服务管理
echo echo 🔧 AIMovie服务管理
echo echo 1. 安装服务
echo echo 2. 启动服务  
echo echo 3. 停止服务
echo echo 4. 卸载服务
echo set /p choice=请选择操作 ^(1-4^): 
echo.
echo if "%%choice%%"=="1" goto install
echo if "%%choice%%"=="2" goto start
echo if "%%choice%%"=="3" goto stop  
echo if "%%choice%%"=="4" goto uninstall
echo goto end
echo.
echo :install
echo echo 📦 安装AIMovie服务...
echo sc create "AIMovie" binPath= "%%~dp0start_service.bat" start= auto
echo echo ✅ 服务安装完成
echo goto end
echo.
echo :start
echo echo 🚀 启动AIMovie服务...
echo sc start "AIMovie"
echo goto end
echo.
echo :stop
echo echo ⏹️  停止AIMovie服务...
echo sc stop "AIMovie"
echo goto end
echo.
echo :uninstall
echo echo 🗑️  卸载AIMovie服务...
echo sc delete "AIMovie"
echo goto end
echo.
echo :end
echo pause
) > service_manager.bat

:: 创建开发环境启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo call %VENV_NAME%\Scripts\activate.bat
echo echo 🎬 AIMovie 开发环境
echo echo ==========================================
echo echo 💻 开发模式启动
echo echo 🔗 前端: http://localhost:8501
echo echo 🔗 API: http://127.0.0.1:8000/docs
echo echo ==========================================
echo python start.py
echo pause
) > start_dev.bat

:: 创建生产环境启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo cd /d "%%~dp0"
echo call %VENV_NAME%\Scripts\activate.bat
echo echo 🎬 AIMovie 生产环境
echo echo ==========================================
echo echo 🚀 生产模式启动
echo echo 🔗 前端: http://localhost:8501
echo echo 🔗 API: http://127.0.0.1:8000
echo echo ==========================================
echo set ENVIRONMENT=production
echo python start.py
) > start_prod.bat

:: 创建更新脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🔄 更新AIMovie项目
echo echo ==========================================
echo cd /d "%%~dp0"
echo call %VENV_NAME%\Scripts\activate.bat
echo echo 📥 拉取最新代码...
echo git pull origin main
echo echo 📦 更新依赖包...
echo pip install -r requirements.txt --upgrade
echo echo ✅ 更新完成
echo pause
) > update.bat

:: 创建环境检查脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🔍 AIMovie 环境检查
echo echo ==========================================
echo cd /d "%%~dp0"
echo call %VENV_NAME%\Scripts\activate.bat
echo echo 🐍 Python版本:
echo python --version
echo echo.
echo echo 📦 已安装包:
echo pip list
echo echo.
echo echo ⚙️  配置检查:
echo python -c "from src.config.cloud_settings import get_cloud_settings; settings = get_cloud_settings(); print('✅ 配置加载成功')"
echo echo.
echo echo 🌐 网络连接测试:
echo python -c "import requests; r=requests.get('https://www.baidu.com', timeout=5); print('✅ 网络连接正常' if r.status_code==200 else '❌ 网络连接异常')"
echo pause
) > check_env.bat

:: 创建清理脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo 🧹 清理AIMovie临时文件
echo echo ==========================================
echo cd /d "%%~dp0"
echo echo 🗑️  清理临时文件...
echo if exist "temp" rmdir /s /q temp
echo if exist "uploads" rmdir /s /q uploads  
echo if exist "outputs" rmdir /s /q outputs
echo if exist "__pycache__" rmdir /s /q __pycache__
echo for /r . %%%%i in ^(__pycache__^) do if exist "%%%%i" rmdir /s /q "%%%%i"
echo for /r . %%%%i in ^(*.pyc^) do if exist "%%%%i" del "%%%%i"
echo echo 📁 重新创建目录...
echo mkdir temp uploads outputs logs
echo echo ✅ 清理完成
echo pause
) > cleanup.bat

:: 测试安装
echo.
echo 🧪 测试安装...
python -c "import fastapi, streamlit; print('✅ 核心包导入成功')" 2>nul
if %errorLevel% == 0 (
    echo ✅ 安装测试通过
) else (
    echo ❌ 安装测试失败，请检查依赖
)

:: 完成部署
echo.
echo ==========================================
echo 🎉 Windows 11 开发环境部署完成！
echo ==========================================
echo.
echo 📋 可用脚本:
echo   🚀 start_dev.bat     - 开发环境启动
echo   🏭 start_prod.bat    - 生产环境启动  
echo   🔧 service_manager.bat - Windows服务管理
echo   🔄 update.bat        - 更新项目
echo   🔍 check_env.bat     - 环境检查
echo   🧹 cleanup.bat       - 清理临时文件
echo.
echo 📝 下一步:
echo   1. 配置.env文件中的API密钥
echo   2. 运行 start_dev.bat 启动开发环境
echo   3. 访问 http://localhost:8501 使用应用
echo.
echo 💡 提示: 
echo   - 开发环境: 使用 start_dev.bat
echo   - 生产环境: 使用 start_prod.bat  
echo   - Windows服务: 使用 service_manager.bat
echo.
pause 