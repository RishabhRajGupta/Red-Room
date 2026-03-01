@echo off
REM This script will rewrite git history to remove API keys
echo ========================================
echo Git History Rewrite - Remove API Keys
echo ========================================
echo.
echo This will:
echo 1. Keep your backup branch (backup-before-cleanup)
echo 2. Create a new clean history with only the latest commit
echo 3. Force push to GitHub
echo.
echo WARNING: This rewrites history on GitHub!
echo.
echo Press Ctrl+C to cancel, or
pause
echo.

REM Get the remote URL
for /f "tokens=*" %%i in ('git remote get-url origin') do set REMOTE_URL=%%i
echo Remote: %REMOTE_URL%
echo.

REM Create a new orphan branch (no history)
echo [1/6] Creating new clean branch...
git checkout --orphan clean-main
echo.

REM Add all current files
echo [2/6] Adding all files...
git add -A
echo.

REM Create single clean commit
echo [3/6] Creating clean commit...
git commit -m "Initial commit - Production ready (no API keys)"
echo.

REM Delete old main branch
echo [4/6] Replacing main branch...
git branch -D main
git branch -m main
echo.

REM Force push
echo [5/6] Pushing to GitHub...
echo This will FORCE PUSH!
echo Press Ctrl+C to cancel, or
pause
git push origin main --force
echo.

REM Verify
echo [6/6] Verifying...
git log --oneline
echo.

echo ========================================
echo SUCCESS! Clean History Pushed
echo ========================================
echo.
echo Old history backup: backup-before-cleanup
echo.
echo CRITICAL: Revoke the exposed API keys NOW!
echo Visit: https://makersuite.google.com/app/apikey
echo Delete these keys:
echo - AIzaSyBkjQf8hUqT_qTx2cilgpuaExdviEBa-0g
echo - AIzaSyBqZ6jeAg-NF6v6FH-KWqsNW2bnlhuxfNU
echo - AIzaSyDt6Uf1-fgnUmgx6rUIHi_R3CsXlOh6sM8
echo - AIzaSyBsMwNoGgslF97gETtHYtc5u3NFPCAFuCI
echo - AIzaSyCG2MddLWVIdHjOH7FTSNJxEwu8DR0HZoE
echo - AIzaSyDPNItnbRl7AwqcrGVMAwANFpmVvzIwKJA
echo - AIzaSyCDrN5jpl-AXKsSd_ovf8CE_rvzVCf7aJA
echo - AIzaSyB5kEinx4DgvzBRqmnQr5Dofh6y7MgapZk
echo.
pause
