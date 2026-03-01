@echo off
REM Safely Remove Specific Commit from Git History
echo ========================================
echo Removing "Stable Version" Commit
echo ========================================
echo.

REM Step 1: Create backup
echo [1/5] Creating backup branch...
git branch backup-before-rewrite 2>nul
if %errorlevel% equ 0 (
    echo Backup created: backup-before-rewrite
) else (
    echo Backup already exists: backup-before-rewrite
)
echo.

REM Step 2: Show current history
echo [2/5] Current commit history:
git log --oneline
echo.

REM Step 3: Rebase to remove commit
echo [3/5] Removing "Stable Version" commit...
echo.
echo This will open an editor. Instructions:
echo 1. Find the line with "Stable Version"
echo 2. Change "pick" to "drop"
echo 3. Save and close the editor
echo.
echo Press any key to continue...
pause >nul

git rebase -i f068972^

if %errorlevel% neq 0 (
    echo.
    echo Rebase failed or was aborted.
    echo To restore: git rebase --abort
    echo To restore backup: git checkout backup-before-rewrite
    exit /b 1
)
echo.

REM Step 4: Verify
echo [4/5] Verifying commit is removed...
git log --oneline
echo.
git log -p | findstr "AIzaSy" >nul
if %errorlevel% equ 0 (
    echo WARNING: API keys still found in history!
    echo Consider using clean-and-push.bat instead.
    exit /b 1
) else (
    echo SUCCESS: No API keys found in history!
)
echo.

REM Step 5: Push
echo [5/5] Ready to push to GitHub...
echo.
echo This will FORCE PUSH and rewrite remote history!
echo Press Ctrl+C to cancel, or
pause

git push origin main --force

echo.
echo ========================================
echo Commit Removed Successfully!
echo ========================================
echo.
echo IMPORTANT: Revoke the exposed API keys!
echo Visit: https://makersuite.google.com/app/apikey
echo.
echo Backup available: backup-before-rewrite
echo To restore: git checkout backup-before-rewrite
echo.
pause
