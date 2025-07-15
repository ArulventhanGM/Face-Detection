"""
Face processor with OpenCV fallback for when face_recognition is not available
"""
import cv2
import numpy as np
from PIL import Image
import pickle
import json
import time
import os

class FaceProcessorMinimal:
    """Minimal face processor using only OpenCV for basic face detection"""
    
    def __init__(self):
        # Load OpenCV's face detection classifier
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_faces = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from database (simplified)"""
        try:
            from models import KnownFace
            self.known_faces = KnownFace.get_all()
        except Exception as e:
            print(f"Warning: Could not load known faces: {e}")
            self.known_faces = []
    
    def process_image_for_known_face(self, image_path):
        """Process image for known face storage (simplified without encoding)"""
        try:
            # Load and validate image
            image = cv2.imread(image_path)
            if image is None:
                return None, "Could not load image"
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please upload an image with only one face"
            
            # Return a simple face descriptor (just the bounding box for now)
            face_box = faces[0]
            return face_box.tolist(), None
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def recognize_faces_in_image(self, image_path):
        """Basic face detection without recognition"""
        start_time = time.time()
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None, "Could not load image"
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            detected_faces = []
            
            for (x, y, w, h) in faces:
                # Since we don't have face recognition, mark all as unknown
                face_info = {
                    'id': None,
                    'name': 'Unknown (Recognition disabled)',
                    'employee_id': 'N/A',
                    'department': 'N/A', 
                    'position': 'N/A',
                    'email': 'N/A',
                    'phone': 'N/A',
                    'confidence': 0.0,
                    'face_location': (y, x+w, y+h, x)  # Convert to face_recognition format
                }
                detected_faces.append(face_info)
            
            processing_time = time.time() - start_time
            
            result = {
                'total_faces_detected': len(faces),
                'total_faces_recognized': 0,  # No recognition in minimal mode
                'recognized_faces': detected_faces,
                'processing_time': processing_time,
                'image_path': image_path,
                'mode': 'minimal_opencv_only'
            }
            
            # Save to history if models are available
            try:
                from models import RecognitionHistory
                RecognitionHistory.create(
                    test_image_path=image_path,
                    recognized_faces=json.dumps(detected_faces),
                    total_faces_detected=len(faces),
                    total_faces_recognized=0,
                    processing_time=processing_time
                )
            except:
                pass  # Ignore if can't save to history
            
            return result, None
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def create_annotated_image(self, image_path, recognition_result):
        """Create annotated image with face boxes"""
        try:
            image = cv2.imread(image_path)
            
            for face in recognition_result['recognized_faces']:
                top, right, bottom, left = face['face_location']
                
                # Draw rectangle around face (red for unknown in minimal mode)
                color = (0, 0, 255)  # Red for unknown
                cv2.rectangle(image, (left, top), (right, bottom), color, 2)
                
                # Draw label
                label = face['name']
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(image, (left, bottom - 35), (left + label_size[0], bottom), color, cv2.FILLED)
                
                # Draw label text
                cv2.putText(image, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save annotated image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            annotated_path = os.path.join(os.path.dirname(image_path), f"{base_name}_annotated.jpg")
            
            cv2.imwrite(annotated_path, image)
            return annotated_path
            
        except Exception as e:
            print(f"Error creating annotated image: {str(e)}")
            return None
    
    def refresh_known_faces(self):
        """Refresh known faces"""
        self.load_known_faces()
        return len(self.known_faces)

# Try to import the full face_recognition processor, fall back to minimal if needed
try:
    import face_recognition
    from face_processor import FaceProcessor
    print("✓ Full face recognition available")
except ImportError as e:
    print(f"⚠ Face recognition not available, using minimal OpenCV-only mode: {e}")
    FaceProcessor = FaceProcessorMinimal

# Utility functions remain the same
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_upload_directories():
    directories = ['uploads', 'uploads/known_faces', 'uploads/test_images']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def validate_image_file(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except:
        return False
