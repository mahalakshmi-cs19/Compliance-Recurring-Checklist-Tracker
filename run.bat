@echo off
title Compliance & Recurring Checklist Tracker
echo ================================================================
echo   Starting Compliance & Recurring Checklist Tracker
echo ================================================================

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Setting up venv...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Initialize and seed database if not present
if not exist "compliance.db" (
    echo [INFO] Initializing database and demo compliance data...
    python seed_data.py
)

echo [INFO] Starting web server on http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000
python app.py

pause
