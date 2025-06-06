@echo off
chcp 65001 >nul
title AIMovie 一键启动

echo.
echo 🎬 AIMovie 一键启动菜单
echo ==========================================
echo.
echo 请选择启动方式:
echo.
echo 1. 🚀 快速启动 (开发模式)
echo 2. 🏭 生产模式启动
echo 3. 🐳 Docker容器启动
echo 4. 🔧 Windows服务启动
echo 5. 🔍 环境检查
echo 6. 📋 查看日志
echo 7. 🛠️  配置管理
echo 8. ❌ 退出
echo.
set /p choice=请输入选择 (1-8): 

if "%choice%"=="1" goto dev_start
if "%choice%"=="2" goto prod_start
if "%choice%"=="3" goto docker_start
if "%choice%"=="4" goto service_start
if "%choice%"=="5" goto check_env
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto config_manage
if "%choice%"=="8" goto exit
goto invalid_choice

:dev_start
echo.
echo 🚀 启动开发环境...
echo ==========================================
cd /d "%~dp0"
if exist "aimovie_env\Scripts\activate.bat" (
    call aimovie_env\Scripts\activate.bat
    echo 🎬 AIMovie 开发环境
    echo ==========================================
    echo 💻 开发模式启动
    echo 🔗 前端: http://localhost:8501
    echo 🔗 API: http://127.0.0.1:8000/docs
    echo ==========================================
    python start.py
) else (
    echo ❌ 虚拟环境不存在，请先运行部署脚本
    echo 💡 运行: deploy_win11.bat
    pause
)
goto end

:prod_start
echo.
echo 🏭 启动生产环境...
echo ==========================================
cd /d "%~dp0"
if exist "aimovie_env\Scripts\activate.bat" (
    call aimovie_env\Scripts\activate.bat
    echo 🎬 AIMovie 生产环境
    echo ==========================================
    echo 🚀 生产模式启动
    echo 🔗 前端: http://localhost:8501
    echo 🔗 API: http://127.0.0.1:8000
    echo ==========================================
    set ENVIRONMENT=production
    python start.py
) else (
    echo ❌ 虚拟环境不存在，请先运行部署脚本
    pause
)
goto end

:docker_start
echo.
echo 🐳 Docker容器启动...
echo ==========================================
docker --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Docker已安装
    echo 🔍 检查Docker Compose...
    docker-compose --version >nul 2>&1
    if %errorLevel% == 0 (
        echo ✅ Docker Compose已安装
        echo 🚀 启动Docker容器...
        docker-compose up -d
        echo ✅ 容器启动完成
        echo 🌐 访问地址: http://localhost
        echo 📊 监控面板: http://localhost:3000
    ) else (
        echo ❌ Docker Compose未安装
        echo 💡 请安装Docker Desktop
    )
) else (
    echo ❌ Docker未安装
    echo 💡 请先安装Docker Desktop
)
pause
goto menu

:service_start
echo.
echo 🔧 Windows服务启动...
echo ==========================================
if exist "service_manager.bat" (
    call service_manager.bat
) else (
    echo ❌ 服务管理脚本不存在
    echo 💡 请先运行部署脚本创建服务
)
pause
goto menu

:check_env
echo.
echo 🔍 环境检查...
echo ==========================================
cd /d "%~dp0"
if exist "check_env.bat" (
    call check_env.bat
) else (
    echo 🐍 Python版本:
    python --version 2>nul || echo ❌ Python未安装
    echo.
    echo 📦 虚拟环境:
    if exist "aimovie_env" (
        echo ✅ 虚拟环境存在
    ) else (
        echo ❌ 虚拟环境不存在
    )
    echo.
    echo ⚙️  配置文件:
    if exist ".env" (
        echo ✅ 配置文件存在
    ) else (
        echo ❌ 配置文件不存在
    )
    echo.
    echo 🐳 Docker:
    docker --version 2>nul || echo ❌ Docker未安装
    echo.
    echo 🔧 Git:
    git --version 2>nul || echo ❌ Git未安装
)
pause
goto menu

:view_logs
echo.
echo 📋 查看日志...
echo ==========================================
echo 1. API日志
echo 2. 前端日志
echo 3. 错误日志
echo 4. 所有日志
echo.
set /p log_choice=请选择日志类型 (1-4): 

if "%log_choice%"=="1" (
    if exist "logs\api.log" (
        type logs\api.log | more
    ) else (
        echo ❌ API日志文件不存在
    )
)
if "%log_choice%"=="2" (
    if exist "logs\frontend.log" (
        type logs\frontend.log | more
    ) else (
        echo ❌ 前端日志文件不存在
    )
)
if "%log_choice%"=="3" (
    if exist "logs\error.log" (
        type logs\error.log | more
    ) else (
        echo ❌ 错误日志文件不存在
    )
)
if "%log_choice%"=="4" (
    echo === API日志 ===
    if exist "logs\api.log" type logs\api.log | more
    echo.
    echo === 前端日志 ===
    if exist "logs\frontend.log" type logs\frontend.log | more
    echo.
    echo === 错误日志 ===
    if exist "logs\error.log" type logs\error.log | more
)
pause
goto menu

:config_manage
echo.
echo 🛠️  配置管理...
echo ==========================================
echo 1. 编辑环境配置 (.env)
echo 2. 查看当前配置
echo 3. 重置配置文件
echo 4. 备份配置
echo.
set /p config_choice=请选择操作 (1-4): 

if "%config_choice%"=="1" (
    if exist ".env" (
        notepad .env
    ) else (
        echo ❌ 配置文件不存在
        echo 💡 请先运行部署脚本
    )
)
if "%config_choice%"=="2" (
    if exist ".env" (
        echo 当前配置:
        type .env
    ) else (
        echo ❌ 配置文件不存在
    )
)
if "%config_choice%"=="3" (
    echo ⚠️  这将重置所有配置，确定继续吗？
    set /p confirm=输入 Y 确认: 
    if /i "%confirm%"=="Y" (
        if exist ".env" del .env
        echo ✅ 配置文件已删除，请重新运行部署脚本
    )
)
if "%config_choice%"=="4" (
    if exist ".env" (
        copy .env .env.backup.%date:~0,4%%date:~5,2%%date:~8,2%
        echo ✅ 配置已备份到 .env.backup.%date:~0,4%%date:~5,2%%date:~8,2%
    ) else (
        echo ❌ 配置文件不存在
    )
)
pause
goto menu

:invalid_choice
echo.
echo ❌ 无效选择，请重新输入
pause
goto menu

:menu
cls
echo.
echo 🎬 AIMovie 一键启动菜单
echo ==========================================
echo.
echo 请选择启动方式:
echo.
echo 1. 🚀 快速启动 (开发模式)
echo 2. 🏭 生产模式启动
echo 3. 🐳 Docker容器启动
echo 4. 🔧 Windows服务启动
echo 5. 🔍 环境检查
echo 6. 📋 查看日志
echo 7. 🛠️  配置管理
echo 8. ❌ 退出
echo.
set /p choice=请输入选择 (1-8): 

if "%choice%"=="1" goto dev_start
if "%choice%"=="2" goto prod_start
if "%choice%"=="3" goto docker_start
if "%choice%"=="4" goto service_start
if "%choice%"=="5" goto check_env
if "%choice%"=="6" goto view_logs
if "%choice%"=="7" goto config_manage
if "%choice%"=="8" goto exit
goto invalid_choice

:exit
echo.
echo 👋 感谢使用 AIMovie！
echo.
exit /b 0

:end
pause 