# Face Recognition Web Application Setup Script for Windows
# This script sets up and runs the full-stack face recognition application

Write-Host "🎭 Face Recognition Web Application Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Python is installed
function Check-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Found Python: $pythonVersion"
            return $true
        }
    } catch {
        Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or higher."
        return $false
    }
}

# Check if Node.js is installed
function Check-Node {
    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Found Node.js: $nodeVersion"
            return $true
        }
    } catch {
        Write-Warning "Node.js not found. React frontend will not be available."
        return $false
    }
}

# Install Python dependencies
function Install-PythonDeps {
    Write-Status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Status "Creating virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Python dependencies installed successfully!"
        return $true
    } else {
        Write-Error "Failed to install Python dependencies."
        return $false
    }
}

# Install Node.js dependencies
function Install-NodeDeps {
    param([bool]$HasNode)
    
    if ($HasNode) {
        Write-Status "Installing Node.js dependencies..."
        Push-Location frontend
        npm install
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Node.js dependencies installed successfully!"
        } else {
            Write-Error "Failed to install Node.js dependencies."
        }
        Pop-Location
    }
}

# Create necessary directories
function Create-Directories {
    Write-Status "Creating necessary directories..."
    
    $directories = @("known_faces", "test_images", "outputs", "backend")
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Created directory: $dir"
        }
    }
}

# Check for known faces
function Check-KnownFaces {
    $faceFiles = Get-ChildItem -Path "known_faces" -Include "*.jpg", "*.jpeg", "*.png" -Recurse -ErrorAction SilentlyContinue
    $faceCount = $faceFiles.Count
    
    if ($faceCount -eq 0) {
        Write-Warning "No known faces found in 'known_faces' directory."
        Write-Warning "Please add individual photos of people you want to recognize."
        Write-Warning "Use format: firstname_lastname.jpg (e.g., john_doe.jpg)"
    } else {
        Write-Status "Found $faceCount known face(s) in the database."
    }
}

# Start the Flask backend
function Start-Backend {
    Write-Status "Starting Flask backend server..."
    
    # Activate virtual environment and start backend
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        & "venv\Scripts\Activate.ps1"
        Set-Location backend
        python app.py
    }
    
    Write-Status "Backend server started (Job ID: $($backendJob.Id))"
    Write-Status "Backend URL: http://localhost:5000"
    
    return $backendJob
}

# Start the React frontend
function Start-Frontend {
    param([bool]$HasNode)
    
    if ($HasNode) {
        Write-Status "Starting React frontend..."
        
        $frontendJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            Set-Location frontend
            npm start
        }
        
        Write-Status "Frontend server started (Job ID: $($frontendJob.Id))"
        Write-Status "Frontend URL: http://localhost:3000"
        
        return $frontendJob
    }
    
    return $null
}

# Main setup function
function Main {
    Write-Status "Starting Face Recognition Web Application setup..."
    
    # Check system requirements
    $hasPython = Check-Python
    if (-not $hasPython) {
        exit 1
    }
    
    $hasNode = Check-Node
    
    # Create directories
    Create-Directories
    
    # Install dependencies
    $pythonInstallSuccess = Install-PythonDeps
    if (-not $pythonInstallSuccess) {
        exit 1
    }
    
    Install-NodeDeps -HasNode $hasNode
    
    # Check for known faces
    Check-KnownFaces
    
    # Start services
    $backendJob = Start-Backend
    
    # Wait a moment for backend to start
    Start-Sleep -Seconds 3
    
    $frontendJob = $null
    if ($hasNode) {
        $frontendJob = Start-Frontend -HasNode $hasNode
        Write-Status "🚀 Application is starting up!"
        Write-Status "🌐 Frontend: http://localhost:3000"
        Write-Status "🔧 Backend API: http://localhost:5000"
    } else {
        Write-Status "🚀 Application is running!"
        Write-Status "🌐 Web Interface: http://localhost:5000"
    }
    
    Write-Status "📱 API Documentation: http://localhost:5000/api/health"
    Write-Status ""
    Write-Status "To stop the application, press Ctrl+C"
    
    # Wait for user interrupt
    try {
        while ($true) {
            Start-Sleep -Seconds 1
            
            # Check if jobs are still running
            if ($backendJob.State -eq "Failed" -or $backendJob.State -eq "Completed") {
                Write-Error "Backend server stopped unexpectedly"
                break
            }
            
            if ($frontendJob -and ($frontendJob.State -eq "Failed" -or $frontendJob.State -eq "Completed")) {
                Write-Warning "Frontend server stopped unexpectedly"
            }
        }
    } catch [System.Management.Automation.RuntimeException] {
        Write-Status "Stopping application..."
    } finally {
        # Clean up jobs
        if ($backendJob) {
            Stop-Job $backendJob -ErrorAction SilentlyContinue
            Remove-Job $backendJob -ErrorAction SilentlyContinue
        }
        if ($frontendJob) {
            Stop-Job $frontendJob -ErrorAction SilentlyContinue
            Remove-Job $frontendJob -ErrorAction SilentlyContinue
        }
    }
}

# Run main function
Main
