# Face Recognition System

A comprehensive face recognition system built with Python Flask backend and React.js frontend, featuring LBPH (Local Binary Patterns Histograms) algorithm for efficient and accurate face recognition.

## 🚀 Features

### Core Functionality
- **Real-time Face Recognition**: Process camera feeds and static images with live detection
- **LBPH Algorithm**: Fast and accurate face recognition using OpenCV's LBPH recognizer
- **Multi-face Detection**: Detect and recognize up to 50 faces in a single image
- **High Performance**: 3-5 second processing time with 90%+ accuracy on quality images
- **Confidence Scoring**: Detailed confidence metrics and distance calculations

### Admin Panel
- **Face Database Management**: Complete CRUD operations for known faces
- **Bulk Upload**: Upload multiple face images with CSV template support
- **Advanced Search**: Filter by name, department, position, employee ID with pagination
- **Statistics Dashboard**: Real-time analytics with department/position breakdowns
- **Export Functionality**: Export database and results in JSON, CSV, PDF formats

### User Interface
- **Drag-and-Drop Upload**: Intuitive file upload with preview
- **Camera Integration**: Real-time camera capture with WebRTC support
- **Visual Results**: Annotated images with color-coded bounding boxes
- **Multiple View Modes**: Original, annotated, and split-view comparison
- **Responsive Design**: Mobile-first design that works on all devices

### Technical Features
- **Performance Monitoring**: System health metrics and resource usage tracking
- **Enhanced Validation**: Comprehensive input validation with detailed error messages
- **Data Export**: Multiple format support (JSON, CSV, PDF) with customizable options
- **History Tracking**: Complete audit trail with searchable recognition history
- **RESTful API**: Well-documented endpoints with consistent response format

## 🛠 Technology Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask**: Lightweight web framework
- **OpenCV**: Computer vision and LBPH face recognition
- **SQLite**: Embedded database for face data and metadata
- **ReportLab**: PDF generation for comprehensive reports
- **Pillow**: Advanced image processing capabilities

### Frontend
- **React.js 18+**: Modern UI framework with hooks
- **JavaScript ES6+**: Modern JavaScript features
- **CSS3**: Advanced styling with flexbox and grid
- **Lucide React**: Beautiful and consistent icon library
- **React Hot Toast**: User-friendly notifications

## 📁 Project Structure

```
FaceDetection/
├── backend/
│   ├── app.py                 # Main Flask application with API endpoints
│   ├── models.py              # Database models and operations
│   ├── face_processor.py      # LBPH face recognition implementation
│   ├── utils.py               # Utility functions and validation
│   ├── export_utils.py        # Export functionality (JSON, CSV, PDF)
│   ├── requirements.txt       # Python dependencies
│   ├── test_face_processor.py # Unit tests for face processor
│   ├── test_api.py           # API endpoint tests
│   ├── uploads/              # Uploaded images directory
│   │   ├── known_faces/      # Training face images
│   │   ├── test_images/      # Recognition test images
│   │   └── annotated/        # Processed images with annotations
│   └── database.db           # SQLite database
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

**🚨 SETUPTOOLS ERROR FIX:**
If you get "Cannot import 'setuptools.build_meta'" error, try these solutions in order:

1. **Emergency Fix (Recommended)**:
   ```bash
   emergency-setup-backend.bat
   ```

2. **Docker Solution (Most Reliable)**:
   ```bash
   start-with-docker.bat
   ```

3. **Minimal Setup (No face_recognition)**:
   ```bash
   start-minimal.bat
   ```

**Other Common Issues:**
- **Timeout errors** → Use improved scripts with longer timeouts
- **Visual C++ Build Tools missing** → Install from Microsoft
- **CMake not found** → Download and install CMake
- **Python 3.13 compatibility** → Use Python 3.9-3.11

**📖 Detailed Help:**
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Complete troubleshooting guide
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide

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
