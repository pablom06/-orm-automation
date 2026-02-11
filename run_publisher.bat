@echo off
REM ============================================
REM ORM Automation - Windows Runner Script
REM ============================================
REM This script runs the publisher from Windows

cd /d "%~dp0"

echo.
echo ========================================
echo ORM Content Publisher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if dependencies are installed
if not exist "venv\" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Run the publisher
echo Running publisher...
python publish.py %*

echo.
echo Done!
pause
