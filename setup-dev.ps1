# PowerShell script to set up the development environment on Windows

Write-Host "Setting up Churn Analysis development environment..." -ForegroundColor Green

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js is not installed. Please install Node.js 18+ and try again." -ForegroundColor Red
    exit 1
}

# Check if pnpm is installed
if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    Write-Host "Installing pnpm..." -ForegroundColor Yellow
    npm install -g pnpm
}

Write-Host "Setting up backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment and install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
pip install -r requirements.txt

Set-Location ..

Write-Host "Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
pnpm install

Set-Location ..

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "`nTo run the applications:" -ForegroundColor Cyan
Write-Host "1. Backend: cd backend && venv\Scripts\Activate.ps1 && uvicorn main:app --reload" -ForegroundColor White
Write-Host "2. Frontend: cd frontend && pnpm dev" -ForegroundColor White
Write-Host "`nBackend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
