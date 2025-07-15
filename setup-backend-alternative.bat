@echo off
echo Alternative Face Recognition Backend Setup...
echo This script uses alternative installation methods for problematic packages.
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip and install build tools
echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel

REM Try installing from conda-forge (if conda is available)
echo Checking for conda...
conda --version >nul 2>&1
if not errorlevel 1 (
    echo Conda found! Installing packages via conda-forge...
    conda install -c conda-forge numpy pillow flask flask-cors dlib opencv face_recognition -y
    pip install werkzeug==2.3.7 python-multipart==0.0.6
    goto :database_init
)

REM Alternative: Install pre-compiled wheels
echo Installing pre-compiled wheels...

REM Install core packages first
pip install --no-cache-dir --timeout 600 numpy pillow flask flask-cors werkzeug python-multipart

REM Try installing dlib from pre-compiled wheel
echo Trying to install dlib from wheel...
pip install --no-cache-dir --timeout 600 https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.0-cp39-cp39-win_amd64.whl
if errorlevel 1 (
    echo Dlib wheel failed, trying pip install...
    pip install --no-cache-dir --timeout 900 dlib
)

REM Install face_recognition
echo Installing face_recognition...
pip install --no-cache-dir --timeout 600 face_recognition

REM Install opencv
pip install --no-cache-dir --timeout 300 opencv-python

:database_init
echo.
echo Checking installation...
python -c "import face_recognition, cv2, flask; print('All packages installed successfully!')"
if errorlevel 1 (
    echo Error: Package verification failed. Some dependencies may be missing.
    echo.
    echo Alternative solutions:
    echo 1. Install Anaconda/Miniconda and use conda environment
    echo 2. Use Docker to run the application
    echo 3. Install Visual C++ Build Tools and retry
    echo.
    pause
    exit /b 1
)

REM Initialize database
echo Initializing database...
python models.py

echo.
echo Setup completed successfully!
echo You can now run the backend with: python app.py
echo.
pause
