#!/usr/bin/env python3
"""
Face Recognition Application Launcher
Simple script to start the Face Recognition web application
"""

import os
import sys
import subprocess
import time

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🎭 FACE RECOGNITION WEB APPLICATION")
    print("=" * 60)
    print()

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 3.8+ required!")
        return False
    
    print("   ✅ Python version OK")
    return True

def check_directories():
    """Check required directories"""
    print("\n📁 Checking project structure...")
    
    required_dirs = ["backend", "known_faces", "test_images", "outputs"]
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}/")
        else:
            print(f"   📁 Creating {directory}/")
            os.makedirs(directory, exist_ok=True)

def install_dependencies():
    """Install basic dependencies"""
    print("\n📦 Installing dependencies...")
    
    basic_packages = ["flask", "flask-cors", "pillow", "numpy", "werkzeug"]
    
    for package in basic_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package} already installed")
        except ImportError:
            print(f"   📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def start_application():
    """Start the Flask application"""
    print("\n🚀 Starting Face Recognition Application...")
    print()
    print("=" * 60)
    print("📱 Open your browser and go to:")
    print("🌐 http://localhost:5000")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Change to backend directory
    if os.path.exists("backend"):
        os.chdir("backend")
    
    # Try to start the application
    app_files = ["app_demo.py", "app.py"]
    
    for app_file in app_files:
        if os.path.exists(app_file):
            print(f"🎬 Running {app_file}...")
            try:
                subprocess.run([sys.executable, app_file])
                break
            except KeyboardInterrupt:
                print("\n\n🛑 Application stopped by user")
                break
            except Exception as e:
                print(f"❌ Error running {app_file}: {e}")
                continue
    else:
        print("❌ No application file found!")

def main():
    """Main function"""
    print_banner()
    
    if not check_python():
        input("Press Enter to exit...")
        return
    
    check_directories()
    install_dependencies()
    start_application()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Launcher stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
