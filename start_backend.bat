@echo off
cd /d "%~dp0"
echo ===================================================
echo   Starting Stego-Upscale AI Backend (FastAPI)
echo ===================================================

REM Check if .venv exists, create if not
if not exist ".venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check and install dependencies
echo [*] Checking dependencies in requirements.txt...
python -m pip install -r requirements.txt

echo.
echo ===================================================
echo   API Server:  http://localhost:8000
echo   Healthcheck: http://localhost:8000/health
echo   Swagger UI:  http://localhost:8000/docs
echo ===================================================
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
