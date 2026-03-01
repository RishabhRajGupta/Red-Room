@echo off
echo ========================================
echo The Red Room - Real-Time Scanner
echo (Using Conda Environment)
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda is not installed or not in PATH
    echo Please run setup-conda-env.bat first
    pause
    exit /b 1
)

REM Activate conda environment
echo Activating conda environment 'redroom'...
call conda activate redroom

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Environment 'redroom' not found
    echo Please run setup-conda-env.bat first
    pause
    exit /b 1
)

echo.
echo Starting real-time web scanner...
echo Server will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python web_scanner_app_realtime.py
