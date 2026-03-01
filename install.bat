@echo off
echo ========================================
echo The Red Room - Quick Install
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
pip install -r requirements-realtime.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Installing The Red Room package...
pip install -e .

if errorlevel 1 (
    echo [WARNING] Package install failed, using run.bat instead
)

echo.
echo [2/3] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker not found!
    echo Docker is required for fullscan command.
    echo Download from: https://www.docker.com/products/docker-desktop
    echo.
    echo You can still use other commands without Docker.
) else (
    echo Docker found!
)

echo.
echo [3/3] Testing installation...
python -m redroom.cli hardware

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Quick Start:
echo   1. Test three-agent system:
echo      python test_three_agents.py
echo.
echo   2. Scan demo app:
echo      run.bat fullscan ./demo-app
echo      (or: python -m redroom.cli fullscan ./demo-app)
echo.
echo   3. Check hardware:
echo      run.bat hardware
echo      (or: python -m redroom.cli hardware)
echo.
echo Read QUICKSTART.md for more info.
echo.
pause
