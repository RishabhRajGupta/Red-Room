@echo off
echo ========================================
echo The Red Room - Conda Environment Setup
echo ========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda is not installed or not in PATH
    echo Please install Anaconda or Miniconda first
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Step 1: Creating conda environment 'redroom'...
echo.
conda env create -f environment.yml

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Environment already exists. Updating instead...
    conda env update -f environment.yml --prune
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To activate the environment, run:
echo   conda activate redroom
echo.
echo Then start the scanner with:
echo   python web_scanner_app_realtime.py
echo.
echo Or use the quick start script:
echo   start-realtime-scanner-conda.bat
echo.
pause
