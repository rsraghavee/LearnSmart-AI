@echo off
REM LearnSmart AI - Windows Setup Script
echo ====================================
echo LearnSmart AI - Setup Script
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Creating .env file from template...
if not exist .env (
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your MySQL credentials!
) else (
    echo .env file already exists, skipping...
)

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file with your MySQL database credentials
echo 2. Make sure MySQL server is running
echo 3. Create the database: CREATE DATABASE learnsmart_ai;
echo 4. Run the application: python app.py
echo.
pause


