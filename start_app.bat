@echo off
echo Starting Face Recognition Web Application...
echo.
echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Checking for known faces...
if not exist "known_faces\*.jpg" if not exist "known_faces\*.jpeg" if not exist "known_faces\*.png" (
    echo WARNING: No known faces found in 'known_faces' directory
    echo Please add individual photos of people you want to recognize
    echo Use format: firstname_lastname.jpg (e.g., john_doe.jpg)
    echo.
)

echo.
echo Starting Flask server...
cd backend
echo.
echo =================================
echo  Face Recognition Web App Ready
echo =================================
echo  Web Interface: http://localhost:5000
echo  API Documentation: http://localhost:5000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
