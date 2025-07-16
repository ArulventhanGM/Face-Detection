import unittest
import json
import tempfile
import shutil
import os
import sys
from io import BytesIO
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import init_database, KnownFace

class TestFaceRecognitionAPI(unittest.TestCase):
    """Test suite for Face Recognition API endpoints"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_faces.db')
        
        # Set up test database
        os.environ['DATABASE_PATH'] = self.test_db_path
        init_database()
        
        # Configure Flask app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Create test image
        self.test_image_data = self.create_test_image()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_image(self):
        """Create a test image for API testing"""
        # Create a simple face-like image
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(image, (100, 100), 80, (255, 255, 255), -1)
        cv2.circle(image, (80, 80), 10, (0, 0, 0), -1)
        cv2.circle(image, (120, 80), 10, (0, 0, 0), -1)
        cv2.ellipse(image, (100, 120), (20, 10), 0, 0, 180, (0, 0, 0), 2)
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', image)
        return BytesIO(buffer.tobytes())
    
    def test_system_stats_endpoint(self):
        """Test system stats endpoint"""
        response = self.client.get('/api/system/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
    
    def test_system_health_endpoint(self):
        """Test system health endpoint"""
        response = self.client.get('/api/system/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('system_stats', data['data'])
        self.assertIn('face_processor', data['data'])
    
    def test_admin_get_faces_empty(self):
        """Test getting faces from empty database"""
        response = self.client.get('/api/admin/faces')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']), 0)
    
    def test_admin_upload_face_valid(self):
        """Test uploading a valid face"""
        self.test_image_data.seek(0)
        
        data = {
            'image': (self.test_image_data, 'test_face.jpg'),
            'name': 'John Doe',
            'employee_id': 'EMP001',
            'department': 'Engineering',
            'position': 'Software Engineer',
            'email': 'john.doe@test.com',
            'phone': '+1234567890'
        }
        
        response = self.client.post('/api/admin/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertIn('face_id', response_data['data'])
    
    def test_admin_upload_face_invalid_data(self):
        """Test uploading face with invalid data"""
        self.test_image_data.seek(0)
        
        data = {
            'image': (self.test_image_data, 'test_face.jpg'),
            'name': '',  # Invalid: empty name
            'employee_id': 'EMP001'
        }
        
        response = self.client.post('/api/admin/upload', 
                                  data=data,
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
    
    def test_admin_search_faces(self):
        """Test searching faces"""
        # First add a face
        self.test_image_data.seek(0)
        upload_data = {
            'image': (self.test_image_data, 'test_face.jpg'),
            'name': 'Jane Smith',
            'employee_id': 'EMP002',
            'department': 'Marketing'
        }
        
        self.client.post('/api/admin/upload', 
                        data=upload_data,
                        content_type='multipart/form-data')
        
        # Search for the face
        response = self.client.get('/api/admin/search?q=Jane')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']['faces']), 0)
        self.assertEqual(data['data']['faces'][0]['name'], 'Jane Smith')
    
    def test_admin_get_departments(self):
        """Test getting departments"""
        response = self.client.get('/api/admin/departments')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
    
    def test_admin_get_statistics(self):
        """Test getting face statistics"""
        response = self.client.get('/api/admin/statistics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('total_faces', data['data'])
    
    def test_recognition_no_file(self):
        """Test recognition endpoint without file"""
        response = self.client.post('/api/recognize')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_recognition_with_file(self):
        """Test recognition endpoint with file"""
        self.test_image_data.seek(0)
        
        data = {
            'image': (self.test_image_data, 'test_recognition.jpg')
        }
        
        response = self.client.post('/api/recognize',
                                  data=data,
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertIn('total_faces_detected', response_data['data'])
        self.assertIn('recognized_faces', response_data['data'])
    
    def test_camera_capture_no_data(self):
        """Test camera capture without image data"""
        response = self.client.post('/api/camera/capture',
                                  json={},
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_history_search(self):
        """Test history search endpoint"""
        response = self.client.get('/api/history/search')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('history', data['data'])
        self.assertIn('total_count', data['data'])
    
    def test_history_statistics(self):
        """Test history statistics endpoint"""
        response = self.client.get('/api/history/statistics')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('total_recognitions', data['data'])
    
    def test_export_results(self):
        """Test exporting recognition results"""
        # Create sample results data
        sample_results = {
            'total_faces_detected': 2,
            'total_faces_recognized': 1,
            'recognized_faces': [
                {
                    'name': 'John Doe',
                    'confidence': 85.5,
                    'face_location': [50, 150, 200, 100]
                },
                {
                    'name': 'Unknown',
                    'confidence': 0.0,
                    'face_location': [60, 160, 210, 110]
                }
            ],
            'processing_time': 2.5
        }
        
        # Test JSON export
        response = self.client.post('/api/export/results',
                                  json={
                                      'results': sample_results,
                                      'format': 'json'
                                  },
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json; charset=utf-8')
    
    def test_export_database(self):
        """Test exporting face database"""
        response = self.client.get('/api/export/database?format=json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json; charset=utf-8')

class TestAPIValidation(unittest.TestCase):
    """Test suite for API input validation"""
    
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_invalid_file_type(self):
        """Test uploading invalid file type"""
        # Create a text file instead of image
        text_data = BytesIO(b"This is not an image")
        
        data = {
            'image': (text_data, 'test.txt'),
            'name': 'Test User'
        }
        
        response = self.client.post('/api/admin/upload',
                                  data=data,
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
    
    def test_missing_required_fields(self):
        """Test API with missing required fields"""
        response = self.client.post('/api/admin/upload',
                                  data={},
                                  content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 400)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
