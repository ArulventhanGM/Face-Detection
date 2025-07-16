import unittest
import os
import tempfile
import shutil
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from face_processor import FaceProcessor
from models import init_database, KnownFace

class TestFaceProcessor(unittest.TestCase):
    """Test suite for LBPH Face Processor"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_faces.db')
        
        # Initialize test database
        os.environ['DATABASE_PATH'] = self.test_db_path
        init_database()
        
        # Create test face processor
        self.processor = FaceProcessor()
        
        # Create test images
        self.test_image_path = self.create_test_image()
        self.test_image_no_face = self.create_test_image_no_face()
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def create_test_image(self):
        """Create a test image with a face-like pattern"""
        # Create a simple face-like image for testing
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Draw a simple face pattern
        cv2.circle(image, (100, 100), 80, (255, 255, 255), -1)  # Face
        cv2.circle(image, (80, 80), 10, (0, 0, 0), -1)   # Left eye
        cv2.circle(image, (120, 80), 10, (0, 0, 0), -1)  # Right eye
        cv2.ellipse(image, (100, 120), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # Mouth
        
        test_image_path = os.path.join(self.test_dir, 'test_face.jpg')
        cv2.imwrite(test_image_path, image)
        return test_image_path
    
    def create_test_image_no_face(self):
        """Create a test image without a face"""
        image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        test_image_path = os.path.join(self.test_dir, 'test_no_face.jpg')
        cv2.imwrite(test_image_path, image)
        return test_image_path
    
    def test_face_processor_initialization(self):
        """Test face processor initialization"""
        self.assertIsNotNone(self.processor.face_recognizer)
        self.assertIsNotNone(self.processor.face_cascade)
        self.assertEqual(self.processor.face_size, (100, 100))
        self.assertEqual(self.processor.confidence_threshold, 100)
    
    def test_extract_face_for_training(self):
        """Test face extraction for training"""
        # Test with image containing face
        face_data = self.processor._extract_face_for_training(self.test_image_path)
        self.assertIsNotNone(face_data)
        self.assertEqual(face_data.shape, self.processor.face_size)
        
        # Test with image without face
        face_data = self.processor._extract_face_for_training(self.test_image_no_face)
        self.assertIsNone(face_data)
    
    def test_process_image_for_known_face(self):
        """Test processing image for known face"""
        # Test with valid face image
        face_data, error = self.processor.process_image_for_known_face(self.test_image_path)
        self.assertIsNotNone(face_data)
        self.assertIsNone(error)
        
        # Test with image without face
        face_data, error = self.processor.process_image_for_known_face(self.test_image_no_face)
        self.assertIsNone(face_data)
        self.assertIsNotNone(error)
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        # Test with good confidence (low LBPH value)
        confidence = self.processor._calculate_confidence_score(20.0)
        self.assertGreater(confidence, 80)
        
        # Test with poor confidence (high LBPH value)
        confidence = self.processor._calculate_confidence_score(150.0)
        self.assertEqual(confidence, 0.0)
        
        # Test with medium confidence
        confidence = self.processor._calculate_confidence_score(50.0)
        self.assertGreater(confidence, 40)
        self.assertLess(confidence, 60)
    
    def test_load_known_faces_empty_database(self):
        """Test loading known faces from empty database"""
        self.processor.load_known_faces()
        self.assertEqual(len(self.processor.known_face_metadata), 0)
        self.assertFalse(self.processor.is_trained)
    
    def test_recognize_faces_no_training(self):
        """Test face recognition without training data"""
        result, error = self.processor.recognize_faces_in_image(self.test_image_path)
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertEqual(result['total_faces_detected'], 1)
        self.assertEqual(result['total_faces_recognized'], 0)
        self.assertEqual(result['recognized_faces'][0]['name'], 'Unknown')
    
    def test_system_info(self):
        """Test system information retrieval"""
        info = self.processor.get_system_info()
        self.assertIn('known_faces_count', info)
        self.assertIn('face_detection_model', info)
        self.assertIn('recognition_algorithm', info)
        self.assertIn('is_trained', info)
        self.assertEqual(info['recognition_algorithm'], 'LBPH')
    
    def test_update_settings(self):
        """Test updating processor settings"""
        original_threshold = self.processor.confidence_threshold
        
        # Update confidence threshold
        self.processor.update_settings(confidence_threshold=80.0)
        self.assertEqual(self.processor.confidence_threshold, 80.0)
        self.assertNotEqual(self.processor.confidence_threshold, original_threshold)
        
        # Update face size
        self.processor.update_settings(face_size=(120, 120))
        self.assertEqual(self.processor.face_size, (120, 120))
    
    def test_validate_face_image(self):
        """Test face image validation"""
        # Test with valid image
        is_valid, error = self.processor.validate_face_image(self.test_image_path)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test with non-existent image
        is_valid, error = self.processor.validate_face_image('non_existent.jpg')
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_refresh_known_faces(self):
        """Test refreshing known faces"""
        count = self.processor.refresh_known_faces()
        self.assertEqual(count, 0)  # Empty database
        self.assertFalse(self.processor.is_trained)

class TestFaceProcessorWithData(unittest.TestCase):
    """Test suite for Face Processor with training data"""
    
    def setUp(self):
        """Set up test environment with sample data"""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_faces.db')
        
        os.environ['DATABASE_PATH'] = self.test_db_path
        init_database()
        
        # Create test images
        self.test_image1 = self.create_test_face_image('person1.jpg')
        self.test_image2 = self.create_test_face_image('person2.jpg')
        
        # Add test faces to database
        self.add_test_face('John Doe', 'EMP001', self.test_image1)
        self.add_test_face('Jane Smith', 'EMP002', self.test_image2)
        
        # Create processor
        self.processor = FaceProcessor()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def create_test_face_image(self, filename):
        """Create a test face image"""
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        cv2.circle(image, (100, 100), 80, (255, 255, 255), -1)
        cv2.circle(image, (80, 80), 10, (0, 0, 0), -1)
        cv2.circle(image, (120, 80), 10, (0, 0, 0), -1)
        cv2.ellipse(image, (100, 120), (20, 10), 0, 0, 180, (0, 0, 0), 2)
        
        path = os.path.join(self.test_dir, filename)
        cv2.imwrite(path, image)
        return path
    
    def add_test_face(self, name, employee_id, image_path):
        """Add a test face to the database"""
        # Process face data
        face_data = self.processor._extract_face_for_training(image_path)
        if face_data is not None:
            import pickle
            face_encoding_blob = pickle.dumps(face_data)
            
            KnownFace.create(
                name=name,
                employee_id=employee_id,
                department='Test Dept',
                position='Test Position',
                email=f'{name.lower().replace(" ", ".")}@test.com',
                phone='+1234567890',
                image_path=image_path,
                face_encoding=face_encoding_blob
            )
    
    def test_load_known_faces_with_data(self):
        """Test loading known faces with training data"""
        self.processor.load_known_faces()
        self.assertEqual(len(self.processor.known_face_metadata), 2)
        self.assertTrue(self.processor.is_trained)
    
    def test_recognize_faces_with_training(self):
        """Test face recognition with training data"""
        # Create a test image similar to training data
        test_image = self.create_test_face_image('test_recognition.jpg')
        
        result, error = self.processor.recognize_faces_in_image(test_image)
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertEqual(result['total_faces_detected'], 1)
        
        # The face should be recognized (though confidence may vary)
        recognized_face = result['recognized_faces'][0]
        self.assertIn('name', recognized_face)
        self.assertIn('confidence', recognized_face)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
