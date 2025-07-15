# Face Recognition System - Development Guide

## Prerequisites

Before running the system, ensure you have the following installed:

### For Backend (Python/Flask):
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (usually comes with Python)
- **Visual C++ Build Tools** (for face_recognition library on Windows)

### For Frontend (React):
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **npm** (comes with Node.js)

### Additional Requirements for face_recognition library:
- **cmake** - [Download CMake](https://cmake.org/download/)
- **dlib** prerequisites (automatically handled by pip on most systems)

## Quick Start

### Option 1: Automatic Startup (Recommended)
1. Double-click `start-system.bat` to start both backend and frontend automatically
2. Wait for both services to start (backend on port 5000, frontend on port 3000)
3. Open your browser and go to `http://localhost:3000`

### Option 2: Manual Startup

#### Backend Setup:
1. Open a command prompt and navigate to the project root
2. Run `start-backend.bat` OR follow these manual steps:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python models.py  # Initialize database
   python app.py     # Start server
   ```

#### Frontend Setup:
1. Open another command prompt and navigate to the project root
2. Run `start-frontend.bat` OR follow these manual steps:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Troubleshooting

### Common Issues:

#### 1. face_recognition Installation Failed
```bash
# Install Visual C++ Build Tools first, then try:
pip install --upgrade pip
pip install wheel
pip install dlib
pip install face_recognition
```

#### 2. CMake Not Found Error
- Install CMake from https://cmake.org/download/
- Add CMake to your system PATH

#### 3. Port Already in Use
- Backend (5000): Change the port in `backend/app.py` line: `app.run(port=5001)`
- Frontend (3000): Set environment variable `PORT=3001` before running `npm start`

#### 4. CORS Issues
- Ensure backend is running on port 5000
- Check the proxy setting in `frontend/package.json`

#### 5. Database Issues
- Delete `backend/database.db` and run `python models.py` again
- Check file permissions in the backend directory

## System Architecture

### Backend (Flask API)
- **Port**: 5000
- **Database**: SQLite (file-based)
- **Face Recognition**: face_recognition library with dlib
- **Image Processing**: OpenCV, PIL

### Frontend (React SPA)
- **Port**: 3000
- **UI Framework**: React 18
- **HTTP Client**: Axios
- **File Upload**: react-dropzone
- **Notifications**: react-hot-toast

## API Documentation

### Health Check
- `GET /api/health` - Check if the system is running

### Admin Panel
- `POST /api/admin/upload-face` - Upload known face with metadata
- `GET /api/admin/faces` - Get all known faces
- `DELETE /api/admin/faces/<id>` - Delete a known face

### Face Recognition
- `POST /api/recognize` - Upload image for face recognition
- `GET /api/recognition-history` - Get recognition history

### System Stats
- `GET /api/stats` - Get system statistics

## Usage Guide

### 1. Adding Known Faces (Admin Panel)
1. Go to Admin Panel
2. Drag & drop an image or click to select
3. Fill in the person's details (name is required)
4. Click "Add Face"

### 2. Recognizing Faces
1. Go to Face Recognition page
2. Upload an image with faces
3. Click "Recognize Faces"
4. View results with confidence scores

### 3. Viewing History
1. Go to History page
2. View all past recognition sessions
3. Click "View Details" for detailed results

## File Structure

```
FaceDetection/
├── backend/                 # Flask API server
│   ├── app.py              # Main application
│   ├── models.py           # Database models
│   ├── face_processor.py   # Face recognition logic
│   ├── utils.py            # Utility functions
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/            # Uploaded images
│   └── database.db         # SQLite database (created automatically)
├── frontend/               # React web application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── App.js          # Main app component
│   ├── package.json        # Node.js dependencies
│   └── public/             # Static files
├── start-system.bat        # Start both backend and frontend
├── start-backend.bat       # Start only backend
├── start-frontend.bat      # Start only frontend
└── README.md              # This file
```

## Performance Tips

1. **Image Size**: Resize large images before upload for faster processing
2. **Face Quality**: Use clear, well-lit images for better recognition accuracy
3. **Known Faces**: Add multiple angles of the same person for improved recognition
4. **Database**: Regularly clean old test images from the uploads folder

## Security Considerations

1. **Production Deployment**: 
   - Change Flask debug mode to False
   - Use environment variables for sensitive settings
   - Implement proper authentication and authorization
   - Use HTTPS in production

2. **Data Privacy**:
   - Face data is stored locally in SQLite database
   - Implement data retention policies
   - Consider encryption for sensitive data

## Development

### Adding New Features
1. Backend: Add new routes in `app.py` and logic in respective modules
2. Frontend: Create new components in `src/components/` or pages in `src/pages/`
3. API: Update `src/services/api.js` for new endpoints

### Testing
- Backend: Add unit tests for face recognition logic
- Frontend: Use React Testing Library for component tests
- Integration: Test complete workflows from upload to recognition

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review error messages in browser console and terminal
3. Ensure all prerequisites are properly installed
4. Verify network connectivity and port availability
