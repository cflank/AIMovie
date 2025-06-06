@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎬 AIMovie 一键部署                        ║
echo ║                AI视频解说生成器 - 云端版                      ║
echo ║                                                              ║
echo ║  🌟 支持多种大模型组合                                        ║
echo ║  💰 成本透明，按需付费                                        ║
echo ║  🚀 无需GPU，云端处理                                         ║
echo ║                                                              ║
echo ║  Version: 2.0.0 Final                                       ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 设置项目目录为当前目录
set "PROJECT_DIR=%CD%"
echo 📁 项目目录: %PROJECT_DIR%

:: 检查Python环境
echo.
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

:: 检查pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip未安装，请检查Python安装
    pause
    exit /b 1
)
echo ✅ pip已安装

:: 创建虚拟环境
echo.
echo 🔧 创建虚拟环境...
set "VENV_DIR=%PROJECT_DIR%\aimovie_env"

if exist "%VENV_DIR%" (
    echo ⚠️  虚拟环境已存在，是否重新创建？
    choice /c YN /m "重新创建虚拟环境 (Y/N)"
    if !errorlevel! equ 1 (
        echo 🗑️  删除旧环境...
        rmdir /s /q "%VENV_DIR%"
    ) else (
        echo ✅ 使用现有虚拟环境
        goto :activate_env
    )
)

echo 📦 创建新的虚拟环境...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo ❌ 虚拟环境创建失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境创建成功

:activate_env
:: 激活虚拟环境
echo.
echo 🔄 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ 虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境已激活

:: 升级pip
echo.
echo 📈 升级pip...
python -m pip install --upgrade pip
echo ✅ pip升级完成

:: 安装依赖
echo.
echo 📦 安装项目依赖...

:: 选择依赖文件
set "REQ_FILE="
if exist "requirements_cloud_minimal.txt" (
    set "REQ_FILE=requirements_cloud_minimal.txt"
    echo 📋 使用最小化依赖: %REQ_FILE%
) else if exist "requirements_cloud.txt" (
    set "REQ_FILE=requirements_cloud.txt"
    echo 📋 使用云端依赖: %REQ_FILE%
) else if exist "requirements.txt" (
    set "REQ_FILE=requirements.txt"
    echo 📋 使用标准依赖: %REQ_FILE%
) else (
    echo ⚠️  未找到依赖文件，手动安装核心包...
    goto :manual_install
)

:: 安装依赖文件
echo 🔄 安装依赖包...
python -m pip install -r "%REQ_FILE%"
if errorlevel 1 (
    echo ⚠️  依赖安装失败，尝试手动安装核心包...
    goto :manual_install
) else (
    echo ✅ 依赖安装成功
    goto :install_ai_services
)

:manual_install
echo 🔧 手动安装核心依赖...
set "CORE_PACKAGES=fastapi uvicorn streamlit requests python-dotenv pydantic aiofiles"
for %%p in (%CORE_PACKAGES%) do (
    echo   安装 %%p...
    python -m pip install %%p
)
echo ✅ 核心依赖安装完成

:install_ai_services
echo.
echo 🤖 安装AI服务SDK...
echo 💡 根据需要选择安装的服务SDK:
echo    1. 全部安装 (推荐)
echo    2. 仅安装基础服务
echo    3. 跳过AI服务安装
choice /c 123 /m "请选择"

if !errorlevel! equ 1 (
    echo 📦 安装所有AI服务SDK...
    set "AI_PACKAGES=dashscope baidu-aip openai anthropic zhipuai azure-cognitiveservices-speech tencentcloud-sdk-python"
    for %%p in (!AI_PACKAGES!) do (
        echo   安装 %%p...
        python -m pip install %%p
    )
    echo ✅ AI服务SDK安装完成
) else if !errorlevel! equ 2 (
    echo 📦 安装基础AI服务SDK...
    set "BASIC_AI=dashscope baidu-aip"
    for %%p in (!BASIC_AI!) do (
        echo   安装 %%p...
        python -m pip install %%p
    )
    echo ✅ 基础AI服务SDK安装完成
) else (
    echo ⏭️  跳过AI服务SDK安装
)

:: 创建必要目录
echo.
echo 📁 创建项目目录...
for %%d in (logs temp uploads outputs cache) do (
    if not exist "%%d" mkdir "%%d"
)
echo ✅ 目录结构创建完成

:: 创建配置文件
echo.
echo ⚙️  创建配置文件...
if not exist ".env" (
    if exist "env_template.txt" (
        copy "env_template.txt" ".env" >nul
        echo ✅ 已从模板创建.env配置文件
    ) else (
        echo # AIMovie 基础配置 > .env
        echo DEBUG=false >> .env
        echo API_HOST=127.0.0.1 >> .env
        echo API_PORT=8000 >> .env
        echo STREAMLIT_PORT=8501 >> .env
        echo LOG_LEVEL=INFO >> .env
        echo. >> .env
        echo # 预设配置 ^(选择其中一种^) >> .env
        echo PRESET_CONFIG=cost_effective >> .env
        echo. >> .env
        echo # 通义千问 API ^(推荐^) >> .env
        echo QWEN_API_KEY=your_qwen_api_key_here >> .env
        echo ✅ 已创建基础.env配置文件
    )
) else (
    echo ✅ 配置文件已存在
)

:: 创建启动脚本
echo.
echo 🚀 创建启动脚本...

:: 创建主启动脚本
echo @echo off > "启动AIMovie.bat"
echo chcp 65001 ^>nul >> "启动AIMovie.bat"
echo cd /d "%PROJECT_DIR%" >> "启动AIMovie.bat"
echo call "%VENV_DIR%\Scripts\activate.bat" >> "启动AIMovie.bat"
echo echo 🎬 启动AIMovie应用... >> "启动AIMovie.bat"
echo python start_cloud.py >> "启动AIMovie.bat"
echo pause >> "启动AIMovie.bat"

:: 创建Streamlit直接启动脚本
echo @echo off > "启动前端界面.bat"
echo chcp 65001 ^>nul >> "启动前端界面.bat"
echo cd /d "%PROJECT_DIR%" >> "启动前端界面.bat"
echo call "%VENV_DIR%\Scripts\activate.bat" >> "启动前端界面.bat"
echo echo 🎨 启动前端界面... >> "启动前端界面.bat"
echo python -m streamlit run frontend/cloud_streamlit_app.py --server.port 8501 >> "启动前端界面.bat"
echo pause >> "启动前端界面.bat"

:: 创建环境激活脚本
echo @echo off > "进入环境.bat"
echo chcp 65001 ^>nul >> "进入环境.bat"
echo cd /d "%PROJECT_DIR%" >> "进入环境.bat"
echo call "%VENV_DIR%\Scripts\activate.bat" >> "进入环境.bat"
echo echo ✅ 已进入AIMovie虚拟环境 >> "进入环境.bat"
echo echo 💡 可以运行以下命令: >> "进入环境.bat"
echo echo    python start_cloud.py          - 启动完整应用 >> "进入环境.bat"
echo echo    streamlit run frontend/cloud_streamlit_app.py - 仅启动前端 >> "进入环境.bat"
echo cmd /k >> "进入环境.bat"

echo ✅ 启动脚本创建完成

:: 验证安装
echo.
echo 🔍 验证安装...
python -c "import streamlit, fastapi, requests; print('✅ 核心依赖验证通过')" 2>nul
if errorlevel 1 (
    echo ⚠️  核心依赖验证失败，但可以尝试启动
) else (
    echo ✅ 核心依赖验证通过
)

:: 显示配置信息
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎉 部署完成                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 📋 下一步操作:
echo.
echo 1️⃣  配置API密钥:
echo    📝 编辑 .env 文件，填入您的API密钥
echo    💡 最简配置: 只需填入 QWEN_API_KEY
echo.
echo 2️⃣  启动应用:
echo    🚀 双击 "启动AIMovie.bat" - 完整应用
echo    🎨 双击 "启动前端界面.bat" - 仅前端界面
echo    🔧 双击 "进入环境.bat" - 进入开发环境
echo.
echo 3️⃣  访问地址:
echo    🌐 前端界面: http://localhost:8501
echo    📚 API文档: http://localhost:8000/docs
echo.
echo 💰 推荐配置组合:
echo    🏆 最高性价比: 通义千问 + 阿里云TTS + 百度AI
echo    💎 质量最高: GPT-4 + Azure TTS + GPT-4V  
echo    💰 最经济: 文心一言 + Edge-TTS + 百度AI
echo.
echo 📖 详细文档: SUPPORTED_MODELS.md
echo 🆘 问题反馈: https://github.com/cflank/AIMovie/issues
echo.

:: 询问是否立即进入环境
choice /c YN /m "是否立即进入虚拟环境"
if !errorlevel! equ 1 (
    echo.
    echo 🔄 进入虚拟环境...
    call "%VENV_DIR%\Scripts\activate.bat"
    echo ✅ 已进入AIMovie虚拟环境
    echo 💡 运行 python start_cloud.py 启动应用
    cmd /k
) else (
    echo.
    echo 👋 部署完成！请按照上述步骤配置和启动应用。
    pause
)

endlocal 