import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pickle
import json
import time
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict, Optional, Any
from models import KnownFace, RecognitionHistory
from utils import performance_monitor

class FaceProcessor:
    def __init__(self):
        self.known_face_data = []  # Store face data for LBPH training
        self.known_face_metadata = []
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.confidence_threshold = 100  # LBPH confidence threshold (lower is better)
        self.max_image_size = (1920, 1080)  # Max resolution for processing
        self.face_size = (100, 100)  # Standard face size for LBPH training
        self.logger = logging.getLogger(__name__)
        self.is_trained = False
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known faces from database and train LBPH recognizer"""
        try:
            faces = KnownFace.get_all()
            self.known_face_data = []
            self.known_face_metadata = []

            face_images = []
            face_labels = []

            for idx, face in enumerate(faces):
                try:
                    # Load and process face image for LBPH training
                    if os.path.exists(face['image_path']):
                        face_img = self._extract_face_for_training(face['image_path'])
                        if face_img is not None:
                            face_images.append(face_img)
                            face_labels.append(idx)  # Use index as label

                            # Store metadata with label mapping
                            metadata = {
                                'id': face['id'],
                                'label': idx,
                                'name': face['name'],
                                'employee_id': face['employee_id'],
                                'department': face['department'],
                                'position': face['position'],
                                'email': face['email'],
                                'phone': face['phone'],
                                'image_path': face['image_path']
                            }
                            self.known_face_metadata.append(metadata)
                        else:
                            self.logger.warning(f"Could not extract face from {face['image_path']}")
                    else:
                        self.logger.warning(f"Image file not found: {face['image_path']}")
                except Exception as e:
                    self.logger.error(f"Error processing face {face['id']}: {str(e)}")

            # Train LBPH recognizer if we have face data
            if len(face_images) > 0:
                self.face_recognizer.train(face_images, np.array(face_labels))
                self.is_trained = True
                self.logger.info(f"LBPH recognizer trained with {len(face_images)} faces")
            else:
                self.is_trained = False
                self.logger.warning("No valid face images found for training")

        except Exception as e:
            self.logger.error(f"Error loading known faces: {str(e)}")
            self.is_trained = False

    def _extract_face_for_training(self, image_path: str) -> Optional[np.ndarray]:
        """Extract and prepare face for LBPH training"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces using Haar cascade
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(faces) == 0:
                self.logger.warning(f"No face detected in {image_path}")
                return None

            if len(faces) > 1:
                self.logger.warning(f"Multiple faces detected in {image_path}, using largest")

            # Use the largest face (assuming it's the main subject)
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face

            # Extract face region
            face_roi = gray[y:y+h, x:x+w]

            # Resize to standard size for LBPH
            face_resized = cv2.resize(face_roi, self.face_size)

            # Apply histogram equalization for better recognition
            face_equalized = cv2.equalizeHist(face_resized)

            return face_equalized

        except Exception as e:
            self.logger.error(f"Error extracting face from {image_path}: {str(e)}")
            return None
    
    def _preprocess_image(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Preprocess image for better face detection"""
        try:
            # Load and validate image
            if not os.path.exists(image_path):
                return None, "Image file not found"

            # Load with PIL for better format support
            pil_image = Image.open(image_path)

            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Resize if too large for performance
            if pil_image.size[0] > self.max_image_size[0] or pil_image.size[1] > self.max_image_size[1]:
                pil_image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                self.logger.info(f"Resized image to {pil_image.size} for processing")

            # Enhance image quality for better face detection
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)

            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.1)

            # Convert to numpy array for face_recognition
            image_array = np.array(pil_image)

            return image_array, None

        except Exception as e:
            self.logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            return None, f"Error preprocessing image: {str(e)}"

    @performance_monitor
    def process_image_for_known_face(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
        """Process an image to extract face for LBPH training"""
        try:
            # Extract face for training
            face_data = self._extract_face_for_training(image_path)

            if face_data is None:
                return None, "No face detected in the image. Please ensure the image contains a clear, well-lit face."

            self.logger.info(f"Successfully processed face from {image_path}")
            return face_data, None

        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {str(e)}")
            return None, f"Error processing image: {str(e)}"
    
    def _calculate_confidence_score(self, lbph_confidence: float) -> float:
        """Calculate confidence score from LBPH confidence (lower is better)"""
        # LBPH confidence: lower values mean better match
        # Convert to percentage where higher is better
        if lbph_confidence > self.confidence_threshold:
            return 0.0

        # Normalize to 0-100 scale (invert since lower LBPH confidence is better)
        confidence = max(0, (self.confidence_threshold - lbph_confidence) / self.confidence_threshold * 100)
        return round(confidence, 2)

    @performance_monitor
    def recognize_faces_in_image(self, image_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Recognize faces in a test image using LBPH with enhanced performance and accuracy"""
        start_time = time.time()

        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                return None, "Could not load image"

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Check if we have trained recognizer
            if not self.is_trained:
                self.logger.warning("LBPH recognizer not trained - no known faces in database")

            # Detect faces using Haar cascade
            face_locations = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            if len(face_locations) == 0:
                return {
                    'total_faces_detected': 0,
                    'total_faces_recognized': 0,
                    'recognized_faces': [],
                    'processing_time': time.time() - start_time,
                    'image_path': image_path,
                    'message': 'No faces detected in the image'
                }, None

            # Limit processing for performance (max 50 faces as per requirements)
            if len(face_locations) > 50:
                self.logger.warning(f"Too many faces detected ({len(face_locations)}), processing first 50")
                face_locations = face_locations[:50]

            recognized_faces = []

            # Process each detected face
            for i, (x, y, w, h) in enumerate(face_locations):
                # Convert OpenCV rectangle to face_recognition format (top, right, bottom, left)
                face_location = (y, x + w, y + h, x)
                face_info = self._match_face_lbph(gray, (x, y, w, h), face_location, i)
                recognized_faces.append(face_info)

            processing_time = time.time() - start_time

            # Create result summary
            result = {
                'total_faces_detected': len(face_locations),
                'total_faces_recognized': len([f for f in recognized_faces if f['name'] != 'Unknown']),
                'recognized_faces': recognized_faces,
                'processing_time': round(processing_time, 3),
                'image_path': image_path,
                'image_dimensions': f"{image.shape[1]}x{image.shape[0]}",
                'detection_model': 'haar_cascade',
                'recognition_tolerance': self.confidence_threshold
            }

            # Save to history
            try:
                RecognitionHistory.create(
                    test_image_path=image_path,
                    recognized_faces=json.dumps(recognized_faces),
                    total_faces_detected=len(face_locations),
                    total_faces_recognized=len([f for f in recognized_faces if f['name'] != 'Unknown']),
                    processing_time=processing_time
                )
            except Exception as e:
                self.logger.error(f"Error saving recognition history: {str(e)}")

            self.logger.info(f"Recognition completed: {len(face_locations)} faces detected, "
                           f"{len([f for f in recognized_faces if f['name'] != 'Unknown'])} recognized "
                           f"in {processing_time:.3f}s")

            return result, None

        except Exception as e:
            self.logger.error(f"Error recognizing faces in {image_path}: {str(e)}")
            return None, f"Error processing image: {str(e)}"

    def _match_face_lbph(self, gray_image: np.ndarray, face_rect: Tuple[int, int, int, int],
                        face_location: Tuple[int, int, int, int], face_index: int) -> Dict[str, Any]:
        """Match a face using LBPH recognizer"""
        try:
            if not self.is_trained:
                return self._create_unknown_face_info(face_location, face_index)

            x, y, w, h = face_rect

            # Extract face region
            face_roi = gray_image[y:y+h, x:x+w]

            # Resize to standard size
            face_resized = cv2.resize(face_roi, self.face_size)

            # Apply histogram equalization
            face_equalized = cv2.equalizeHist(face_resized)

            # Predict using LBPH recognizer
            label, confidence = self.face_recognizer.predict(face_equalized)

            # Check if confidence is within threshold
            if confidence <= self.confidence_threshold and label < len(self.known_face_metadata):
                # Face recognized
                metadata = self.known_face_metadata[label].copy()
                metadata['confidence'] = self._calculate_confidence_score(confidence)
                metadata['face_location'] = face_location
                metadata['lbph_confidence'] = round(float(confidence), 4)
                metadata['face_index'] = face_index
                return metadata
            else:
                # Unknown face
                return self._create_unknown_face_info(face_location, face_index, confidence)

        except Exception as e:
            self.logger.error(f"Error matching face {face_index}: {str(e)}")
            return self._create_unknown_face_info(face_location, face_index)



    def _create_unknown_face_info(self, face_location: Tuple[int, int, int, int], face_index: int, lbph_confidence: float = None) -> Dict[str, Any]:
        """Create face info for unknown faces"""
        return {
            'id': None,
            'name': 'Unknown',
            'employee_id': 'N/A',
            'department': 'N/A',
            'position': 'N/A',
            'email': 'N/A',
            'phone': 'N/A',
            'confidence': 0.0,
            'face_location': face_location,
            'lbph_confidence': round(float(lbph_confidence), 4) if lbph_confidence is not None else None,
            'face_index': face_index,
            'image_path': None
        }
            

    
    def create_annotated_image(self, image_path: str, recognition_result: Dict[str, Any]) -> Optional[str]:
        """Create an enhanced annotated image with face boxes and labels"""
        try:
            # Load original image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Could not load image: {image_path}")
                return None

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Define colors for different confidence levels
            colors = {
                'high': (0, 255, 0),      # Green for high confidence (>80%)
                'medium': (255, 165, 0),   # Orange for medium confidence (50-80%)
                'low': (255, 255, 0),      # Yellow for low confidence (20-50%)
                'unknown': (255, 0, 0)     # Red for unknown faces
            }

            for face in recognition_result['recognized_faces']:
                top, right, bottom, left = face['face_location']

                # Determine color based on confidence
                if face['name'] == 'Unknown':
                    color = colors['unknown']
                    confidence_level = 'unknown'
                elif face['confidence'] >= 80:
                    color = colors['high']
                    confidence_level = 'high'
                elif face['confidence'] >= 50:
                    color = colors['medium']
                    confidence_level = 'medium'
                else:
                    color = colors['low']
                    confidence_level = 'low'

                # Draw rectangle around face with thickness based on confidence
                thickness = 3 if face['name'] != 'Unknown' else 2
                cv2.rectangle(image, (left, top), (right, bottom), color, thickness)

                # Create label with more information
                if face['name'] != 'Unknown':
                    label = f"{face['name']} ({face['confidence']:.1f}%)"
                    if face.get('employee_id') and face['employee_id'] != 'N/A':
                        label += f" - {face['employee_id']}"
                else:
                    label = "Unknown"

                # Calculate label size and position
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                font_thickness = 2
                label_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]

                # Draw label background with padding
                padding = 5
                label_bg_top = bottom - 35
                label_bg_bottom = bottom
                label_bg_left = left
                label_bg_right = left + label_size[0] + (padding * 2)

                cv2.rectangle(
                    image,
                    (label_bg_left, label_bg_top),
                    (label_bg_right, label_bg_bottom),
                    color,
                    cv2.FILLED
                )

                # Draw label text
                cv2.putText(
                    image,
                    label,
                    (left + padding, bottom - 8),
                    font,
                    font_scale,
                    (255, 255, 255),
                    font_thickness
                )

                # Add face index number for reference
                face_index = face.get('face_index', 0)
                index_label = f"#{face_index + 1}"
                cv2.putText(
                    image,
                    index_label,
                    (left + 5, top + 20),
                    font,
                    0.5,
                    color,
                    2
                )

            # Add summary information at the top
            summary = f"Faces: {recognition_result['total_faces_detected']} | Recognized: {recognition_result['total_faces_recognized']} | Time: {recognition_result['processing_time']:.2f}s"
            cv2.putText(
                image,
                summary,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Add background for summary text
            summary_size = cv2.getTextSize(summary, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(
                image,
                (5, 5),
                (summary_size[0] + 15, 40),
                (0, 0, 0),
                cv2.FILLED
            )
            cv2.putText(
                image,
                summary,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            # Save annotated image
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            annotated_path = os.path.join(
                os.path.dirname(image_path),
                f"{base_name}_annotated.jpg"
            )

            success = cv2.imwrite(annotated_path, image)
            if success:
                self.logger.info(f"Annotated image saved: {annotated_path}")
                return annotated_path
            else:
                self.logger.error(f"Failed to save annotated image: {annotated_path}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating annotated image: {str(e)}")
            return None
    
    def refresh_known_faces(self) -> int:
        """Refresh the known faces cache and retrain LBPH recognizer"""
        self.load_known_faces()
        face_count = len(self.known_face_metadata)
        self.logger.info(f"Refreshed known faces cache: {face_count} faces loaded, trained: {self.is_trained}")
        return face_count

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for debugging and monitoring"""
        return {
            'known_faces_count': len(self.known_face_metadata),
            'face_detection_model': 'haar_cascade',
            'recognition_algorithm': 'LBPH',
            'confidence_threshold': self.confidence_threshold,
            'max_image_size': self.max_image_size,
            'face_size': self.face_size,
            'is_trained': self.is_trained,
            'lbph_available': hasattr(cv2, 'face') and hasattr(cv2.face, 'LBPHFaceRecognizer_create')
        }

    def update_settings(self, **kwargs) -> None:
        """Update face processor settings"""
        if 'confidence_threshold' in kwargs:
            self.confidence_threshold = float(kwargs['confidence_threshold'])
            self.logger.info(f"Updated LBPH confidence threshold to {self.confidence_threshold}")

        if 'face_size' in kwargs:
            self.face_size = tuple(kwargs['face_size'])
            self.logger.info(f"Updated face size to {self.face_size}")
            # Need to retrain with new face size
            self.load_known_faces()

        if 'max_image_size' in kwargs:
            self.max_image_size = tuple(kwargs['max_image_size'])
            self.logger.info(f"Updated max image size to {self.max_image_size}")

    def validate_face_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """Validate if an image is suitable for face recognition"""
        try:
            # Check file exists
            if not os.path.exists(image_path):
                return False, "Image file not found"

            # Check file size (max 10MB as per requirements)
            file_size = os.path.getsize(image_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                return False, f"Image file too large ({file_size / (1024*1024):.1f}MB). Maximum size is 10MB."

            # Try to load and validate image
            image, error = self._preprocess_image(image_path)
            if error:
                return False, error

            # Check image dimensions
            height, width = image.shape[:2]
            if width < 100 or height < 100:
                return False, "Image too small. Minimum size is 100x100 pixels."

            return True, None

        except Exception as e:
            return False, f"Error validating image: {str(e)}"

# Utility functions
def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_upload_directories() -> None:
    """Ensure upload directories exist"""
    directories = [
        'uploads',
        'uploads/known_faces',
        'uploads/test_images',
        'uploads/annotated'  # For annotated images
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logging.error(f"Error getting file size for {file_path}: {str(e)}")
        return 0

def validate_image_file(file_path: str) -> bool:
    """Validate if file is a valid image"""
    try:
        with Image.open(file_path) as img:
            img.verify()

        # Additional validation - check if it's a supported format
        with Image.open(file_path) as img:
            if img.format not in ['JPEG', 'PNG', 'BMP', 'GIF']:
                return False

        return True
    except Exception as e:
        logging.error(f"Error validating image file {file_path}: {str(e)}")
        return False

def get_image_info(file_path: str) -> Dict[str, Any]:
    """Get detailed image information"""
    try:
        with Image.open(file_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size': get_file_size(file_path),
                'file_size_mb': round(get_file_size(file_path) / (1024 * 1024), 2)
            }
    except Exception as e:
        logging.error(f"Error getting image info for {file_path}: {str(e)}")
        return {}
