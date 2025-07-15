# Face Recognition System

A comprehensive face recognition system that detects and identifies faces in real-time group photos or individual images.

## Features

- **Real-time Face Detection**: Process group photos or individual images
- **Face Recognition**: Match detected faces with preloaded face data
- **Admin Panel**: Upload known face images with metadata
- **User Interface**: Upload test images and view recognition results
- **Structured Results**: Display all matched individuals with their details

## Technology Stack

- **Backend**: Python, Flask, face_recognition library
- **Frontend**: React, Axios
- **Database**: SQLite
- **Image Processing**: OpenCV, PIL

## Project Structure

```
FaceDetection/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models.py              # Database models
│   ├── face_processor.py      # Face detection and recognition logic
│   ├── utils.py               # Utility functions
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/               # Uploaded images directory
│   │   ├── known_faces/       # Admin uploaded face images
│   │   └── test_images/       # User uploaded test images
│   └── database.db            # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── App.js             # Main React app
│   ├── package.json
│   └── public/
└── README.md
```

## Installation & Setup

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** (for cloning)

### Quick Start (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ArulventhanGM/Face-Detection.git
   cd Face-Detection
   ```

2. **Start the complete system**:
   ```bash
   # Double-click this file on Windows:
   start-system.bat
   
   # Or run manually:
   start "Backend" start-backend.bat
   start "Frontend" start-frontend.bat
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize database:
   ```bash
   python models.py
   ```

5. Start the Flask server:
   ```bash
   python app.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

### Troubleshooting

If you encounter issues during installation, especially with the `face_recognition` library:

1. **Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for detailed solutions
2. **Try the alternative setup**: `setup-backend-alternative.bat`
3. **Use Docker**: `docker-compose up --build` (most reliable)
4. **Use Conda** instead of pip for scientific packages

**Common Issues:**
- Timeout errors → Use improved scripts with longer timeouts
- Visual C++ Build Tools missing → Install from Microsoft
- CMake not found → Download and install CMake
- Python 3.13 compatibility → Use Python 3.9-3.11

### Troubleshooting

If you encounter issues during installation, check the [DEVELOPMENT.md](DEVELOPMENT.md) file for detailed troubleshooting steps.

## Usage

1. **Admin Panel**: Upload known face images with metadata (name, ID, etc.)
2. **Face Recognition**: Upload test images to identify faces
3. **Results**: View matched individuals with their details in a structured format

## API Endpoints

- `POST /api/admin/upload-face` - Upload known face with metadata
- `GET /api/admin/faces` - Get all known faces
- `DELETE /api/admin/faces/<id>` - Delete a known face
- `POST /api/recognize` - Upload image for face recognition
- `GET /api/recognition-history` - Get recognition history

## Additional Documentation

- [DEVELOPMENT.md](DEVELOPMENT.md) - Detailed development guide and troubleshooting
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment instructions

## Features Demo

### Admin Panel
- Upload face images with metadata (name, employee ID, department, etc.)
- View all registered faces in a grid layout
- Delete faces from the system
- Real-time validation and error handling

### Face Recognition
- Drag & drop image upload interface
- Real-time face detection and recognition
- Confidence scores for each recognized face
- Annotated result images with face boxes and labels
- Support for group photos with multiple faces

### Dashboard & Analytics
- System health monitoring
- Recognition statistics and metrics
- Storage usage tracking
- Quick action shortcuts

### History & Reporting
- Complete recognition session history
- Detailed results for each recognition attempt
- Export and analysis capabilities

## License

MIT License
