@echo off
echo Starting Face Recognition System Frontend...
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
    if errorlevel 1 (
        echo Error: Failed to install dependencies. Make sure Node.js and npm are installed.
        pause
        exit /b 1
    )
)

REM Start the React development server
echo Starting React development server...
echo Frontend will be available at http://localhost:3000
echo.
npm start

pause
