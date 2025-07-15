import os
import hashlib
from datetime import datetime
import mimetypes

def generate_unique_filename(original_filename):
    """Generate a unique filename using timestamp and hash"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Create hash from original filename and current time
    hash_input = f"{original_filename}_{timestamp}".encode('utf-8')
    file_hash = hashlib.md5(hash_input).hexdigest()[:8]
    
    return f"{timestamp}_{file_hash}{ext}"

def get_file_info(file_path):
    """Get comprehensive file information"""
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    
    return {
        'filename': os.path.basename(file_path),
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'mime_type': mimetypes.guess_type(file_path)[0]
    }

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def cleanup_old_files(directory, max_age_days=30):
    """Clean up old files in a directory"""
    if not os.path.exists(directory):
        return 0
    
    current_time = datetime.now().timestamp()
    max_age_seconds = max_age_days * 24 * 60 * 60
    cleaned_count = 0
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception as e:
                    print(f"Error removing old file {file_path}: {e}")
    
    return cleaned_count

def validate_image_dimensions(file_path, max_width=4000, max_height=4000):
    """Validate image dimensions"""
    try:
        from PIL import Image
        
        with Image.open(file_path) as img:
            width, height = img.size
            
            if width > max_width or height > max_height:
                return False, f"Image dimensions ({width}x{height}) exceed maximum allowed ({max_width}x{max_height})"
            
            return True, None
            
    except Exception as e:
        return False, f"Error validating image: {str(e)}"

def compress_image(input_path, output_path, quality=85, max_dimension=1920):
    """Compress and resize image if needed"""
    try:
        from PIL import Image
        
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            width, height = img.size
            if width > max_dimension or height > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            # Save with compression
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
        return True, None
        
    except Exception as e:
        return False, f"Error compressing image: {str(e)}"

def create_response(success=True, message="", data=None, error=None):
    """Create standardized API response"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response

def validate_metadata(data, required_fields=None):
    """Validate metadata fields"""
    if required_fields is None:
        required_fields = ['name']
    
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field] or data[field].strip() == '':
            errors.append(f"{field} is required")
    
    # Additional validations
    if 'name' in data and data['name']:
        if len(data['name'].strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        if len(data['name'].strip()) > 100:
            errors.append("Name must be less than 100 characters long")
    
    if 'employee_id' in data and data['employee_id']:
        if len(data['employee_id'].strip()) > 50:
            errors.append("Employee ID must be less than 50 characters long")
    
    if 'email' in data and data['email']:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append("Invalid email format")
    
    if 'phone' in data and data['phone']:
        # Basic phone validation
        phone_clean = re.sub(r'[^\d+\-\(\)\s]', '', data['phone'])
        if len(phone_clean.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
            errors.append("Phone number must contain at least 10 digits")
    
    return errors

def log_activity(activity_type, message, user_id=None):
    """Log system activities"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': activity_type,
        'message': message,
        'user_id': user_id
    }
    
    # You could implement file logging or database logging here
    print(f"[{log_entry['timestamp']}] {activity_type}: {message}")
    
    return log_entry

def get_system_stats():
    """Get system statistics"""
    try:
        from models import KnownFace, RecognitionHistory
        
        known_faces_count = len(KnownFace.get_all())
        recent_recognitions = len(RecognitionHistory.get_all(limit=100))
        
        # Calculate storage usage
        upload_dirs = ['uploads/known_faces', 'uploads/test_images']
        total_storage = 0
        
        for directory in upload_dirs:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        total_storage += os.path.getsize(file_path)
        
        return {
            'known_faces_count': known_faces_count,
            'recent_recognitions': recent_recognitions,
            'total_storage_bytes': total_storage,
            'total_storage_formatted': format_file_size(total_storage),
            'uptime': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'error': f"Error getting system stats: {str(e)}"
        }
