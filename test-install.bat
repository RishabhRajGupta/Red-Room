@echo off
echo ========================================
echo Testing The Red Room Installation
echo ========================================
echo.

echo [1/4] Testing hardware detection...
python -m redroom.cli hardware
if errorlevel 1 (
    echo [FAIL] Hardware detection failed
    pause
    exit /b 1
)
echo [PASS] Hardware detection works!
echo.

echo [2/4] Testing three-agent system...
python test_three_agents.py
if errorlevel 1 (
    echo [FAIL] Three-agent test failed
    pause
    exit /b 1
)
echo [PASS] Three-agent system works!
echo.

echo [3/4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [SKIP] Docker not installed (optional for fullscan)
) else (
    echo [PASS] Docker is installed!
)
echo.

echo [4/4] Testing CLI commands...
python -m redroom.cli --help >nul 2>&1
if errorlevel 1 (
    echo [FAIL] CLI not working
    pause
    exit /b 1
)
echo [PASS] CLI works!
echo.

echo ========================================
echo All Tests Passed!
echo ========================================
echo.
echo You're ready to use The Red Room!
echo.
echo Try:
echo   python -m redroom.cli fullscan ./demo-app
echo.
pause
