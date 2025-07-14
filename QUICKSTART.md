# Face Recognition Web Application - Quick Start Guide

Thank you for using the Face Recognition Web Application! This guide will help you get started quickly.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
**Windows:**
```powershell
.\setup_and_run.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option 2: Manual Setup
1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add known faces:
   - Place individual photos in `known_faces/` directory
   - Use format: `firstname_lastname.jpg`
   - Example: `john_doe.jpg`, `jane_smith.jpg`

3. Start the backend:
   ```bash
   cd backend
   python app.py
   ```

4. Open your browser to `http://localhost:5000`

## 📁 Directory Structure

```
face_recognition_app/
├── backend/                    # Flask backend
│   ├── app.py                 # Main Flask application
│   ├── recognizer.py          # Face recognition logic
│   ├── metadata_handler.py    # Person metadata management
│   └── templates/
│       └── index.html         # Web interface
├── frontend/                   # React frontend (optional)
│   ├── src/
│   ├── public/
│   └── package.json
├── known_faces/               # Add individual photos here
├── test_images/               # Uploaded group photos
├── outputs/                   # Generated annotated images
└── requirements.txt           # Python dependencies
```

## 🎯 How to Use

1. **Add Known Faces**: Place individual photos in `known_faces/` directory
2. **Upload Group Photo**: Use the web interface to upload a group photo
3. **Adjust Settings**: Set recognition tolerance (lower = more strict)
4. **Process Image**: Click "Process Image" to start face recognition
5. **View Results**: See identified people and annotated image

## 🔧 Configuration

### Adding New People
1. Add their photo to `known_faces/` directory
2. Update metadata in `backend/metadata_handler.py`:
   ```python
   "person_name": {
       "name": "Person Name",
       "email": "person@company.com",
       "role": "Job Title",
       "department": "Department"
   }
   ```
3. Refresh the face database via the web interface

### Recognition Settings
- **Tolerance**: 0.3 (strict) to 1.0 (lenient)
- **Image Formats**: JPG, JPEG, PNG
- **Max File Size**: 16MB

## 🌐 API Endpoints

- `POST /api/upload` - Upload and process group photo
- `GET /api/known-faces` - Get known faces information
- `POST /api/refresh-encodings` - Refresh face database
- `GET /api/health` - Health check

## 🛠️ Troubleshooting

**No faces detected:**
- Ensure good lighting in photos
- Use clear, front-facing photos
- Check image quality

**Poor recognition:**
- Adjust tolerance settings
- Use better reference photos
- Ensure consistent lighting

**Installation issues:**
- Check Python version (3.8+)
- Install CMake for dlib
- Try installing dependencies individually

## 📱 Features

- ✅ Group photo face detection
- ✅ Face recognition with known database
- ✅ Person metadata integration
- ✅ Visual annotation with names
- ✅ Web interface with drag-and-drop
- ✅ REST API for integration
- ✅ Real-time processing
- ✅ Cached encodings for performance

## 🔒 Privacy & Security

- All processing is done locally
- No data sent to external servers
- Images are stored temporarily
- Face encodings are cached locally

## 📞 Support

For help and support:
1. Check the troubleshooting section
2. Review the API documentation
3. Check the GitHub repository for updates

---

**Happy Face Recognition! 🎭**
