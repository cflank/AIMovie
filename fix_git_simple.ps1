# Git Path Fix for Cursor
Write-Host "Fixing Git Path for Cursor..." -ForegroundColor Green

# Check if Git is installed
$gitExe = "C:\Program Files\Git\bin\git.exe"
if (Test-Path $gitExe) {
    Write-Host "Git found at: $gitExe" -ForegroundColor Green
    
    # Add to current session PATH
    $gitBin = "C:\Program Files\Git\bin"
    if ($env:PATH -notlike "*$gitBin*") {
        $env:PATH += ";$gitBin"
        Write-Host "Git added to current session PATH" -ForegroundColor Yellow
    }
    
    # Test Git command
    try {
        $version = git --version
        Write-Host "Git is working: $version" -ForegroundColor Green
    } catch {
        Write-Host "Git command failed" -ForegroundColor Red
    }
    
    # Add to user environment permanently
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$gitBin*") {
        $newPath = if ($userPath) { "$userPath;$gitBin" } else { $gitBin }
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "Git added to user environment variables" -ForegroundColor Green
        Write-Host "Please restart Cursor for permanent effect" -ForegroundColor Yellow
    } else {
        Write-Host "Git already in user PATH" -ForegroundColor Green
    }
    
} else {
    Write-Host "Git not found. Please install Git first." -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/windows" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Cursor Git Setup Tips:" -ForegroundColor Cyan
Write-Host "1. Restart Cursor after running this script" -ForegroundColor Gray
Write-Host "2. Use Ctrl+Shift+G for Git panel" -ForegroundColor Gray
Write-Host "3. Use Ctrl+Shift+P to search Git commands" -ForegroundColor Gray
Write-Host "" 