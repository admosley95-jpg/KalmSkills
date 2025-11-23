# Backend Startup Script
# Run this to start just the Python FastAPI backend

Write-Host "🔧 Starting Backend Server..." -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\backend"

# Check if dependencies are installed
try {
    python -c "import fastapi, uvicorn" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Installing backend dependencies..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt
    }
} catch {
    Write-Host "⚠️  Installing backend dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
}

Write-Host "✅ Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Documentation available at http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
