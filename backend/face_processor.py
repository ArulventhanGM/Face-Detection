import face_recognition
import cv2
import numpy as np
from PIL import Image
import pickle
import json
import time
import os
from models import KnownFace, RecognitionHistory

class FaceProcessor:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all known faces from database"""
        self.known_face_encodings = []
        self.known_face_metadata = []
        
        known_faces = KnownFace.get_all_encodings()
        
        for face in known_faces:
            # Deserialize face encoding from database
            face_encoding = pickle.loads(face['face_encoding'])
            self.known_face_encodings.append(face_encoding)
            
            # Store metadata
            metadata = {
                'id': face['id'],
                'name': face['name'],
                'employee_id': face['employee_id'],
                'department': face['department'],
                'position': face['position'],
                'email': face['email'],
                'phone': face['phone'],
                'image_path': face['image_path']
            }
            self.known_face_metadata.append(metadata)
    
    def process_image_for_known_face(self, image_path):
        """Process an image to extract face encoding for storing as known face"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return None, "No face detected in the image"
            
            if len(face_locations) > 1:
                return None, "Multiple faces detected. Please upload an image with only one face"
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) > 0:
                return face_encodings[0], None
            else:
                return None, "Could not encode the face in the image"
                
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def recognize_faces_in_image(self, image_path):
        """Recognize faces in a test image"""
        start_time = time.time()
        
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            recognized_faces = []
            
            for i, face_encoding in enumerate(face_encodings):
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding, 
                    tolerance=0.6
                )
                
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, 
                    face_encoding
                )
                
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    # Face recognized
                    metadata = self.known_face_metadata[best_match_index].copy()
                    metadata['confidence'] = float(1 - face_distances[best_match_index])
                    metadata['face_location'] = face_locations[i]  # (top, right, bottom, left)
                    recognized_faces.append(metadata)
                else:
                    # Unknown face
                    unknown_face = {
                        'id': None,
                        'name': 'Unknown',
                        'employee_id': 'N/A',
                        'department': 'N/A',
                        'position': 'N/A',
                        'email': 'N/A',
                        'phone': 'N/A',
                        'confidence': 0.0,
                        'face_location': face_locations[i]
                    }
                    recognized_faces.append(unknown_face)
            
            processing_time = time.time() - start_time
            
            # Create result summary
            result = {
                'total_faces_detected': len(face_locations),
                'total_faces_recognized': len([f for f in recognized_faces if f['name'] != 'Unknown']),
                'recognized_faces': recognized_faces,
                'processing_time': processing_time,
                'image_path': image_path
            }
            
            # Save to history
            RecognitionHistory.create(
                test_image_path=image_path,
                recognized_faces=json.dumps(recognized_faces),
                total_faces_detected=len(face_locations),
                total_faces_recognized=len([f for f in recognized_faces if f['name'] != 'Unknown']),
                processing_time=processing_time
            )
            
            return result, None
            
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def create_annotated_image(self, image_path, recognition_result):
        """Create an annotated image with face boxes and labels"""
        try:
            # Load original image
            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            for face in recognition_result['recognized_faces']:
                top, right, bottom, left = face['face_location']
                
                # Draw rectangle around face
                color = (0, 255, 0) if face['name'] != 'Unknown' else (255, 0, 0)
                cv2.rectangle(image, (left, top), (right, bottom), color, 2)
                
                # Draw label
                label = f"{face['name']}"
                if face['name'] != 'Unknown':
                    label += f" ({face['confidence']:.2f})"
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(
                    image, 
                    (left, bottom - 35), 
                    (left + label_size[0], bottom), 
                    color, 
                    cv2.FILLED
                )
                
                # Draw label text
                cv2.putText(
                    image, 
                    label, 
                    (left + 6, bottom - 6), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, 
                    (255, 255, 255), 
                    2
                )
            
            # Save annotated image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            annotated_path = os.path.join(
                os.path.dirname(image_path), 
                f"{base_name}_annotated.jpg"
            )
            
            cv2.imwrite(annotated_path, image)
            return annotated_path
            
        except Exception as e:
            print(f"Error creating annotated image: {str(e)}")
            return None
    
    def refresh_known_faces(self):
        """Refresh the known faces cache"""
        self.load_known_faces()
        return len(self.known_face_encodings)

# Utility functions
def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_upload_directories():
    """Ensure upload directories exist"""
    directories = [
        'uploads',
        'uploads/known_faces',
        'uploads/test_images'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def validate_image_file(file_path):
    """Validate if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except:
        return False
