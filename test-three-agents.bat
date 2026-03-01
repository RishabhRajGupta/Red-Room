@echo off
echo ========================================
echo The Red Room - Three-Agent System Test
echo ========================================
echo.
echo Testing: Saboteur → Exploit Lab → Surgeon
echo.

REM Activate conda environment if it exists
if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" redroom
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" redroom
)

REM Run the test
python test_three_agents.py

echo.
echo ========================================
echo Test Complete!
echo ========================================
pause
