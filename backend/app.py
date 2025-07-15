from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pickle
from werkzeug.utils import secure_filename
import json

# Import our modules
from models import init_database, KnownFace, RecognitionHistory
from face_processor import FaceProcessor, allowed_file, ensure_upload_directories, validate_image_file
from utils import (
    generate_unique_filename, 
    get_file_info, 
    create_response, 
    validate_metadata,
    log_activity,
    get_system_stats,
    compress_image
)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app, origins=['http://localhost:3000'])

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
UPLOAD_FOLDERS = {
    'known_faces': 'uploads/known_faces',
    'test_images': 'uploads/test_images'
}

# Global face processor instance
face_processor = None

def initialize_app():
    """Initialize the application"""
    global face_processor
    
    # Initialize database
    init_database()
    
    # Ensure upload directories exist
    ensure_upload_directories()
    
    # Initialize face processor
    face_processor = FaceProcessor()
    
    log_activity("SYSTEM", "Application initialized successfully")

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return create_response(
        success=True,
        message="Face Recognition API is running",
        data={
            "status": "healthy",
            "known_faces_loaded": len(face_processor.known_face_encodings) if face_processor else 0
        }
    )

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = get_system_stats()
        return create_response(
            success=True,
            message="System statistics retrieved",
            data=stats
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving system statistics",
            error=str(e)
        ), 500

# Admin Panel Routes

@app.route('/api/admin/upload-face', methods=['POST'])
def upload_known_face():
    """Upload a known face with metadata"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return create_response(
                success=False,
                message="No image file provided"
            ), 400
        
        file = request.files['image']
        if file.filename == '':
            return create_response(
                success=False,
                message="No file selected"
            ), 400
        
        # Validate file type
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return create_response(
                success=False,
                message="Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
            ), 400
        
        # Get metadata from form
        name = request.form.get('name', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        department = request.form.get('department', '').strip()
        position = request.form.get('position', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate required metadata
        metadata = {
            'name': name,
            'employee_id': employee_id,
            'department': department,
            'position': position,
            'email': email,
            'phone': phone
        }
        
        validation_errors = validate_metadata(metadata, required_fields=['name'])
        if validation_errors:
            return create_response(
                success=False,
                message="Validation errors",
                error=validation_errors
            ), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDERS['known_faces'], unique_filename)
        
        file.save(file_path)
        
        # Validate image file
        if not validate_image_file(file_path):
            os.remove(file_path)
            return create_response(
                success=False,
                message="Invalid image file"
            ), 400
        
        # Compress image if needed
        compressed_path = file_path.replace('.', '_compressed.')
        compress_success, compress_error = compress_image(file_path, compressed_path)
        
        if compress_success:
            os.remove(file_path)
            file_path = compressed_path
        
        # Process image for face encoding
        face_encoding, error = face_processor.process_image_for_known_face(file_path)
        
        if error:
            os.remove(file_path)
            return create_response(
                success=False,
                message=error
            ), 400
        
        # Serialize face encoding for storage
        face_encoding_blob = pickle.dumps(face_encoding)
        
        # Save to database
        face_id = KnownFace.create(
            name=name,
            employee_id=employee_id if employee_id else None,
            department=department if department else None,
            position=position if position else None,
            email=email if email else None,
            phone=phone if phone else None,
            image_path=file_path,
            face_encoding=face_encoding_blob
        )
        
        if face_id is None:
            os.remove(file_path)
            return create_response(
                success=False,
                message="Employee ID already exists or database error"
            ), 400
        
        # Refresh face processor with new data
        face_processor.refresh_known_faces()
        
        log_activity("ADMIN", f"New face added: {name} (ID: {face_id})")
        
        return create_response(
            success=True,
            message=f"Face added successfully for {name}",
            data={
                'face_id': face_id,
                'name': name,
                'employee_id': employee_id,
                'file_info': get_file_info(file_path)
            }
        )
        
    except Exception as e:
        log_activity("ERROR", f"Error uploading face: {str(e)}")
        return create_response(
            success=False,
            message="Internal server error",
            error=str(e)
        ), 500

@app.route('/api/admin/faces', methods=['GET'])
def get_known_faces():
    """Get all known faces"""
    try:
        faces = KnownFace.get_all()
        
        # Add file info to each face
        for face in faces:
            if os.path.exists(face['image_path']):
                face['file_info'] = get_file_info(face['image_path'])
            else:
                face['file_info'] = None
        
        return create_response(
            success=True,
            message=f"Retrieved {len(faces)} known faces",
            data=faces
        )
        
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving known faces",
            error=str(e)
        ), 500

@app.route('/api/admin/faces/<int:face_id>', methods=['DELETE'])
def delete_known_face(face_id):
    """Delete a known face"""
    try:
        # Get face details before deletion
        face = KnownFace.get_by_id(face_id)
        if not face:
            return create_response(
                success=False,
                message="Face not found"
            ), 404
        
        # Delete from database (this also removes the image file)
        success = KnownFace.delete(face_id)
        
        if success:
            # Refresh face processor
            face_processor.refresh_known_faces()
            
            log_activity("ADMIN", f"Face deleted: {face['name']} (ID: {face_id})")
            
            return create_response(
                success=True,
                message=f"Face deleted successfully: {face['name']}"
            )
        else:
            return create_response(
                success=False,
                message="Error deleting face"
            ), 500
            
    except Exception as e:
        return create_response(
            success=False,
            message="Error deleting face",
            error=str(e)
        ), 500

# Face Recognition Routes

@app.route('/api/recognize', methods=['POST'])
def recognize_faces():
    """Recognize faces in uploaded image"""
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return create_response(
                success=False,
                message="No image file provided"
            ), 400
        
        file = request.files['image']
        if file.filename == '':
            return create_response(
                success=False,
                message="No file selected"
            ), 400
        
        # Validate file type
        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return create_response(
                success=False,
                message="Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS)
            ), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDERS['test_images'], unique_filename)
        
        file.save(file_path)
        
        # Validate image file
        if not validate_image_file(file_path):
            os.remove(file_path)
            return create_response(
                success=False,
                message="Invalid image file"
            ), 400
        
        # Process image for face recognition
        result, error = face_processor.recognize_faces_in_image(file_path)
        
        if error:
            os.remove(file_path)
            return create_response(
                success=False,
                message=error
            ), 400
        
        # Create annotated image
        annotated_path = face_processor.create_annotated_image(file_path, result)
        if annotated_path:
            result['annotated_image_path'] = annotated_path
        
        log_activity(
            "RECOGNITION", 
            f"Face recognition completed: {result['total_faces_detected']} faces detected, "
            f"{result['total_faces_recognized']} recognized"
        )
        
        return create_response(
            success=True,
            message="Face recognition completed",
            data=result
        )
        
    except Exception as e:
        log_activity("ERROR", f"Error in face recognition: {str(e)}")
        return create_response(
            success=False,
            message="Error processing image",
            error=str(e)
        ), 500

@app.route('/api/recognition-history', methods=['GET'])
def get_recognition_history():
    """Get recognition history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = RecognitionHistory.get_all(limit=limit)
        
        # Parse JSON strings and add file info
        for record in history:
            record['recognized_faces'] = json.loads(record['recognized_faces'])
            
            if os.path.exists(record['test_image_path']):
                record['file_info'] = get_file_info(record['test_image_path'])
            else:
                record['file_info'] = None
        
        return create_response(
            success=True,
            message=f"Retrieved {len(history)} recognition records",
            data=history
        )
        
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving recognition history",
            error=str(e)
        ), 500

# File serving routes

@app.route('/api/images/known/<filename>')
def serve_known_face_image(filename):
    """Serve known face images"""
    return send_from_directory(UPLOAD_FOLDERS['known_faces'], filename)

@app.route('/api/images/test/<filename>')
def serve_test_image(filename):
    """Serve test images"""
    return send_from_directory(UPLOAD_FOLDERS['test_images'], filename)

# Error handlers

@app.errorhandler(413)
def too_large(e):
    return create_response(
        success=False,
        message="File too large. Maximum size is 16MB"
    ), 413

@app.errorhandler(404)
def not_found(e):
    return create_response(
        success=False,
        message="Endpoint not found"
    ), 404

@app.errorhandler(500)
def internal_error(e):
    return create_response(
        success=False,
        message="Internal server error"
    ), 500

# Application startup
if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
