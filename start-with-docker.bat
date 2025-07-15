@echo off
echo Face Recognition - Docker Quick Setup
echo This is the most reliable installation method
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed or not in PATH
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    echo After installation, restart your computer and try again.
    pause
    exit /b 1
)

echo Docker found! Starting Face Recognition System...
echo.

REM Navigate to project root
cd /d "%~dp0"

REM Build and start the containers
echo Building and starting containers (this may take 5-10 minutes on first run)...
docker-compose up --build

pause
