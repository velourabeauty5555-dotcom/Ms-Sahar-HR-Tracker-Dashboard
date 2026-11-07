@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto setup
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto setup
)

echo Python was not found. Install Python 3.9 or later from https://www.python.org/downloads/
echo During installation, enable "Add Python to PATH", then run this file again.
pause
exit /b 1

:setup
if not exist ".venv\Scripts\python.exe" (
    echo Creating a private Python environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto failed
)

if not exist ".venv\Lib\site-packages\reportlab\__init__.py" (
    echo Installing the PDF report package...
    ".venv\Scripts\python.exe" -m pip install "reportlab>=4.2.2"
    if errorlevel 1 goto failed
)
if not exist ".venv\packages-installed" (
    echo Installing app requirements...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto failed
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto failed
    type nul > ".venv\packages-installed"
)

echo Starting HR Client Tracker...
".venv\Scripts\python.exe" -m streamlit run TRACKER.py
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo The app could not start. Check the error above and make sure you have an internet connection for the first setup.
pause
exit /b 1

