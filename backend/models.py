import sqlite3
from datetime import datetime
import os

DATABASE_PATH = 'database.db'

def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create known_faces table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS known_faces (
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
        )
    ''')
    
    # Create recognition_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recognition_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_image_path TEXT NOT NULL,
            recognized_faces TEXT,  -- JSON string of recognized faces
            total_faces_detected INTEGER DEFAULT 0,
            total_faces_recognized INTEGER DEFAULT 0,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class KnownFace:
    @staticmethod
    def create(name, employee_id, department, position, email, phone, image_path, face_encoding):
        """Create a new known face entry"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO known_faces 
                (name, employee_id, department, position, email, phone, image_path, face_encoding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, employee_id, department, position, email, phone, image_path, face_encoding))
            
            face_id = cursor.lastrowid
            conn.commit()
            return face_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all known faces"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, employee_id, department, position, email, phone, 
                   image_path, created_at, updated_at
            FROM known_faces
            ORDER BY name
        ''')
        
        faces = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': face[0],
                'name': face[1],
                'employee_id': face[2],
                'department': face[3],
                'position': face[4],
                'email': face[5],
                'phone': face[6],
                'image_path': face[7],
                'created_at': face[8],
                'updated_at': face[9]
            }
            for face in faces
        ]
    
    @staticmethod
    def get_by_id(face_id):
        """Get a specific known face by ID"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, employee_id, department, position, email, phone, 
                   image_path, face_encoding, created_at, updated_at
            FROM known_faces
            WHERE id = ?
        ''', (face_id,))
        
        face = cursor.fetchone()
        conn.close()
        
        if face:
            return {
                'id': face[0],
                'name': face[1],
                'employee_id': face[2],
                'department': face[3],
                'position': face[4],
                'email': face[5],
                'phone': face[6],
                'image_path': face[7],
                'face_encoding': face[8],
                'created_at': face[9],
                'updated_at': face[10]
            }
        return None
    
    @staticmethod
    def get_all_encodings():
        """Get all face encodings with metadata"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, employee_id, department, position, email, phone, 
                   image_path, face_encoding
            FROM known_faces
        ''')
        
        faces = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': face[0],
                'name': face[1],
                'employee_id': face[2],
                'department': face[3],
                'position': face[4],
                'email': face[5],
                'phone': face[6],
                'image_path': face[7],
                'face_encoding': face[8]
            }
            for face in faces
        ]
    
    @staticmethod
    def delete(face_id):
        """Delete a known face"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get image path before deletion
        cursor.execute('SELECT image_path FROM known_faces WHERE id = ?', (face_id,))
        result = cursor.fetchone()
        
        if result:
            image_path = result[0]
            cursor.execute('DELETE FROM known_faces WHERE id = ?', (face_id,))
            conn.commit()
            
            # Delete image file if it exists
            if os.path.exists(image_path):
                os.remove(image_path)
            
            conn.close()
            return True
        
        conn.close()
        return False

class RecognitionHistory:
    @staticmethod
    def create(test_image_path, recognized_faces, total_faces_detected, total_faces_recognized, processing_time):
        """Create a new recognition history entry"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recognition_history 
            (test_image_path, recognized_faces, total_faces_detected, total_faces_recognized, processing_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_image_path, recognized_faces, total_faces_detected, total_faces_recognized, processing_time))
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return history_id
    
    @staticmethod
    def get_all(limit=50):
        """Get recognition history with pagination"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, test_image_path, recognized_faces, total_faces_detected, 
                   total_faces_recognized, processing_time, created_at
            FROM recognition_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': record[0],
                'test_image_path': record[1],
                'recognized_faces': record[2],
                'total_faces_detected': record[3],
                'total_faces_recognized': record[4],
                'processing_time': record[5],
                'created_at': record[6]
            }
            for record in history
        ]

# Initialize database when module is imported
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
