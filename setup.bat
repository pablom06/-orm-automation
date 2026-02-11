@echo off
REM ============================================
REM ORM Automation - Initial Setup
REM ============================================

cd /d "%~dp0"

echo.
echo ========================================
echo ORM Content Publisher - Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your MEDIUM_TOKEN
echo 2. Run: run_publisher.bat --dry-run (to test)
echo 3. Run: run_publisher.bat (to publish)
echo.
echo For automated daily publishing:
echo   - Option A: Run run_daemon.bat (keeps window open)
echo   - Option B: Set up Windows Task Scheduler (see DEPLOYMENT.md)
echo   - Option C: Use GitHub Actions (see DEPLOYMENT.md)
echo.
pause
