# 🎭 Face Recognition Web Application

A full-stack face recognition web application that detects and identifies people in group photos using AI. Built with Flask backend and a modern web frontend.

## 🚀 Features

- **Group Photo Analysis**: Upload group photos and get instant face detection
- **Face Recognition**: Matches detected faces against a database of known people
- **Metadata Integration**: Retrieves and displays person information (name, role, department, email)
- **Visual Annotation**: Generates annotated images with labeled faces
- **Web Interface**: Beautiful, responsive web UI with drag-and-drop upload
- **REST API**: Complete API for programmatic integration
- **Real-time Processing**: Fast face detection and recognition
- **Caching System**: Optimized face encoding caching for better performance

## 📁 Project Structure

```
face_recognition_app/
├── backend/
│   ├── app.py                  # Flask backend server
│   ├── recognizer.py           # Face recognition logic
│   ├── metadata_handler.py     # Person metadata management
│   ├── encodings.pkl           # Cached face encodings
│   └── templates/
│       └── index.html          # Web interface
├── known_faces/                # Directory for known person images
├── test_images/                # Uploaded group photos
├── outputs/                    # Generated annotated images
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- CMake (for dlib compilation)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd face_recognition_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up known faces database**
   - Create the `known_faces/` directory if it doesn't exist
   - Add individual photos of people you want to recognize
   - Name files as `person_name.jpg` (e.g., `john_doe.jpg`, `jane_smith.jpg`)
   - Use clear, front-facing photos for best results

4. **Start the application**
   ```bash
   cd backend
   python app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:5000`
   - The web interface will load automatically

## 📸 How to Use

### Web Interface
1. **Upload a group photo** using the drag-and-drop interface
2. **Adjust recognition tolerance** (lower = more strict matching)
3. **Click "Process Image"** to start face recognition
4. **View results** including:
   - Statistics (total faces, known faces, unknown faces)
   - Person details with metadata
   - Annotated image with labeled faces

### API Endpoints

#### Upload and Process Image
```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- image: Image file
- tolerance: Recognition tolerance (0.3-1.0, default: 0.5)

Response:
{
  "success": true,
  "statistics": {
    "total_faces_detected": 5,
    "known_faces": 3,
    "unknown_faces": 2
  },
  "recognized_people": [
    {
      "name": "John Doe",
      "email": "john.doe@company.com",
      "role": "Software Engineer",
      "department": "Engineering",
      "employee_id": "EMP001"
    }
  ],
  "annotated_image_url": "/api/annotated/image_annotated.jpg"
}
```

#### Get Known Faces
```http
GET /api/known-faces

Response:
{
  "total_faces": 5,
  "encodings_cached": true,
  "faces": [
    {
      "name": "john_doe",
      "has_metadata": true,
      "metadata": { ... }
    }
  ]
}
```

#### Refresh Face Database
```http
POST /api/refresh-encodings

Response:
{
  "message": "Face encodings cache refreshed successfully"
}
```

## 🔧 Configuration

### Face Recognition Settings
- **Tolerance**: Controls matching strictness (0.3-1.0)
  - Lower values = stricter matching, fewer false positives
  - Higher values = more lenient matching, more potential matches

### Adding New People
1. Add their photo to `known_faces/` directory
2. Name the file as `firstname_lastname.jpg`
3. Update metadata in `backend/metadata_handler.py`
4. Refresh encodings via API or restart the application

### Metadata Management
Edit `backend/metadata_handler.py` to add/update person information:

```python
PEOPLE_METADATA = {
    "john_doe": {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "role": "Software Engineer",
        "department": "Engineering",
        "employee_id": "EMP001",
        "phone": "+1-555-0123"
    }
}
```

## 🎯 Performance Tips

1. **Image Quality**: Use high-quality, well-lit photos for known faces
2. **File Naming**: Use consistent naming convention (firstname_lastname.jpg)
3. **Face Orientation**: Front-facing photos work best
4. **Image Size**: Optimize images for faster processing
5. **Caching**: Use the encoding cache for better performance

## 🔍 Troubleshooting

### Common Issues

**No faces detected in known_faces**
- Check image quality and lighting
- Ensure faces are clearly visible and front-facing
- Verify file formats (JPG, PNG, JPEG supported)

**Poor recognition accuracy**
- Adjust tolerance settings
- Use better quality reference photos
- Ensure good lighting in group photos

**Performance issues**
- Refresh encodings cache
- Optimize image sizes
- Check system resources

**Installation problems**
- Ensure CMake is installed for dlib
- Try installing dependencies individually
- Check Python version compatibility

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export FLASK_DEBUG=1
python app.py
```

## 📊 API Documentation

### Health Check
```http
GET /api/health
```

### Person Metadata
```http
GET /api/metadata/<name>
POST /api/metadata/<name>
```

### Annotated Images
```http
GET /api/annotated/<filename>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [face_recognition](https://github.com/ageitgey/face_recognition) library by Adam Geitgey
- [OpenCV](https://opencv.org/) for image processing
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [dlib](http://dlib.net/) for face detection algorithms

## 📞 Support

For questions or support, please:
1. Check the troubleshooting section
2. Review the API documentation
3. Create an issue in the repository
4. Contact the development team

---

**Built with ❤️ using Python, Flask, and AI**
