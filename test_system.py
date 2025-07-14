#!/usr/bin/env python3
"""
Face Recognition Web Application Test Suite
This script tests all components of the face recognition system
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import face_recognition
        print("  ✅ face_recognition imported successfully")
    except ImportError as e:
        print(f"  ❌ face_recognition import failed: {e}")
        return False
    
    try:
        import cv2
        print("  ✅ opencv-python imported successfully")
    except ImportError as e:
        print(f"  ❌ opencv-python import failed: {e}")
        return False
    
    try:
        import flask
        print("  ✅ flask imported successfully")
    except ImportError as e:
        print(f"  ❌ flask import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("  ✅ numpy imported successfully")
    except ImportError as e:
        print(f"  ❌ numpy import failed: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test if all required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'backend',
        'known_faces',
        'test_images',
        'outputs',
        'frontend'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/ exists")
        else:
            print(f"  ❌ {directory}/ missing")
            all_exist = False
    
    return all_exist

def test_backend_files():
    """Test if all backend files exist"""
    print("\n🔧 Testing backend files...")
    
    required_files = [
        'backend/app.py',
        'backend/recognizer.py',
        'backend/metadata_handler.py',
        'backend/templates/index.html'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_recognizer_module():
    """Test the recognizer module functionality"""
    print("\n🎯 Testing recognizer module...")
    
    try:
        from recognizer import load_known_faces, get_known_faces_info
        
        # Test loading known faces
        encodings, names = load_known_faces()
        print(f"  ✅ load_known_faces() executed successfully")
        print(f"  📊 Found {len(names)} known faces: {names}")
        
        # Test getting face info
        info = get_known_faces_info()
        print(f"  ✅ get_known_faces_info() executed successfully")
        print(f"  📊 Face info: {info}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing recognizer module: {e}")
        return False

def test_metadata_handler():
    """Test the metadata handler module"""
    print("\n👥 Testing metadata handler...")
    
    try:
        from metadata_handler import get_person_metadata, get_all_people
        
        # Test getting all people
        all_people = get_all_people()
        print(f"  ✅ get_all_people() executed successfully")
        print(f"  📊 Found {len(all_people)} people in metadata")
        
        # Test getting specific person
        if all_people:
            first_person = list(all_people.keys())[0]
            person_data = get_person_metadata(first_person)
            print(f"  ✅ get_person_metadata('{first_person}') executed successfully")
            print(f"  📊 Person data: {person_data}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing metadata handler: {e}")
        return False

def test_flask_app():
    """Test if the Flask app can start"""
    print("\n🌐 Testing Flask application...")
    
    try:
        # Import the Flask app
        sys.path.insert(0, 'backend')
        from app import app
        
        # Test if app can be created
        print("  ✅ Flask app imported successfully")
        
        # Test app configuration
        if app.config.get('TESTING') is not None:
            print("  ✅ Flask app configured properly")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing Flask app: {e}")
        return False

def test_known_faces_setup():
    """Test the known faces setup"""
    print("\n👤 Testing known faces setup...")
    
    known_faces_dir = Path('known_faces')
    if not known_faces_dir.exists():
        print("  ❌ known_faces directory doesn't exist")
        return False
    
    # Count face images
    face_files = list(known_faces_dir.glob('*.jpg')) + \
                 list(known_faces_dir.glob('*.jpeg')) + \
                 list(known_faces_dir.glob('*.png'))
    
    if len(face_files) == 0:
        print("  ⚠️  No face images found in known_faces directory")
        print("  💡 Add individual photos with format: firstname_lastname.jpg")
        return False
    
    print(f"  ✅ Found {len(face_files)} face image(s)")
    for face_file in face_files:
        print(f"    - {face_file.name}")
    
    return True

def test_api_endpoints():
    """Test API endpoints (requires server to be running)"""
    print("\n🔌 Testing API endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health endpoint working")
            health_data = response.json()
            print(f"  📊 Health data: {health_data}")
        else:
            print(f"  ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test known faces endpoint
        response = requests.get(f"{base_url}/api/known-faces", timeout=5)
        if response.status_code == 200:
            print("  ✅ Known faces endpoint working")
            faces_data = response.json()
            print(f"  📊 Known faces: {faces_data.get('total_faces', 0)}")
        else:
            print(f"  ❌ Known faces endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ⚠️  Server not running - API tests skipped")
        print("  💡 Start the server with: python backend/app.py")
        return False
    except Exception as e:
        print(f"  ❌ Error testing API endpoints: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Face Recognition Web Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Directory Structure", test_directory_structure),
        ("Backend Files", test_backend_files),
        ("Recognizer Module", test_recognizer_module),
        ("Metadata Handler", test_metadata_handler),
        ("Flask App", test_flask_app),
        ("Known Faces Setup", test_known_faces_setup),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Face Recognition app is ready to use.")
        print("\n🚀 To start the application:")
        print("   Windows: .\\start_app.bat")
        print("   Linux/Mac: ./setup_and_run.sh")
        print("   Manual: python backend/app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common solutions:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Add face images to known_faces/ directory")
        print("   3. Check file permissions")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
