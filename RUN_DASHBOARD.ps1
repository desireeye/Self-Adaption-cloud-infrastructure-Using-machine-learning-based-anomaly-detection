# Complete Dashboard Setup and Integration Script
# This script installs dependencies and starts both backend and frontend

param(
    [switch]$SkipInstall = $false,
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false
)

$projectRoot = "C:\Users\arzoo\OneDrive\Desktop\self-adaptive project"
$backendDir = "$projectRoot\dashboard\backend"
$frontendDir = "$projectRoot\dashboard\frontend"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Self-Adaptive Dashboard - Setup & Integration          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Function to start backend
function Start-Backend {
    Write-Host "`n🔧 Starting Backend API Server..." -ForegroundColor Yellow
    Write-Host "📍 Location: $backendDir" -ForegroundColor Gray
    Write-Host "📡 Port: 8000" -ForegroundColor Gray
    Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    
    Set-Location $backendDir
    
    if (-not $SkipInstall) {
        Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
        pip install -q -r requirements_clean.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "`n🚀 Launching FastAPI server..." -ForegroundColor Green
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to start frontend
function Start-Frontend {
    Write-Host "`n🎨 Starting Frontend Dashboard..." -ForegroundColor Yellow
    Write-Host "📍 Location: $frontendDir" -ForegroundColor Gray
    Write-Host "🌐 Port: 3000" -ForegroundColor Gray
    Write-Host "📱 URL: http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    
    Set-Location $frontendDir
    
    if (-not $SkipInstall) {
        Write-Host "📦 Installing Node dependencies..." -ForegroundColor Cyan
        npm install --silent
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install Node dependencies" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    }
    
    Write-Host "`n🚀 Starting React development server..." -ForegroundColor Green
    npm start
}

# Main execution
Write-Host "`n📋 Configuration:" -ForegroundColor Cyan
Write-Host "  Backend: $backendDir"
Write-Host "  Frontend: $frontendDir"
Write-Host ""

if ($BackendOnly) {
    Start-Backend
} elseif ($FrontendOnly) {
    Start-Frontend
} else {
    Write-Host "⚠️  For full dashboard experience, run in TWO separate PowerShell terminals:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Terminal 1 - Backend:" -ForegroundColor Cyan
    Write-Host "  cd `"$backendDir`""
    Write-Host "  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    Write-Host ""
    Write-Host "Terminal 2 - Frontend:" -ForegroundColor Cyan
    Write-Host "  cd `"$frontendDir`""
    Write-Host "  npm install"
    Write-Host "  npm start"
    Write-Host ""
    Write-Host "Then access: http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    Write-Host "Or run this script with flags:" -ForegroundColor Yellow
    Write-Host "  .\RUN_DASHBOARD.ps1 -BackendOnly"
    Write-Host "  .\RUN_DASHBOARD.ps1 -FrontendOnly"
    Write-Host "  .\RUN_DASHBOARD.ps1 -SkipInstall"
}
