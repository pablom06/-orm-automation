@echo off
REM ============================================
REM ORM Automation - Daemon Mode
REM ============================================
REM This script runs the publisher in continuous daemon mode

cd /d "%~dp0"

echo.
echo ========================================
echo ORM Content Publisher - Daemon Mode
echo ========================================
echo This will run continuously and publish
echo at your scheduled time each day.
echo Press Ctrl+C to stop.
echo ========================================
echo.

if not exist "venv\" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Run in daemon mode
python publish.py --daemon
