@echo off
title LedgerDesk CA - Practice Operating System Launcher
color 0A
echo ===================================================
echo   LedgerDesk CA — Starting Backend & Frontend OS
echo ===================================================
echo.

cd /d "%~dp0backend"

echo Checking Python dependencies...
python -m pip install -r requirements.txt

echo.
echo Seeding initial database...
python -m app.seed

echo.
echo Starting FastAPI Uvicorn Server at http://localhost:8000 ...
python -m uvicorn app.main:app --reload --port 8000

pause
