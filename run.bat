@echo off
title Adaptive Security Framework
echo ========================================================
echo Starting Adaptive Security Framework Command Center...
echo ========================================================
echo.

cd /d "%~dp0"
set PYTHONPATH=%cd%
set PATH=C:\Users\Acer\AppData\Local\Programs\nodejs;%PATH%

echo [1/2] Checking Python and packages...
python -c "import fastapi, uvicorn, websockets, pydantic" 2>nul
if %errorlevel% neq 0 (
    echo Installing backend dependencies...
    python -m pip install -r backend\requirements.txt
)

echo [2/2] Launching backend server (http://localhost:8000)...
start http://localhost:8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
pause
