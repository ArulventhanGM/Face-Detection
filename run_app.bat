@echo off
title Face Recognition Web Application
color 0A

echo.
echo ==========================================
echo  🎭 Face Recognition Web Application
echo ==========================================
echo.

echo 📍 Current Directory: %CD%
echo.

echo 🔍 Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 📦 Installing basic dependencies...
pip install flask flask-cors pillow numpy werkzeug
echo.

echo 🔍 Checking project structure...
if exist "backend\app_demo.py" (
    echo ✅ Found backend\app_demo.py
) else (
    echo ❌ backend\app_demo.py not found!
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Face Recognition Application...
echo.
echo ==========================================
echo  📱 Open your browser to:
echo  🌐 http://localhost:5000
echo ==========================================
echo  🛑 Press Ctrl+C to stop the server
echo ==========================================
echo.

cd backend
python app_demo.py

pause
