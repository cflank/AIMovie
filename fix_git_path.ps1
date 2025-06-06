# 🔧 Cursor Git路径修复脚本
# 用于解决Cursor中找不到Git命令的问题

param(
    [switch]$Permanent,  # 是否永久修复
    [switch]$CurrentSession  # 只修复当前会话
)

Write-Host "🔧 Cursor Git路径修复工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查Git是否已安装
$gitPaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
)

$gitPath = $null
foreach ($path in $gitPaths) {
    if (Test-Path $path) {
        $gitPath = Split-Path $path -Parent
        Write-Host "✅ 找到Git安装路径: $gitPath" -ForegroundColor Green
        break
    }
}

if (-not $gitPath) {
    Write-Host "❌ 未找到Git安装，请先安装Git" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/windows" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}

# 检查当前PATH中是否已包含Git
$currentPath = $env:PATH
if ($currentPath -like "*$gitPath*") {
    Write-Host "✅ Git路径已存在于当前会话PATH中" -ForegroundColor Green
    
    # 测试Git命令
    try {
        $gitVersion = git --version 2>$null
        Write-Host "✅ Git命令可用: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Git路径存在但命令不可用" -ForegroundColor Yellow
    }
} else {
    Write-Host "📝 添加Git到当前会话PATH..." -ForegroundColor Yellow
    $env:PATH += ";$gitPath"
    Write-Host "✅ Git已添加到当前会话PATH" -ForegroundColor Green
}

# 如果指定了永久修复
if ($Permanent) {
    Write-Host ""
    Write-Host "🔄 执行永久修复..." -ForegroundColor Cyan
    
    try {
        # 获取用户环境变量PATH
        $userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
        
        if ($userPath -like "*$gitPath*") {
            Write-Host "✅ Git路径已存在于用户环境变量中" -ForegroundColor Green
        } else {
            Write-Host "📝 添加Git到用户环境变量..." -ForegroundColor Yellow
            $newUserPath = if ($userPath) { "$userPath;$gitPath" } else { $gitPath }
            [Environment]::SetEnvironmentVariable("Path", $newUserPath, [EnvironmentVariableTarget]::User)
            Write-Host "✅ Git已添加到用户环境变量" -ForegroundColor Green
        }
        
        # 检查系统环境变量（需要管理员权限）
        try {
            $systemPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
            if ($systemPath -like "*$gitPath*") {
                Write-Host "✅ Git路径已存在于系统环境变量中" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Git不在系统环境变量中，建议以管理员身份运行此脚本" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️ 无法检查系统环境变量（需要管理员权限）" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "❌ 永久修复失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 测试Git功能
Write-Host ""
Write-Host "🧪 测试Git功能..." -ForegroundColor Cyan

try {
    $gitVersion = git --version
    Write-Host "✅ Git版本: $gitVersion" -ForegroundColor Green
    
    # 检查Git配置
    $userName = git config --global user.name 2>$null
    $userEmail = git config --global user.email 2>$null
    
    if ($userName -and $userEmail) {
        Write-Host "✅ Git用户配置: $userName <$userEmail>" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Git用户信息未配置" -ForegroundColor Yellow
        Write-Host "建议运行以下命令配置:" -ForegroundColor Yellow
        Write-Host "  git config --global user.name `"Your Name`"" -ForegroundColor Gray
        Write-Host "  git config --global user.email `"your.email@example.com`"" -ForegroundColor Gray
    }
    
    # 如果在Git仓库中，显示状态
    if (Test-Path ".git") {
        Write-Host "📁 当前目录是Git仓库" -ForegroundColor Green
        try {
            $gitStatus = git status --porcelain 2>$null
            if ($gitStatus) {
                Write-Host "📝 有未提交的更改" -ForegroundColor Yellow
            } else {
                Write-Host "✅ 工作目录干净" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️ 无法获取Git状态" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Git命令测试失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 显示Cursor特定建议
Write-Host ""
Write-Host "💡 Cursor使用建议:" -ForegroundColor Cyan
Write-Host "1. 重启Cursor以确保环境变量生效" -ForegroundColor Gray
Write-Host "2. 使用Ctrl+Shift+G打开源代码管理面板" -ForegroundColor Gray
Write-Host "3. 使用Ctrl+Shift+P搜索Git命令" -ForegroundColor Gray
Write-Host "4. 如果问题持续，请检查Cursor设置中的终端配置" -ForegroundColor Gray

# 创建Cursor配置建议
Write-Host ""
Write-Host "🔧 Cursor配置建议:" -ForegroundColor Cyan
Write-Host "在Cursor设置中添加以下环境变量配置:" -ForegroundColor Gray
Write-Host @"
{
    "terminal.integrated.env.windows": {
        "PATH": "`${env:PATH};$gitPath"
    }
}
"@ -ForegroundColor DarkGray

Write-Host ""
if ($Permanent) {
    Write-Host "🎉 修复完成！请重启Cursor以使更改完全生效。" -ForegroundColor Green
} else {
    Write-Host "🎉 当前会话修复完成！" -ForegroundColor Green
    Write-Host "💡 要永久修复，请运行: .\fix_git_path.ps1 -Permanent" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "按任意键退出" 