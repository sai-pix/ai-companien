@echo off
echo Starting AI Desktop Wellness Companion...
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
