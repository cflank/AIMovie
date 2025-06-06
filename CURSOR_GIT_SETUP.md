# 🔧 Cursor中Git配置指南

## 🎯 问题描述

在Cursor中使用终端时，经常遇到"git命令找不到"的问题，这通常是因为：
1. Git没有正确添加到系统PATH环境变量
2. Cursor使用的PowerShell会话没有加载正确的环境变量
3. Git安装时没有选择"添加到PATH"选项

## 🔍 问题诊断

### 检查Git是否已安装
```powershell
# 检查Git是否安装在默认位置
Test-Path "C:\Program Files\Git\bin\git.exe"

# 检查PATH中是否包含Git
$env:PATH -split ';' | Where-Object { $_ -like '*Git*' }

# 尝试直接运行Git
git --version
```

## 🛠️ 解决方案

### 方案一：临时解决（当前会话有效）

```powershell
# 添加Git到当前PowerShell会话的PATH
$env:PATH += ";C:\Program Files\Git\bin"

# 验证
git --version
```

### 方案二：永久解决（推荐）

#### 2.1 通过系统设置

1. **打开系统环境变量设置**
   - 按 `Win + R`，输入 `sysdm.cpl`
   - 点击"环境变量"按钮
   - 在"系统变量"中找到"Path"
   - 点击"编辑"

2. **添加Git路径**
   - 点击"新建"
   - 添加：`C:\Program Files\Git\bin`
   - 点击"确定"保存

3. **重启Cursor**
   - 关闭Cursor
   - 重新打开Cursor
   - 在终端中测试：`git --version`

#### 2.2 通过PowerShell（管理员权限）

```powershell
# 以管理员身份运行PowerShell，然后执行：
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Git\bin", [EnvironmentVariableTarget]::Machine)
```

#### 2.3 通过命令行（管理员权限）

```cmd
# 以管理员身份运行命令提示符，然后执行：
setx /M PATH "%PATH%;C:\Program Files\Git\bin"
```

### 方案三：Cursor特定配置

#### 3.1 配置Cursor的PowerShell配置文件

```powershell
# 检查PowerShell配置文件是否存在
Test-Path $PROFILE

# 如果不存在，创建配置文件
if (!(Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}

# 编辑配置文件，添加Git路径
Add-Content $PROFILE '$env:PATH += ";C:\Program Files\Git\bin"'
```

#### 3.2 配置Cursor设置

1. **打开Cursor设置**
   - 按 `Ctrl + ,`
   - 搜索 "terminal"

2. **配置终端环境**
   - 找到 "Terminal › Integrated › Env: Windows"
   - 添加环境变量：
     ```json
     {
         "PATH": "${env:PATH};C:\Program Files\Git\bin"
     }
     ```

#### 3.3 使用Cursor的Git集成

Cursor内置了Git支持，您也可以：
1. 使用Cursor的源代码管理面板（左侧边栏的分支图标）
2. 使用命令面板（`Ctrl + Shift + P`）搜索Git命令

## 🚀 快速修复脚本

创建一个批处理文件来快速修复Git路径问题：

### fix_git_path.bat
```batch
@echo off
echo 🔧 修复Cursor中的Git路径问题...

:: 检查Git是否已安装
if exist "C:\Program Files\Git\bin\git.exe" (
    echo ✅ Git已安装
) else (
    echo ❌ Git未安装，请先安装Git
    pause
    exit /b 1
)

:: 添加Git到用户PATH
for /f "usebackq tokens=2,*" %%A in (`reg query HKCU\Environment /v PATH 2^>nul`) do set "userpath=%%B"
if not defined userpath set "userpath="

echo %userpath% | findstr /C:"Git\bin" >nul
if %errorlevel% equ 0 (
    echo ✅ Git路径已存在于用户PATH中
) else (
    echo 📝 添加Git到用户PATH...
    setx PATH "%userpath%;C:\Program Files\Git\bin"
    echo ✅ Git路径已添加到用户PATH
)

echo.
echo 🎉 修复完成！请重启Cursor以使更改生效。
echo.
pause
```

### fix_git_path.ps1
```powershell
# PowerShell版本的修复脚本
Write-Host "🔧 修复Cursor中的Git路径问题..." -ForegroundColor Cyan

# 检查Git是否已安装
if (Test-Path "C:\Program Files\Git\bin\git.exe") {
    Write-Host "✅ Git已安装" -ForegroundColor Green
} else {
    Write-Host "❌ Git未安装，请先安装Git" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 获取当前用户PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)

# 检查Git路径是否已存在
if ($userPath -like "*Git\bin*") {
    Write-Host "✅ Git路径已存在于用户PATH中" -ForegroundColor Green
} else {
    Write-Host "📝 添加Git到用户PATH..." -ForegroundColor Yellow
    $newPath = $userPath + ";C:\Program Files\Git\bin"
    [Environment]::SetEnvironmentVariable("Path", $newPath, [EnvironmentVariableTarget]::User)
    Write-Host "✅ Git路径已添加到用户PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 修复完成！请重启Cursor以使更改生效。" -ForegroundColor Green
Write-Host ""
Read-Host "按任意键退出"
```

## 🔍 验证修复

修复后，在Cursor终端中运行以下命令验证：

```powershell
# 检查Git版本
git --version

# 检查Git配置
git config --list

# 测试Git命令
git status
```

## 🎯 Cursor特定的Git使用技巧

### 1. 使用Cursor的集成Git功能

- **源代码管理面板**: 点击左侧边栏的分支图标
- **命令面板**: `Ctrl + Shift + P` → 搜索"Git"
- **快捷键**:
  - `Ctrl + Shift + G`: 打开源代码管理
  - `Ctrl + K Ctrl + O`: 打开文件夹

### 2. 配置Git用户信息

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 常用Git命令

```bash
# 查看状态
git status

# 添加文件
git add .

# 提交更改
git commit -m "commit message"

# 推送到远程
git push origin main
```

## 🚨 常见问题

### Q1: 重启Cursor后Git又找不到了
**A**: 说明环境变量没有永久保存，请使用方案二的永久解决方法。

### Q2: 提示权限不足
**A**: 需要以管理员身份运行PowerShell或命令提示符。

### Q3: Git命令可用但Cursor的Git面板不工作
**A**: 尝试重启Cursor，或在设置中重新配置Git路径。

### Q4: 多个Git版本冲突
**A**: 确保PATH中只有一个Git路径，移除其他版本的路径。

## 📚 相关资源

- [Git官方下载](https://git-scm.com/download/windows)
- [Cursor官方文档](https://cursor.sh/docs)
- [PowerShell环境变量管理](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables)

---

**💡 提示**: 建议使用方案二的永久解决方法，这样就不需要每次都重新配置了。 