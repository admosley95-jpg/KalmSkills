# Node.js Installation Script for Windows
# Run this script as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Node.js Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script needs Administrator privileges" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

Write-Host "Running with Administrator privileges" -ForegroundColor Green
Write-Host ""

# Check if Node.js is already installed
$nodeExists = Get-Command node -ErrorAction SilentlyContinue

if ($nodeExists) {
    Write-Host "Node.js is already installed!" -ForegroundColor Green
    node --version
    npm --version
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

# Try winget installation
Write-Host "Attempting to install Node.js via winget..." -ForegroundColor Cyan
$wingetExists = Get-Command winget -ErrorAction SilentlyContinue

if ($wingetExists) {
    winget install OpenJS.NodeJS.LTS --silent --accept-source-agreements --accept-package-agreements
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Node.js installed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "IMPORTANT: Close VS Code and reopen it" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit
    }
}

# Fallback: Download and install manually
Write-Host ""
Write-Host "Downloading Node.js installer..." -ForegroundColor Cyan

$nodeVersion = "20.10.0"
$installerUrl = "https://nodejs.org/dist/v$nodeVersion/node-v$nodeVersion-x64.msi"
$installerPath = "$env:TEMP\nodejs-installer.msi"

Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing

Write-Host "Download complete. Installing..." -ForegroundColor Green
Write-Host ""

$arguments = "/i `"$installerPath`" /quiet /norestart ADDLOCAL=ALL"
Start-Process msiexec.exe -ArgumentList $arguments -Wait -NoNewWindow

Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Close VS Code completely" -ForegroundColor White
Write-Host "2. Reopen VS Code" -ForegroundColor White
Write-Host "3. Run: node --version" -ForegroundColor White
Write-Host "4. Run: npm install" -ForegroundColor White
Write-Host "5. Run: npm run dev" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
