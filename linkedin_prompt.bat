@echo off
REM ============================================
REM LinkedIn Publisher - Daily Prompt
REM ============================================

cd /d "%~dp0"

if not exist "venv\" (
    call setup.bat
)

call venv\Scripts\activate.bat

echo.
echo ========================================
echo LinkedIn Publisher - Daily Check
echo ========================================
echo.

python publish_linkedin.py

pause
