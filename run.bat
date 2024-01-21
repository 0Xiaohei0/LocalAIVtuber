@echo off
REM Check if Python is installed
echo Running setup script...
echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    exit /b 1
)

REM Check if the virtual environment already exists
echo Checking if virtual environment already exists...
if exist "venv" (
    echo Virtual environment already exists.
) else (
    REM Create a virtual environment in the "venv" directory
    echo Creating a virtual environment in the "venv" directory...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate the virtual environment
CALL venv\Scripts\activate.bat

echo Virtual environment activated.

echo Installing dependencies...
CALL pip install -r requirements.txt

echo Starting main.py...
python main.py

pause
