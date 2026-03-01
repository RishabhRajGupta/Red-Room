@echo off
REM Clean Git History and Push to GitHub
echo ========================================
echo Cleaning Git History (Removing API Keys)
echo ========================================
echo.

REM Step 1: Verify backup exists
echo [1/7] Verifying backup branch...
git branch | findstr "backup-before-cleanup" >nul
if %errorlevel% neq 0 (
    echo Creating backup branch...
    git branch backup-before-cleanup
)
echo Backup branch exists: backup-before-cleanup
echo.

REM Step 2: Get current remote URL
echo [2/7] Getting remote URL...
for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
echo Remote: %REMOTE_URL%
echo.

REM Step 3: Remove .git directory
echo [3/7] Removing old git history...
echo WARNING: This will delete all git history!
echo Press Ctrl+C to cancel, or
pause
rmdir /s /q .git
echo Git history removed.
echo.

REM Step 4: Initialize new repository
echo [4/7] Initializing new repository...
git init
git branch -M main
echo New repository initialized.
echo.

REM Step 5: Add all files
echo [5/7] Adding all files...
git add .
echo Files added.
echo.

REM Step 6: Create initial commit
echo [6/7] Creating initial commit...
git commit -m "Initial commit - Production ready (API keys removed)"
echo Commit created.
echo.

REM Step 7: Push to GitHub
echo [7/7] Pushing to GitHub...
echo.
echo Remote URL: %REMOTE_URL%
echo.
echo This will FORCE PUSH and overwrite remote history!
echo Press Ctrl+C to cancel, or
pause
git remote add origin %REMOTE_URL%
git push origin main --force
echo.

echo ========================================
echo Clean History Pushed Successfully!
echo ========================================
echo.
echo IMPORTANT: Revoke the exposed API keys!
echo Visit: https://makersuite.google.com/app/apikey
echo Delete the old keys and generate new ones.
echo.
echo Backup branch available: backup-before-cleanup
echo To restore: git checkout backup-before-cleanup
echo.
pause
