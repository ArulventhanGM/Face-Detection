@echo off
echo Starting Face Recognition System Backend...
echo.

REM Navigate to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment. Make sure Python is installed.
        echo Please install Python 3.8+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip --timeout 300

REM Install dependencies with increased timeout and retry
echo Installing core dependencies...
pip install --timeout 300 --retries 3 numpy==1.24.3
if errorlevel 1 (
    echo Error: Failed to install numpy. Trying alternative approach...
    pip install --timeout 600 --retries 5 --no-cache-dir numpy==1.24.3
    if errorlevel 1 (
        echo Error: Failed to install numpy. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo Installing Pillow...
pip install --timeout 300 --retries 3 pillow==10.0.1

echo Installing Flask dependencies...
pip install --timeout 300 --retries 3 flask==2.3.3 flask-cors==4.0.0 werkzeug==2.3.7 python-multipart==0.0.6

echo Installing dlib (this may take a while)...
pip install --timeout 600 --retries 5 --no-cache-dir dlib==19.24.2
if errorlevel 1 (
    echo Error: Failed to install dlib. Trying with pre-compiled wheel...
    pip install --timeout 600 --retries 5 --only-binary=all dlib
    if errorlevel 1 (
        echo Error: Failed to install dlib. You may need to install Visual C++ Build Tools.
        echo Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        pause
        exit /b 1
    )
)

echo Installing face-recognition...
pip install --timeout 600 --retries 5 --no-cache-dir face-recognition==1.3.0
if errorlevel 1 (
    echo Error: Failed to install face-recognition. Trying alternative approach...
    pip install --timeout 900 --retries 3 --no-deps face-recognition==1.3.0
    if errorlevel 1 (
        echo Error: Failed to install face-recognition.
        pause
        exit /b 1
    )
)

echo Installing OpenCV...
pip install --timeout 300 --retries 3 opencv-python==4.8.1.78

echo.
echo All dependencies installed successfully!

REM Initialize database
echo Initializing database...
python models.py

REM Start the Flask application
echo Starting Flask server...
echo Backend will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
