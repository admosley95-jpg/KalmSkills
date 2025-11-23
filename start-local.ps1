# Local Development Startup Script
# Starts both backend (Python/FastAPI) and frontend (React/Vite)

Write-Host "🚀 Starting KalmSkills Local Development Environment" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "📦 Starting Backend (FastAPI on port 8000)..." -ForegroundColor Cyan
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -PassThru

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "⚛️  Starting Frontend (React/Vite on port 5173)..." -ForegroundColor Cyan
$env:PATH = "C:\Program Files\nodejs;$env:PATH"
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev" -PassThru

Write-Host ""
Write-Host "✅ Services Started!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each terminal window to stop the services" -ForegroundColor Gray
