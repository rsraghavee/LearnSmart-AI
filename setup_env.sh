#!/bin/bash
# LearnSmart AI - Linux/macOS Setup Script

echo "===================================="
echo "LearnSmart AI - Setup Script"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/4] Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file with your MySQL credentials!"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "===================================="
echo "Setup completed successfully!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MySQL database credentials"
echo "2. Make sure MySQL server is running"
echo "3. Create the database: CREATE DATABASE learnsmart_ai;"
echo "4. Run the application: python app.py"
echo ""


