import os
import hashlib
import re
import time
import logging
from datetime import datetime
import mimetypes
from typing import Dict, Any, Optional, Tuple, List
from functools import wraps

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

# Performance monitoring utilities

def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Log performance if it takes too long
            if execution_time > 5.0:  # 5 seconds threshold
                logging.warning(f"Slow function execution: {func.__name__} took {execution_time:.2f}s")

            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

def validate_file_upload(file, allowed_extensions: set, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
    """Comprehensive file upload validation"""
    if not file:
        return False, "No file provided"

    if not file.filename:
        return False, "No filename provided"

    # Check file extension
    if '.' not in file.filename:
        return False, "File must have an extension"

    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"File type '{extension}' not allowed. Allowed types: {', '.join(allowed_extensions)}"

    # Check file size (if available)
    if hasattr(file, 'content_length') and file.content_length:
        if file.content_length > max_size_mb * 1024 * 1024:
            return False, f"File size ({file.content_length / (1024*1024):.1f}MB) exceeds maximum allowed ({max_size_mb}MB)"

    # Check filename for security
    if not is_safe_filename(file.filename):
        return False, "Filename contains invalid characters"

    return True, None

def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no path traversal, etc.)"""
    # Remove any path components
    filename = os.path.basename(filename)

    # Check for dangerous patterns
    dangerous_patterns = [
        r'\.\.', r'/', r'\\', r':', r'\*', r'\?', r'"', r'<', r'>', r'\|'
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, filename):
            return False

    # Check length
    if len(filename) > 255:
        return False

    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]

    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        return False

    return True

def validate_image_content(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate image content and properties"""
    try:
        from PIL import Image

        with Image.open(file_path) as img:
            # Check if it's actually an image
            img.verify()

        # Reopen for further checks (verify() closes the file)
        with Image.open(file_path) as img:
            width, height = img.size

            # Check minimum dimensions
            if width < 50 or height < 50:
                return False, f"Image too small ({width}x{height}). Minimum size is 50x50 pixels"

            # Check maximum dimensions
            if width > 4000 or height > 4000:
                return False, f"Image too large ({width}x{height}). Maximum size is 4000x4000 pixels"

            # Check aspect ratio (should be reasonable for face images)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 5.0:
                return False, f"Image aspect ratio too extreme ({aspect_ratio:.1f}:1). Maximum ratio is 5:1"

            # Check color mode
            if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                return False, f"Unsupported image mode: {img.mode}"

            return True, None

    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def sanitize_input(text: str, max_length: int = 255, allow_special_chars: bool = False) -> str:
    """Sanitize text input"""
    if not text:
        return ""

    # Remove leading/trailing whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    if not allow_special_chars:
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\'\&\$\`\|]', '', text)

    return text

def validate_metadata_enhanced(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Enhanced metadata validation with detailed error reporting"""
    errors = []

    # Required field validation
    if not data.get('name') or not data['name'].strip():
        errors.append("Name is required")
    else:
        name = sanitize_input(data['name'], 100)
        if len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        if not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
            errors.append("Name can only contain letters, spaces, hyphens, dots, and apostrophes")

    # Employee ID validation
    if data.get('employee_id'):
        employee_id = sanitize_input(data['employee_id'], 50)
        if not re.match(r'^[a-zA-Z0-9\-_]+$', employee_id):
            errors.append("Employee ID can only contain letters, numbers, hyphens, and underscores")

    # Email validation
    if data.get('email'):
        email = sanitize_input(data['email'], 254)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")

    # Phone validation
    if data.get('phone'):
        phone = sanitize_input(data['phone'], 20)
        # Remove all non-digit characters except +, -, (, ), and spaces
        phone_clean = re.sub(r'[^\d+\-\(\)\s]', '', phone)
        digits_only = re.sub(r'[^\d]', '', phone_clean)
        if len(digits_only) < 10 or len(digits_only) > 15:
            errors.append("Phone number must contain 10-15 digits")

    # Department validation
    if data.get('department'):
        department = sanitize_input(data['department'], 100)
        if not re.match(r'^[a-zA-Z0-9\s\-&\.]+$', department):
            errors.append("Department name contains invalid characters")

    # Position validation
    if data.get('position'):
        position = sanitize_input(data['position'], 100)
        if not re.match(r'^[a-zA-Z0-9\s\-&\.\/]+$', position):
            errors.append("Position title contains invalid characters")

    return len(errors) == 0, errors

def check_system_resources() -> Dict[str, Any]:
    """Check system resources and performance"""
    import psutil

    try:
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Get memory usage
        memory = psutil.virtual_memory()

        # Get disk usage for uploads directory
        disk_usage = psutil.disk_usage('.')

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_free_gb': disk_usage.free / (1024**3),
            'disk_percent': (disk_usage.used / disk_usage.total) * 100,
            'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning'
        }
    except ImportError:
        return {
            'status': 'unknown',
            'message': 'psutil not available for system monitoring'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error checking system resources: {str(e)}"
        }
