@echo off
REM ============================================
REM Deploy ORM Automation to GitHub
REM ============================================

echo.
echo ========================================
echo Deploy ORM Automation to GitHub
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

echo Step 1: Initialize Git repository...
git init

echo.
echo Step 2: Add all files...
git add .

echo.
echo Step 3: Create initial commit...
git commit -m "Initial commit - ORM automation system with 4-platform publishing"

echo.
echo Step 4: Set main branch...
git branch -M main

echo.
echo ========================================
echo MANUAL STEPS REQUIRED:
echo ========================================
echo.
echo 1. Go to: https://github.com/new
echo 2. Create a new repository named: orm-automation
echo 3. Leave it public (for free GitHub Actions)
echo 4. DO NOT initialize with README
echo 5. Click "Create repository"
echo.
echo Then come back here and press any key...
pause

echo.
set /p GITHUB_USERNAME="Enter your GitHub username: "
set REPO_URL=https://github.com/%GITHUB_USERNAME%/orm-automation.git

echo.
echo Connecting to: %REPO_URL%
git remote add origin %REPO_URL%

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo SUCCESS! Repository pushed to GitHub
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Go to: https://github.com/%GITHUB_USERNAME%/orm-automation/settings/secrets/actions
echo.
echo 2. Click "New repository secret" and add:
echo.
echo    Name: DEVTO_TOKEN
echo    Value: gnTMhr7HFwivsbsJiwC9Vfsd
echo.
echo    Name: HASHNODE_TOKEN
echo    Value: 9374311b-2f4f-4107-868a-37562a319f5f
echo.
echo    Name: HASHNODE_PUBLICATION_ID
echo    Value: 698c167a7ee84b600b3963a8
echo.
echo 3. Go to Actions tab and enable workflows
echo.
echo 4. Done! System will publish automatically at 9 AM daily
echo.
echo For Blogger + WordPress setup: See GITHUB_ACTIONS_SETUP.md
echo.
pause
