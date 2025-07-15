@echo off
echo Starting Complete Face Recognition System...
echo.
echo This will start both the backend server and frontend application.
echo.

REM Start backend in a new command window
echo Starting backend server...
start "Face Recognition Backend" cmd /k "%~dp0start-backend.bat"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new command window  
echo Starting frontend application...
start "Face Recognition Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo Both services are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo You can close this window. The services will continue running in their own windows.
echo.

pause
