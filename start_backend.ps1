# Stego-Upscale AI - PowerShell Virtual Environment Launcher
Set-Location -Path $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting Stego-Upscale AI Backend (FastAPI)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# 1. Create .venv if not found
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Failed to create .venv. Check Python installation." -ForegroundColor Red
        Exit
    }
}

# 2. Activate virtual environment
$ActivateScript = ".venv\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    .venv\Scripts\activate.bat
}

# 3. Install requirements
Write-Host "[*] Verifying dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Start FastAPI server
Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  API Server:  http://localhost:8000" -ForegroundColor Green
Write-Host "  Healthcheck: http://localhost:8000/health" -ForegroundColor Green
Write-Host "  Swagger UI:  http://localhost:8000/docs" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
