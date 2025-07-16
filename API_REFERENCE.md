# Face Recognition System - API Reference

## Overview

This document provides comprehensive API documentation for the Face Recognition System. The system uses LBPH (Local Binary Patterns Histograms) algorithm for efficient face recognition.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, no authentication is required. For production deployment, implement JWT or OAuth 2.0.

## Response Format

All API endpoints return JSON responses in the following format:

```json
{
  "success": true|false,
  "message": "Human-readable message",
  "data": {...},
  "error": "Error details (only when success=false)"
}
```

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

## Face Recognition Endpoints

### POST /recognize
Recognize faces in an uploaded image.

**Request:**
```http
POST /api/recognize
Content-Type: multipart/form-data

Parameters:
- image: File (required) - Image file (JPEG, PNG, max 10MB)
```

**Response:**
```json
{
  "success": true,
  "message": "Face recognition completed successfully",
  "data": {
    "total_faces_detected": 3,
    "total_faces_recognized": 2,
    "recognized_faces": [
      {
        "id": 1,
        "name": "John Doe",
        "employee_id": "EMP001",
        "department": "Engineering",
        "position": "Software Engineer",
        "email": "john.doe@company.com",
        "phone": "+1234567890",
        "confidence": 87.5,
        "face_location": [50, 200, 150, 100],
        "lbph_confidence": 45.2,
        "face_index": 0,
        "image_path": "uploads/known_faces/john_doe.jpg"
      }
    ],
    "processing_time": 2.34,
    "image_path": "uploads/test_images/test_123.jpg",
    "image_dimensions": "1920x1080",
    "detection_model": "haar_cascade",
    "recognition_tolerance": 100,
    "annotated_image_path": "uploads/test_images/test_123_annotated.jpg"
  }
}
```

### POST /camera/capture
Process image from camera capture.

**Request:**
```http
POST /api/camera/capture
Content-Type: application/json

Body:
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Response:** Same format as `/recognize`

### POST /camera/stream-frame
Process real-time video frame (optimized for speed).

**Request:**
```http
POST /api/camera/stream-frame
Content-Type: application/json

Body:
{
  "frame": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_faces_detected": 2,
    "total_faces_recognized": 1,
    "recognized_faces": [
      {
        "name": "Jane Smith",
        "confidence": 92.1,
        "face_location": [60, 180, 160, 80],
        "employee_id": "EMP002",
        "department": "Marketing"
      }
    ],
    "processing_time": 0.85
  }
}
```

## Admin Panel Endpoints

### GET /admin/faces
Get all known faces in the database.

**Request:**
```http
GET /api/admin/faces
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "employee_id": "EMP001",
      "department": "Engineering",
      "position": "Software Engineer",
      "email": "john.doe@company.com",
      "phone": "+1234567890",
      "image_path": "uploads/known_faces/john_doe.jpg",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### POST /admin/upload
Upload a new known face with metadata.

**Request:**
```http
POST /api/admin/upload
Content-Type: multipart/form-data

Parameters:
- image: File (required) - Face image file
- name: String (required) - Person's full name
- employee_id: String (optional) - Unique employee identifier
- department: String (optional) - Department name
- position: String (optional) - Job position
- email: String (optional) - Email address
- phone: String (optional) - Phone number
```

**Response:**
```json
{
  "success": true,
  "message": "Face uploaded successfully",
  "data": {
    "face_id": 15,
    "name": "New Employee",
    "processing_time": 1.23
  }
}
```

### GET /admin/search
Search known faces with filters and pagination.

**Request:**
```http
GET /api/admin/search?q=john&department=engineering&limit=20&offset=0

Parameters:
- q: String (optional) - Search query (searches name, employee_id, email, phone)
- department: String (optional) - Filter by department
- position: String (optional) - Filter by position
- limit: Integer (optional, default: 50) - Results per page
- offset: Integer (optional, default: 0) - Pagination offset
```

**Response:**
```json
{
  "success": true,
  "data": {
    "faces": [...],
    "total_count": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### DELETE /admin/faces/{face_id}
Delete a known face from the database.

**Request:**
```http
DELETE /api/admin/faces/15
```

**Response:**
```json
{
  "success": true,
  "message": "Face deleted successfully"
}
```

### POST /admin/bulk-upload
Upload multiple faces with metadata.

**Request:**
```http
POST /api/admin/bulk-upload
Content-Type: multipart/form-data

Parameters:
- images: File[] (required) - Multiple image files
- metadata: String (required) - JSON array of metadata objects
```

**Response:**
```json
{
  "success": true,
  "message": "Bulk upload completed: 8 successful, 2 failed",
  "data": {
    "results": [
      {
        "index": 0,
        "filename": "person1.jpg",
        "success": true,
        "face_id": 20,
        "name": "Person One"
      }
    ],
    "summary": {
      "total": 10,
      "success": 8,
      "errors": 2
    }
  }
}
```

## System Endpoints

### GET /system/stats
Get basic system statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "known_faces_count": 245,
    "total_recognitions": 1523,
    "avg_processing_time": 2.1,
    "system_uptime": "5 days, 3 hours",
    "database_size": "15.2 MB"
  }
}
```

### GET /system/health
Get comprehensive system health information.

**Response:**
```json
{
  "success": true,
  "data": {
    "system_stats": {...},
    "resources": {
      "cpu_percent": 25.4,
      "memory_percent": 45.2,
      "memory_available_gb": 4.2,
      "disk_free_gb": 125.8,
      "status": "healthy"
    },
    "face_processor": {
      "known_faces_count": 245,
      "face_detection_model": "haar_cascade",
      "recognition_algorithm": "LBPH",
      "confidence_threshold": 100,
      "is_trained": true,
      "lbph_available": true
    },
    "timestamp": "2024-01-15T14:30:00Z",
    "status": "healthy"
  }
}
```

## Export Endpoints

### POST /export/results
Export recognition results in various formats.

**Request:**
```http
POST /api/export/results
Content-Type: application/json

Body:
{
  "results": {...},
  "format": "json|csv|pdf",
  "include_images": false
}
```

**Response:** Binary file download

### GET /export/database
Export the entire face database.

**Request:**
```http
GET /api/export/database?format=json
```

**Response:** Binary file download

## History Endpoints

### GET /recognition-history
Get recognition history with pagination.

**Request:**
```http
GET /api/recognition-history?limit=50
```

### GET /history/search
Search recognition history with filters.

**Request:**
```http
GET /api/history/search?start_date=2024-01-01&end_date=2024-01-31&min_faces=1&max_faces=10
```

### GET /history/statistics
Get recognition history statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_recognitions": 1523,
    "total_faces_processed": 4567,
    "total_faces_recognized": 3890,
    "recognition_rate": 85.2,
    "avg_processing_time": 2.1,
    "recent_activity": 45,
    "daily_activity": [
      {"date": "2024-01-15", "count": 23},
      {"date": "2024-01-14", "count": 31}
    ]
  }
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Implement rate limiting (e.g., 100 requests per minute per IP)
- Add authentication and user-based quotas
- Monitor API usage and implement throttling

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Name is required",
    "Invalid email format"
  ]
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Face not found",
  "error": "No face found with ID 999"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Internal server error",
  "error": "Database connection failed"
}
```
