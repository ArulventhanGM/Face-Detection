@echo off
echo Face Recognition Backend - Emergency Fix Setup
echo This script fixes setuptools issues and installs dependencies properly
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Remove existing virtual environment if it's corrupted
echo Checking for corrupted virtual environment...
if exist "venv" (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create fresh virtual environment
echo Creating fresh virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment.
    echo Please ensure Python 3.8-3.11 is installed from https://www.python.org/downloads/
    echo Python 3.13 may have compatibility issues with face_recognition
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade core build tools first
echo Upgrading core build tools...
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

REM Install build dependencies
echo Installing build dependencies...
pip install cmake
pip install pybind11

REM Install packages in correct order with increased timeouts
echo Installing numpy (this may take a while)...
pip install --timeout 600 --retries 5 --no-cache-dir numpy==1.24.3
if errorlevel 1 (
    echo Error installing numpy. Trying with wheel...
    pip install --timeout 600 --retries 5 --only-binary=all numpy==1.24.3
    if errorlevel 1 (
        echo Error: Failed to install numpy
        pause
        exit /b 1
    )
)

echo Installing Pillow...
pip install --timeout 300 --retries 3 pillow==10.0.1

echo Installing Flask and web dependencies...
pip install --timeout 300 flask==2.3.3 flask-cors==4.0.0 werkzeug==2.3.7 python-multipart==0.0.6

echo Installing dlib (this will take several minutes)...
echo Please be patient - this is the most time-consuming step...
pip install --timeout 1200 --retries 3 --no-cache-dir dlib==19.24.2
if errorlevel 1 (
    echo Dlib installation failed. Trying alternative approach...
    pip install --timeout 1200 --retries 2 --only-binary=all dlib
    if errorlevel 1 (
        echo Error: Failed to install dlib. You may need Visual C++ Build Tools.
        echo Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo Or try the Docker installation method.
        pause
        exit /b 1
    )
)

echo Installing face_recognition...
pip install --timeout 600 --retries 3 --no-cache-dir face_recognition==1.3.0
if errorlevel 1 (
    echo face_recognition installation failed. Trying alternative...
    pip install --timeout 900 --retries 2 face_recognition
    if errorlevel 1 (
        echo Error: Failed to install face_recognition
        pause
        exit /b 1
    )
)

echo Installing OpenCV...
pip install --timeout 300 opencv-python==4.8.1.78

echo.
echo Verifying installation...
python -c "import numpy; print('✓ numpy OK')"
python -c "import PIL; print('✓ Pillow OK')"
python -c "import flask; print('✓ Flask OK')"
python -c "import cv2; print('✓ OpenCV OK')"
python -c "import dlib; print('✓ dlib OK')"
python -c "import face_recognition; print('✓ face_recognition OK')"

if errorlevel 1 (
    echo Some packages failed verification. Please check the output above.
    pause
    exit /b 1
)

echo.
echo All packages installed and verified successfully!

REM Initialize database
echo Initializing database...
python models.py

echo.
echo Setup completed successfully!
echo You can now start the backend with: python app.py
echo.
pause
