from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import pickle
from werkzeug.utils import secure_filename
import json
import base64
import io
import cv2
import numpy as np
from PIL import Image

# Import our modules
from models import init_database, KnownFace, RecognitionHistory
from face_processor import FaceProcessor, allowed_file, ensure_upload_directories, validate_image_file, get_image_info
from export_utils import export_manager
from utils import (
    generate_unique_filename,
    get_file_info,
    create_response,
    validate_metadata,
    validate_metadata_enhanced,
    validate_file_upload,
    validate_image_content,
    log_activity,
    get_system_stats,
    check_system_resources,
    compress_image,
    performance_monitor
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

@app.route('/api/system/health', methods=['GET'])
def system_health():
    """Get system health and performance metrics"""
    try:
        # Get basic system stats
        stats = get_system_stats()

        # Get resource usage
        resources = check_system_resources()

        # Get face processor info
        processor_info = face_processor.get_system_info()

        # Combine all information
        health_data = {
            'system_stats': stats,
            'resources': resources,
            'face_processor': processor_info,
            'timestamp': datetime.now().isoformat(),
            'status': resources.get('status', 'unknown')
        }

        return create_response(
            success=True,
            message="System health retrieved successfully",
            data=health_data
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving system health",
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

        # Enhanced file validation
        file_valid, file_error = validate_file_upload(file, ALLOWED_EXTENSIONS, max_size_mb=10)
        if not file_valid:
            return create_response(
                success=False,
                message=file_error
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
        
        # Use enhanced validation
        is_valid, validation_errors = validate_metadata_enhanced(metadata)
        if not is_valid:
            return create_response(
                success=False,
                message="Validation failed",
                errors=validation_errors
            ), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(filename)
        file_path = os.path.join(UPLOAD_FOLDERS['known_faces'], unique_filename)
        
        file.save(file_path)

        # Enhanced image validation
        if not validate_image_file(file_path):
            os.remove(file_path)
            return create_response(
                success=False,
                message="Invalid image file format"
            ), 400

        # Validate image content and properties
        content_valid, content_error = validate_image_content(file_path)
        if not content_valid:
            os.remove(file_path)
            return create_response(
                success=False,
                message=content_error
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

@app.route('/api/admin/bulk-upload', methods=['POST'])
def bulk_upload_faces():
    """Bulk upload multiple faces with metadata"""
    try:
        # Check if files are present
        if 'images' not in request.files:
            return create_response(
                success=False,
                message="No images provided"
            ), 400

        files = request.files.getlist('images')
        metadata_json = request.form.get('metadata', '[]')

        try:
            metadata_list = json.loads(metadata_json)
        except json.JSONDecodeError:
            return create_response(
                success=False,
                message="Invalid metadata format"
            ), 400

        if len(files) != len(metadata_list):
            return create_response(
                success=False,
                message="Number of images and metadata entries must match"
            ), 400

        results = []
        success_count = 0
        error_count = 0

        for i, (file, metadata) in enumerate(zip(files, metadata_list)):
            try:
                # Validate file
                if not file or file.filename == '':
                    results.append({
                        'index': i,
                        'filename': 'unknown',
                        'success': False,
                        'error': 'No file provided'
                    })
                    error_count += 1
                    continue

                if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': 'Invalid file type'
                    })
                    error_count += 1
                    continue

                # Validate metadata
                validation_error = validate_metadata(metadata)
                if validation_error:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': validation_error
                    })
                    error_count += 1
                    continue

                # Save file
                filename = secure_filename(file.filename)
                unique_filename = generate_unique_filename(filename)
                file_path = os.path.join(UPLOAD_FOLDERS['known_faces'], unique_filename)

                file.save(file_path)

                # Validate image file
                if not validate_image_file(file_path):
                    os.remove(file_path)
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': 'Invalid image file'
                    })
                    error_count += 1
                    continue

                # Process image for face encoding
                face_encoding, error = face_processor.process_image_for_known_face(file_path)

                if error:
                    os.remove(file_path)
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': error
                    })
                    error_count += 1
                    continue

                # Serialize face encoding for storage
                face_encoding_blob = pickle.dumps(face_encoding)

                # Save to database
                face_id = KnownFace.create(
                    name=metadata.get('name', '').strip(),
                    employee_id=metadata.get('employee_id', '').strip() or None,
                    department=metadata.get('department', '').strip() or None,
                    position=metadata.get('position', '').strip() or None,
                    email=metadata.get('email', '').strip() or None,
                    phone=metadata.get('phone', '').strip() or None,
                    image_path=file_path,
                    face_encoding=face_encoding_blob
                )

                if face_id is None:
                    os.remove(file_path)
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': 'Employee ID already exists or database error'
                    })
                    error_count += 1
                    continue

                results.append({
                    'index': i,
                    'filename': file.filename,
                    'success': True,
                    'face_id': face_id,
                    'name': metadata.get('name', '').strip()
                })
                success_count += 1

            except Exception as e:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                results.append({
                    'index': i,
                    'filename': file.filename if file else 'unknown',
                    'success': False,
                    'error': str(e)
                })
                error_count += 1

        # Refresh face processor with new data
        face_processor.refresh_known_faces()

        log_activity("ADMIN", f"Bulk upload completed: {success_count} success, {error_count} errors")

        return create_response(
            success=True,
            message=f"Bulk upload completed: {success_count} successful, {error_count} failed",
            data={
                'results': results,
                'summary': {
                    'total': len(files),
                    'success': success_count,
                    'errors': error_count
                }
            }
        )

    except Exception as e:
        log_activity("ERROR", f"Error in bulk upload: {str(e)}")
        return create_response(
            success=False,
            message="Internal server error during bulk upload",
            error=str(e)
        ), 500

@app.route('/api/admin/search', methods=['GET'])
def search_faces():
    """Search faces with filters and pagination"""
    try:
        query = request.args.get('q', '')
        department = request.args.get('department', '')
        position = request.args.get('position', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        faces, total_count = KnownFace.search_faces(
            query=query,
            department=department,
            position=position,
            limit=limit,
            offset=offset
        )

        return create_response(
            success=True,
            message="Search completed successfully",
            data={
                'faces': faces,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        )

    except Exception as e:
        log_activity("ERROR", f"Error searching faces: {str(e)}")
        return create_response(
            success=False,
            message="Error searching faces",
            error=str(e)
        ), 500

@app.route('/api/admin/departments', methods=['GET'])
def get_departments():
    """Get all unique departments"""
    try:
        departments = KnownFace.get_departments()
        return create_response(
            success=True,
            message="Departments retrieved successfully",
            data=departments
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving departments",
            error=str(e)
        ), 500

@app.route('/api/admin/positions', methods=['GET'])
def get_positions():
    """Get all unique positions"""
    try:
        positions = KnownFace.get_positions()
        return create_response(
            success=True,
            message="Positions retrieved successfully",
            data=positions
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving positions",
            error=str(e)
        ), 500

@app.route('/api/admin/statistics', methods=['GET'])
def get_face_statistics():
    """Get face database statistics"""
    try:
        stats = KnownFace.get_statistics()
        return create_response(
            success=True,
            message="Statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving statistics",
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

@app.route('/api/history/search', methods=['GET'])
def search_history():
    """Search recognition history with filters and pagination"""
    try:
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        min_faces = int(request.args.get('min_faces', 0))
        max_faces = int(request.args.get('max_faces', 999))
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        history, total_count = RecognitionHistory.search_history(
            start_date=start_date,
            end_date=end_date,
            min_faces=min_faces,
            max_faces=max_faces,
            limit=limit,
            offset=offset
        )

        return create_response(
            success=True,
            message="History search completed successfully",
            data={
                'history': history,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        )

    except Exception as e:
        log_activity("ERROR", f"Error searching history: {str(e)}")
        return create_response(
            success=False,
            message="Error searching history",
            error=str(e)
        ), 500

@app.route('/api/history/statistics', methods=['GET'])
def get_history_statistics():
    """Get recognition history statistics"""
    try:
        stats = RecognitionHistory.get_statistics()
        return create_response(
            success=True,
            message="History statistics retrieved successfully",
            data=stats
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Error retrieving history statistics",
            error=str(e)
        ), 500

# Camera and Real-time Recognition Routes

@app.route('/api/camera/capture', methods=['POST'])
def camera_capture():
    """Process image from camera capture (base64 encoded)"""
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return create_response(
                success=False,
                message="No image data provided"
            ), 400

        # Decode base64 image
        try:
            # Remove data URL prefix if present
            image_data = data['image']
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            # Decode base64
            image_bytes = base64.b64decode(image_data)

            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Save temporary file
            temp_filename = generate_unique_filename('camera_capture.jpg')
            temp_path = os.path.join(UPLOAD_FOLDERS['test_images'], temp_filename)
            pil_image.save(temp_path, 'JPEG', quality=90)

        except Exception as e:
            return create_response(
                success=False,
                message="Invalid image data",
                error=str(e)
            ), 400

        # Validate image
        if not validate_image_file(temp_path):
            os.remove(temp_path)
            return create_response(
                success=False,
                message="Invalid image format"
            ), 400

        # Process image for face recognition
        result, error = face_processor.recognize_faces_in_image(temp_path)

        if error:
            os.remove(temp_path)
            return create_response(
                success=False,
                message=error
            ), 400

        # Create annotated image
        annotated_path = face_processor.create_annotated_image(temp_path, result)
        if annotated_path:
            result['annotated_image_path'] = annotated_path

        # Add image info
        result['image_info'] = get_image_info(temp_path)

        log_activity("CAMERA", f"Camera capture processed: {result['total_faces_detected']} faces detected")

        return create_response(
            success=True,
            message="Camera capture processed successfully",
            data=result
        )

    except Exception as e:
        log_activity("ERROR", f"Error in camera capture: {str(e)}")
        return create_response(
            success=False,
            message="Error processing camera capture",
            error=str(e)
        ), 500

@app.route('/api/camera/stream-frame', methods=['POST'])
def process_stream_frame():
    """Process a single frame from video stream"""
    try:
        data = request.get_json()

        if not data or 'frame' not in data:
            return create_response(
                success=False,
                message="No frame data provided"
            ), 400

        # Decode base64 frame
        try:
            frame_data = data['frame']
            if frame_data.startswith('data:image'):
                frame_data = frame_data.split(',')[1]

            frame_bytes = base64.b64decode(frame_data)

            # Convert to numpy array for OpenCV
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return create_response(
                    success=False,
                    message="Could not decode frame"
                ), 400

            # Convert BGR to RGB for face_recognition
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Save temporary frame
            temp_filename = generate_unique_filename('stream_frame.jpg')
            temp_path = os.path.join(UPLOAD_FOLDERS['test_images'], temp_filename)

            # Convert back to PIL and save
            pil_image = Image.fromarray(frame_rgb)
            pil_image.save(temp_path, 'JPEG', quality=85)

        except Exception as e:
            return create_response(
                success=False,
                message="Invalid frame data",
                error=str(e)
            ), 400

        # Process frame for face recognition (faster settings for real-time)
        # Temporarily adjust settings for speed
        original_model = face_processor.face_detection_model
        face_processor.face_detection_model = 'hog'  # Faster for real-time

        result, error = face_processor.recognize_faces_in_image(temp_path)

        # Restore original settings
        face_processor.face_detection_model = original_model

        if error:
            os.remove(temp_path)
            return create_response(
                success=False,
                message=error
            ), 400

        # For streaming, we don't need to save the frame permanently
        # Clean up immediately after processing
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Return lightweight result for real-time processing
        lightweight_result = {
            'total_faces_detected': result['total_faces_detected'],
            'total_faces_recognized': result['total_faces_recognized'],
            'recognized_faces': [
                {
                    'name': face['name'],
                    'confidence': face['confidence'],
                    'face_location': face['face_location'],
                    'employee_id': face.get('employee_id', 'N/A'),
                    'department': face.get('department', 'N/A')
                }
                for face in result['recognized_faces']
            ],
            'processing_time': result['processing_time']
        }

        return create_response(
            success=True,
            message="Frame processed successfully",
            data=lightweight_result
        )

    except Exception as e:
        return create_response(
            success=False,
            message="Error processing stream frame",
            error=str(e)
        ), 500

# Export and Download Routes

@app.route('/api/export/results', methods=['POST'])
def export_recognition_results():
    """Export recognition results in various formats"""
    try:
        data = request.get_json()

        if not data or 'results' not in data:
            return create_response(
                success=False,
                message="No results data provided"
            ), 400

        format_type = data.get('format', 'json').lower()
        include_images = data.get('include_images', False)
        results = data['results']

        if format_type not in ['json', 'csv', 'pdf']:
            return create_response(
                success=False,
                message="Unsupported export format. Use 'json', 'csv', or 'pdf'"
            ), 400

        # Export the results
        exported_data, filename = export_manager.export_recognition_results(
            results, format_type, include_images
        )

        # Set appropriate content type
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv',
            'pdf': 'application/pdf'
        }

        response = Response(
            exported_data,
            mimetype=content_types[format_type],
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': len(exported_data)
            }
        )

        log_activity("EXPORT", f"Recognition results exported as {format_type}: {filename}")
        return response

    except Exception as e:
        log_activity("ERROR", f"Error exporting results: {str(e)}")
        return create_response(
            success=False,
            message="Error exporting results",
            error=str(e)
        ), 500

@app.route('/api/export/database', methods=['GET'])
def export_face_database():
    """Export known faces database"""
    try:
        format_type = request.args.get('format', 'json').lower()

        if format_type not in ['json', 'csv']:
            return create_response(
                success=False,
                message="Unsupported export format. Use 'json' or 'csv'"
            ), 400

        # Get all known faces
        faces_data = KnownFace.get_all()

        # Remove sensitive data (face encodings) for export
        clean_faces_data = []
        for face in faces_data:
            clean_face = {
                'id': face['id'],
                'name': face['name'],
                'employee_id': face['employee_id'],
                'department': face['department'],
                'position': face['position'],
                'email': face['email'],
                'phone': face['phone'],
                'created_at': face['created_at']
            }
            clean_faces_data.append(clean_face)

        # Export the database
        exported_data, filename = export_manager.export_face_database(
            clean_faces_data, format_type
        )

        # Set appropriate content type
        content_types = {
            'json': 'application/json',
            'csv': 'text/csv'
        }

        response = Response(
            exported_data,
            mimetype=content_types[format_type],
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': len(exported_data)
            }
        )

        log_activity("EXPORT", f"Face database exported as {format_type}: {filename}")
        return response

    except Exception as e:
        log_activity("ERROR", f"Error exporting database: {str(e)}")
        return create_response(
            success=False,
            message="Error exporting database",
            error=str(e)
        ), 500

@app.route('/api/download/image/<path:image_path>')
def download_image(image_path):
    """Download processed images"""
    try:
        # Security check - ensure the path is within allowed directories
        allowed_dirs = ['uploads/test_images', 'uploads/known_faces']

        full_path = None
        for allowed_dir in allowed_dirs:
            potential_path = os.path.join(allowed_dir, os.path.basename(image_path))
            if os.path.exists(potential_path):
                full_path = potential_path
                break

        if not full_path:
            return create_response(
                success=False,
                message="Image not found"
            ), 404

        # Get file info
        file_info = get_file_info(full_path)

        return send_from_directory(
            os.path.dirname(full_path),
            os.path.basename(full_path),
            as_attachment=True,
            download_name=f"face_recognition_{os.path.basename(full_path)}"
        )

    except Exception as e:
        log_activity("ERROR", f"Error downloading image: {str(e)}")
        return create_response(
            success=False,
            message="Error downloading image",
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
