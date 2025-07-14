from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import uuid
import time
from werkzeug.utils import secure_filename
from recognizer import recognize_faces_in_image, get_known_faces_info, refresh_encodings
from metadata_handler import get_person_metadata, get_all_people, add_person_metadata

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure upload and output folders
UPLOAD_FOLDER = '../test_images'
OUTPUT_FOLDER = '../outputs'
KNOWN_FACES_FOLDER = '../known_faces'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FACES_FOLDER, exist_ok=True)

# Configure file upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Main page with file upload interface.
    """
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'known_faces_info': get_known_faces_info()
    })

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    Upload and process group photo for face recognition.
    """
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, or GIF'}), 400

        # Get optional parameters
        tolerance = float(request.form.get('tolerance', 0.5))
        tolerance = max(0.3, min(1.0, tolerance))  # Clamp between 0.3 and 1.0

        # Save uploaded image with secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(image_path)

        print(f"Processing uploaded image: {unique_filename}")

        # Run face recognition
        recognized_names, annotated_image_path = recognize_faces_in_image(image_path, tolerance)

        if annotated_image_path is None:
            return jsonify({'error': 'Failed to process image'}), 500

        # Build detailed response with metadata
        persons = []
        for name in recognized_names:
            person_info = get_person_metadata(name)
            if person_info:
                persons.append(person_info)
            else:
                persons.append({
                    'name': name,
                    'status': 'unknown',
                    'message': 'No metadata found for this person'
                })

        # Count statistics
        total_faces = len(recognized_names)
        known_faces = len([p for p in persons if p.get('status') != 'unknown'])
        unknown_faces = total_faces - known_faces

        response_data = {
            'success': True,
            'statistics': {
                'total_faces_detected': total_faces,
                'known_faces': known_faces,
                'unknown_faces': unknown_faces
            },
            'recognized_people': persons,
            'annotated_image_url': f"/api/annotated/{os.path.basename(annotated_image_path)}",
            'original_filename': filename,
            'processing_info': {
                'tolerance_used': tolerance,
                'timestamp': time.time()
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in upload_image: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/annotated/<filename>')
def get_annotated_image(filename):
    """
    Serve annotated images.
    """
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Annotated image not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving image: {str(e)}'}), 500

@app.route('/api/known-faces')
def get_known_faces():
    """
    Get information about known faces and their metadata.
    """
    try:
        faces_info = get_known_faces_info()
        all_metadata = get_all_people()
        
        # Combine face detection info with metadata
        faces_with_metadata = []
        for name in faces_info['known_names']:
            metadata = get_person_metadata(name)
            face_info = {
                'name': name,
                'has_metadata': metadata is not None,
                'metadata': metadata
            }
            faces_with_metadata.append(face_info)
        
        return jsonify({
            'total_faces': faces_info['total_faces'],
            'encodings_cached': faces_info['encodings_cached'],
            'faces': faces_with_metadata
        })
    except Exception as e:
        return jsonify({'error': f'Error fetching known faces: {str(e)}'}), 500

@app.route('/api/refresh-encodings', methods=['POST'])
def refresh_face_encodings():
    """
    Refresh face encodings cache.
    """
    try:
        refresh_encodings()
        return jsonify({'message': 'Face encodings cache refreshed successfully'})
    except Exception as e:
        return jsonify({'error': f'Error refreshing encodings: {str(e)}'}), 500

@app.route('/api/metadata/<name>', methods=['GET'])
def get_metadata(name):
    """
    Get metadata for a specific person.
    """
    try:
        metadata = get_person_metadata(name)
        if metadata:
            return jsonify(metadata)
        else:
            return jsonify({'error': 'Person not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error fetching metadata: {str(e)}'}), 500

@app.route('/api/metadata/<name>', methods=['POST'])
def update_metadata(name):
    """
    Update metadata for a specific person.
    """
    try:
        metadata = request.get_json()
        if not metadata:
            return jsonify({'error': 'No metadata provided'}), 400
        
        add_person_metadata(name, metadata)
        return jsonify({'message': f'Metadata updated for {name}'})
    except Exception as e:
        return jsonify({'error': f'Error updating metadata: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

if __name__ == '__main__':
    print("=== Face Recognition Web App ===")
    print("Starting Flask server...")
    
    # Display startup information
    faces_info = get_known_faces_info()
    print(f"Known faces loaded: {faces_info['total_faces']}")
    print(f"Known names: {faces_info['known_names']}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
