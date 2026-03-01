@echo off
echo ========================================
echo The Red Room - Real-Time Scanner
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements-realtime.txt
echo.
echo Starting real-time web scanner...
echo Server will be available at: http://127.0.0.1:5000
echo.
python web_scanner_app_realtime.py
