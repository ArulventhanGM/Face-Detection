from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import uuid
import time
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
try:
    CORS(app)  # Enable CORS for frontend integration
except:
    pass  # Continue without CORS if not available

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

def get_sample_metadata():
    """Return sample metadata for demonstration"""
    return {
        "john_doe": {
            "name": "John Doe",
            "email": "john.doe@company.com",
            "role": "Software Engineer",
            "department": "Engineering",
            "employee_id": "EMP001",
            "phone": "+1-555-0123"
        },
        "jane_smith": {
            "name": "Jane Smith",
            "email": "jane.smith@company.com",
            "role": "Product Manager",
            "department": "Product",
            "employee_id": "EMP002",
            "phone": "+1-555-0124"
        }
    }

def get_known_faces_count():
    """Count face images in known_faces directory"""
    face_files = []
    if os.path.exists(KNOWN_FACES_FOLDER):
        for filename in os.listdir(KNOWN_FACES_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                face_files.append(filename)
    return len(face_files), face_files

@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    face_count, face_files = get_known_faces_count()
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'known_faces_info': {
            'total_faces': face_count,
            'known_names': [os.path.splitext(f)[0] for f in face_files],
            'encodings_cached': False
        },
        'demo_mode': True,
        'message': 'Install face_recognition library for full functionality'
    })

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Upload and process group photo for face recognition (demo mode)."""
    try:
        # Check if image is in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, or GIF'}), 400

        # Save uploaded image with secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        image_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(image_path)

        print(f"Demo mode: Processing uploaded image: {unique_filename}")

        # Simulate face recognition results
        face_count, face_files = get_known_faces_count()
        sample_metadata = get_sample_metadata()
        
        # Create demo results
        demo_results = []
        known_names = list(sample_metadata.keys())
        
        # Simulate finding 2-3 faces
        import random
        num_faces = random.randint(2, min(3, len(known_names))) if known_names else 0
        
        for i in range(num_faces):
            if i < len(known_names):
                name = known_names[i]
                demo_results.append(sample_metadata[name])
            else:
                demo_results.append({
                    'name': f'Unknown_Person_{i+1}',
                    'status': 'unknown',
                    'message': 'No metadata found for this person'
                })

        # Add some unknown faces
        if num_faces < 3:
            demo_results.append({
                'name': 'Unknown_Person',
                'status': 'unknown',
                'message': 'No metadata found for this person'
            })

        total_faces = len(demo_results)
        known_faces = len([p for p in demo_results if p.get('status') != 'unknown'])
        unknown_faces = total_faces - known_faces

        response_data = {
            'success': True,
            'demo_mode': True,
            'message': 'This is a demo response. Install face_recognition library for actual face detection.',
            'statistics': {
                'total_faces_detected': total_faces,
                'known_faces': known_faces,
                'unknown_faces': unknown_faces
            },
            'recognized_people': demo_results,
            'annotated_image_url': f"/api/image/{unique_filename}",  # Return original image
            'original_filename': filename,
            'processing_info': {
                'tolerance_used': float(request.form.get('tolerance', 0.5)),
                'timestamp': time.time()
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in upload_image: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/image/<filename>')
def get_image(filename):
    """Serve uploaded images."""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            return send_file(filepath, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error serving image: {str(e)}'}), 500

@app.route('/api/annotated/<filename>')
def get_annotated_image(filename):
    """Serve annotated images (demo mode returns original)."""
    return get_image(filename)

@app.route('/api/known-faces')
def get_known_faces():
    """Get information about known faces and their metadata."""
    try:
        face_count, face_files = get_known_faces_count()
        sample_metadata = get_sample_metadata()
        
        # Combine face detection info with metadata
        faces_with_metadata = []
        for filename in face_files:
            name = os.path.splitext(filename)[0]
            metadata = sample_metadata.get(name)
            face_info = {
                'name': name,
                'has_metadata': metadata is not None,
                'metadata': metadata
            }
            faces_with_metadata.append(face_info)
        
        return jsonify({
            'total_faces': face_count,
            'encodings_cached': False,
            'demo_mode': True,
            'faces': faces_with_metadata
        })
    except Exception as e:
        return jsonify({'error': f'Error fetching known faces: {str(e)}'}), 500

@app.route('/api/refresh-encodings', methods=['POST'])
def refresh_face_encodings():
    """Refresh face encodings cache (demo mode)."""
    try:
        return jsonify({
            'message': 'Demo mode: Face encodings cache would be refreshed in full version',
            'demo_mode': True
        })
    except Exception as e:
        return jsonify({'error': f'Error refreshing encodings: {str(e)}'}), 500

@app.route('/api/metadata/<name>', methods=['GET'])
def get_metadata(name):
    """Get metadata for a specific person."""
    try:
        sample_metadata = get_sample_metadata()
        metadata = sample_metadata.get(name)
        if metadata:
            return jsonify(metadata)
        else:
            return jsonify({'error': 'Person not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error fetching metadata: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413

if __name__ == '__main__':
    print("=== Face Recognition Web App (Demo Mode) ===")
    print("Starting Flask server...")
    print("Demo mode: Install face_recognition library for full functionality")
    
    # Display startup information
    face_count, face_files = get_known_faces_count()
    print(f"Known faces found: {face_count}")
    print(f"Known files: {face_files}")
    
    print("\n🌐 Open your browser to: http://localhost:5000")
    print("📝 To install full dependencies: pip install -r requirements.txt")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
