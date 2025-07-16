# Database Schema Documentation

## Overview

The Face Recognition System uses SQLite as its primary database for storing face data, metadata, and recognition history. This document provides comprehensive documentation of the database schema, relationships, and usage patterns.

## Database Structure

### Tables Overview

| Table Name | Purpose | Records |
|------------|---------|---------|
| `known_faces` | Store known face data and metadata | Face profiles |
| `recognition_history` | Track all recognition attempts | Recognition logs |

## Table Schemas

### known_faces

Stores information about known faces in the system, including face data and personal metadata.

```sql
CREATE TABLE known_faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    employee_id TEXT UNIQUE,
    department TEXT,
    position TEXT,
    email TEXT,
    phone TEXT,
    image_path TEXT NOT NULL,
    face_encoding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each face record |
| `name` | TEXT | NOT NULL | Full name of the person |
| `employee_id` | TEXT | UNIQUE | Employee identifier (optional, must be unique if provided) |
| `department` | TEXT | - | Department or division |
| `position` | TEXT | - | Job title or position |
| `email` | TEXT | - | Email address |
| `phone` | TEXT | - | Phone number |
| `image_path` | TEXT | NOT NULL | Path to the stored face image file |
| `face_encoding` | BLOB | NOT NULL | Serialized face data for LBPH recognition |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

#### Indexes

```sql
CREATE INDEX idx_known_faces_name ON known_faces(name);
CREATE INDEX idx_known_faces_employee_id ON known_faces(employee_id);
CREATE INDEX idx_known_faces_department ON known_faces(department);
CREATE INDEX idx_known_faces_created_at ON known_faces(created_at);
```

#### Sample Data

```sql
INSERT INTO known_faces (
    name, employee_id, department, position, email, phone, 
    image_path, face_encoding
) VALUES (
    'John Doe', 'EMP001', 'Engineering', 'Software Engineer',
    'john.doe@company.com', '+1234567890',
    'uploads/known_faces/john_doe.jpg', 
    X'89504E470D0A1A0A...'  -- Binary face data
);
```

### recognition_history

Tracks all face recognition attempts, including results and performance metrics.

```sql
CREATE TABLE recognition_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_image_path TEXT NOT NULL,
    recognized_faces TEXT NOT NULL,
    total_faces_detected INTEGER NOT NULL,
    total_faces_recognized INTEGER NOT NULL,
    processing_time REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Field Descriptions

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each recognition attempt |
| `test_image_path` | TEXT | NOT NULL | Path to the test image that was processed |
| `recognized_faces` | TEXT | NOT NULL | JSON string containing recognition results |
| `total_faces_detected` | INTEGER | NOT NULL | Number of faces detected in the image |
| `total_faces_recognized` | INTEGER | NOT NULL | Number of faces successfully recognized |
| `processing_time` | REAL | NOT NULL | Time taken to process the image (in seconds) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When the recognition was performed |

#### Indexes

```sql
CREATE INDEX idx_recognition_history_created_at ON recognition_history(created_at);
CREATE INDEX idx_recognition_history_faces_detected ON recognition_history(total_faces_detected);
CREATE INDEX idx_recognition_history_processing_time ON recognition_history(processing_time);
```

#### Sample Data

```sql
INSERT INTO recognition_history (
    test_image_path, recognized_faces, total_faces_detected, 
    total_faces_recognized, processing_time
) VALUES (
    'uploads/test_images/group_photo_123.jpg',
    '[{"name": "John Doe", "confidence": 87.5, "face_location": [50, 200, 150, 100]}]',
    3, 1, 2.34
);
```

## Data Relationships

### Entity Relationship Diagram

```
┌─────────────────┐         ┌──────────────────────┐
│   known_faces   │         │ recognition_history  │
├─────────────────┤         ├──────────────────────┤
│ id (PK)         │         │ id (PK)              │
│ name            │         │ test_image_path      │
│ employee_id     │◄────────┤ recognized_faces     │
│ department      │         │ total_faces_detected │
│ position        │         │ total_faces_recognized│
│ email           │         │ processing_time      │
│ phone           │         │ created_at           │
│ image_path      │         └──────────────────────┘
│ face_encoding   │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### Relationship Notes

- No direct foreign key relationship exists between tables
- `recognition_history.recognized_faces` contains JSON data that may reference `known_faces.name` and other fields
- Relationships are maintained at the application level through the recognition process

## Data Access Patterns

### Common Queries

#### 1. Search Known Faces

```sql
-- Search by name, employee ID, email, or phone
SELECT id, name, employee_id, department, position, email, phone, 
       image_path, created_at, updated_at
FROM known_faces 
WHERE (name LIKE '%john%' OR employee_id LIKE '%john%' 
       OR email LIKE '%john%' OR phone LIKE '%john%')
  AND department LIKE '%engineering%'
ORDER BY name
LIMIT 50 OFFSET 0;
```

#### 2. Get Face Statistics

```sql
-- Department statistics
SELECT department, COUNT(*) as count
FROM known_faces 
WHERE department IS NOT NULL AND department != ''
GROUP BY department 
ORDER BY count DESC;

-- Position statistics
SELECT position, COUNT(*) as count
FROM known_faces 
WHERE position IS NOT NULL AND position != ''
GROUP BY position 
ORDER BY count DESC;

-- Recent additions
SELECT COUNT(*) as recent_additions
FROM known_faces 
WHERE created_at >= datetime('now', '-30 days');
```

#### 3. Recognition History Analysis

```sql
-- Recognition performance over time
SELECT DATE(created_at) as date, 
       COUNT(*) as total_recognitions,
       AVG(total_faces_detected) as avg_faces_detected,
       AVG(total_faces_recognized) as avg_faces_recognized,
       AVG(processing_time) as avg_processing_time
FROM recognition_history 
WHERE created_at >= datetime('now', '-7 days')
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Recognition rate calculation
SELECT 
    SUM(total_faces_detected) as total_faces_processed,
    SUM(total_faces_recognized) as total_faces_recognized,
    ROUND((SUM(total_faces_recognized) * 100.0 / SUM(total_faces_detected)), 2) as recognition_rate
FROM recognition_history;
```

#### 4. Performance Monitoring

```sql
-- Slow recognition queries
SELECT id, test_image_path, total_faces_detected, processing_time, created_at
FROM recognition_history 
WHERE processing_time > 5.0
ORDER BY processing_time DESC
LIMIT 10;

-- High-volume recognition periods
SELECT 
    strftime('%Y-%m-%d %H', created_at) as hour,
    COUNT(*) as recognition_count,
    AVG(processing_time) as avg_processing_time
FROM recognition_history 
WHERE created_at >= datetime('now', '-24 hours')
GROUP BY strftime('%Y-%m-%d %H', created_at)
ORDER BY recognition_count DESC;
```

## Data Storage Considerations

### Face Encoding Storage

Face encodings are stored as BLOB data containing serialized numpy arrays:

```python
# Storing face encoding
face_data = extract_face_for_training(image_path)
face_encoding_blob = pickle.dumps(face_data)

# Retrieving face encoding
face_data = pickle.loads(face_encoding_blob)
```

### JSON Data in Recognition History

The `recognized_faces` field contains JSON data with the following structure:

```json
[
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
  },
  {
    "id": null,
    "name": "Unknown",
    "employee_id": "N/A",
    "department": "N/A",
    "position": "N/A",
    "email": "N/A",
    "phone": "N/A",
    "confidence": 0.0,
    "face_location": [60, 220, 160, 120],
    "lbph_confidence": 150.0,
    "face_index": 1,
    "image_path": null
  }
]
```

## Database Maintenance

### Backup Strategy

```bash
# Create database backup
sqlite3 database.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore from backup
sqlite3 database.db ".restore backup_20240115_143000.db"
```

### Cleanup Operations

```sql
-- Remove old recognition history (older than 90 days)
DELETE FROM recognition_history 
WHERE created_at < datetime('now', '-90 days');

-- Remove orphaned face records (missing image files)
DELETE FROM known_faces 
WHERE image_path NOT IN (
    SELECT image_path FROM known_faces 
    WHERE file_exists(image_path) = 1
);
```

### Performance Optimization

```sql
-- Analyze table statistics
ANALYZE;

-- Rebuild indexes
REINDEX;

-- Vacuum database to reclaim space
VACUUM;
```

## Security Considerations

### Data Protection

1. **Face Encoding Security**: Face encodings are stored as binary data, making them difficult to reverse-engineer
2. **Personal Data**: Email and phone numbers should be encrypted in production
3. **Access Control**: Implement proper authentication and authorization
4. **Audit Trail**: Recognition history provides complete audit trail

### Privacy Compliance

1. **Data Retention**: Implement automatic cleanup of old recognition history
2. **Right to Deletion**: Provide functionality to completely remove person's data
3. **Data Minimization**: Only collect necessary personal information
4. **Consent Management**: Track and manage user consent for face recognition

## Migration Scripts

### Version 1.0 to 2.0 (LBPH Migration)

```sql
-- Add new columns for LBPH support
ALTER TABLE known_faces ADD COLUMN face_encoding_version INTEGER DEFAULT 2;
ALTER TABLE known_faces ADD COLUMN lbph_confidence_threshold REAL DEFAULT 100.0;

-- Update existing records
UPDATE known_faces SET face_encoding_version = 2 WHERE face_encoding_version IS NULL;
```

### Performance Indexes

```sql
-- Add composite indexes for common search patterns
CREATE INDEX idx_known_faces_dept_pos ON known_faces(department, position);
CREATE INDEX idx_known_faces_name_dept ON known_faces(name, department);
CREATE INDEX idx_recognition_history_date_faces ON recognition_history(created_at, total_faces_detected);
```

## Monitoring and Alerts

### Database Health Checks

```sql
-- Check database integrity
PRAGMA integrity_check;

-- Check database size
SELECT 
    page_count * page_size as size_bytes,
    page_count,
    page_size
FROM pragma_page_count(), pragma_page_size();

-- Check table sizes
SELECT 
    name,
    COUNT(*) as row_count
FROM sqlite_master 
WHERE type='table' 
GROUP BY name;
```

### Performance Metrics

```sql
-- Query performance statistics
SELECT 
    'known_faces' as table_name,
    COUNT(*) as total_records,
    AVG(length(face_encoding)) as avg_encoding_size,
    MAX(created_at) as latest_addition
FROM known_faces

UNION ALL

SELECT 
    'recognition_history' as table_name,
    COUNT(*) as total_records,
    AVG(processing_time) as avg_processing_time,
    MAX(created_at) as latest_recognition
FROM recognition_history;
```
