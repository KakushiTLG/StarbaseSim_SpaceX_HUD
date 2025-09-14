@echo off
echo StarbaseSim Telemetry GUI - Installation and Launch. This script is made by Claude (so I'm not sure it will work perfectly)
echo =====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found - checking for virtual environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment already exists
)

echo [3/4] Installing dependencies...
REM Activate virtual environment and install requirements
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)


echo [4/4] Starting StarbaseSim Telemetry GUI...
echo.
echo GUI will be available at: http://localhost:5000
echo.
echo Available interfaces:
echo   - http://localhost:5000          (Original interface)
echo.
echo Command line options:
echo   python main.py --overlay     (auto-start with overlay)
echo   python main.py --no-overlay  (web-only mode)
echo   python main.py               (ask user choice)
echo.
echo Press Ctrl+C to stop the server
echo =====================================================
echo.

REM Launch the main application
python main.py

pause