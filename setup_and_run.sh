#!/bin/bash

# Face Recognition Web Application Setup Script
# This script sets up and runs the full-stack face recognition application

echo "🎭 Face Recognition Web Application Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    print_status "Found Python: $($PYTHON_CMD --version)"
}

# Check if Node.js is installed (for React frontend)
check_node() {
    if command -v node &> /dev/null; then
        print_status "Found Node.js: $(node --version)"
        HAS_NODE=true
    else
        print_warning "Node.js not found. React frontend will not be available."
        HAS_NODE=false
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_status "Python dependencies installed successfully!"
    else
        print_error "Failed to install Python dependencies."
        exit 1
    fi
}

# Install Node.js dependencies
install_node_deps() {
    if [ "$HAS_NODE" = true ]; then
        print_status "Installing Node.js dependencies..."
        cd frontend
        npm install
        if [ $? -eq 0 ]; then
            print_status "Node.js dependencies installed successfully!"
        else
            print_error "Failed to install Node.js dependencies."
        fi
        cd ..
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=("known_faces" "test_images" "outputs" "backend")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done
}

# Check for known faces
check_known_faces() {
    face_count=$(find known_faces -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" 2>/dev/null | wc -l)
    
    if [ $face_count -eq 0 ]; then
        print_warning "No known faces found in 'known_faces' directory."
        print_warning "Please add individual photos of people you want to recognize."
        print_warning "Use format: firstname_lastname.jpg (e.g., john_doe.jpg)"
    else
        print_status "Found $face_count known face(s) in the database."
    fi
}

# Start the Flask backend
start_backend() {
    print_status "Starting Flask backend server..."
    
    # Activate virtual environment
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    cd backend
    $PYTHON_CMD app.py &
    BACKEND_PID=$!
    cd ..
    
    print_status "Backend server started (PID: $BACKEND_PID)"
    print_status "Backend URL: http://localhost:5000"
}

# Start the React frontend
start_frontend() {
    if [ "$HAS_NODE" = true ]; then
        print_status "Starting React frontend..."
        cd frontend
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        print_status "Frontend server started (PID: $FRONTEND_PID)"
        print_status "Frontend URL: http://localhost:3000"
    fi
}

# Main setup function
main() {
    print_status "Starting Face Recognition Web Application setup..."
    
    # Check system requirements
    check_python
    check_node
    
    # Create directories
    create_directories
    
    # Install dependencies
    install_python_deps
    install_node_deps
    
    # Check for known faces
    check_known_faces
    
    # Start services
    start_backend
    
    # Wait a moment for backend to start
    sleep 3
    
    if [ "$HAS_NODE" = true ]; then
        start_frontend
        print_status "🚀 Application is starting up!"
        print_status "🌐 Frontend: http://localhost:3000"
        print_status "🔧 Backend API: http://localhost:5000"
    else
        print_status "🚀 Application is running!"
        print_status "🌐 Web Interface: http://localhost:5000"
    fi
    
    print_status "📱 API Documentation: http://localhost:5000/api/health"
    print_status ""
    print_status "To stop the application, press Ctrl+C"
    
    # Wait for user interrupt
    trap 'print_status "Stopping application..."; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit 0' INT
    
    # Keep script running
    wait
}

# Run main function
main "$@"
