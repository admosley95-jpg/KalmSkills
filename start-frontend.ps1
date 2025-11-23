# Frontend Startup Script
# Run this to start just the React/Vite frontend

Write-Host "⚛️  Starting Frontend Development Server..." -ForegroundColor Cyan
Write-Host ""

# Ensure Node.js is in PATH
$env:PATH = "C:\Program Files\nodejs;$env:PATH"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "✅ Starting Vite development server on http://localhost:5173" -ForegroundColor Green
Write-Host ""

npm run dev
