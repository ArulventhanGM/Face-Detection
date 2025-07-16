import sqlite3
from datetime import datetime
import os
import logging
from typing import List, Dict, Any, Optional, Tuple

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

    @staticmethod
    def search_faces(query: str = "", department: str = "", position: str = "",
                    limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Search faces with filters and pagination"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Build WHERE clause
        where_conditions = []
        params = []

        if query:
            where_conditions.append("""
                (name LIKE ? OR employee_id LIKE ? OR email LIKE ? OR phone LIKE ?)
            """)
            query_param = f"%{query}%"
            params.extend([query_param, query_param, query_param, query_param])

        if department:
            where_conditions.append("department LIKE ?")
            params.append(f"%{department}%")

        if position:
            where_conditions.append("position LIKE ?")
            params.append(f"%{position}%")

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) FROM known_faces {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Get paginated results
        search_query = f"""
            SELECT id, name, employee_id, department, position, email, phone,
                   image_path, created_at, updated_at
            FROM known_faces
            {where_clause}
            ORDER BY name
            LIMIT ? OFFSET ?
        """
        cursor.execute(search_query, params + [limit, offset])

        faces = []
        for row in cursor.fetchall():
            faces.append({
                'id': row[0],
                'name': row[1],
                'employee_id': row[2],
                'department': row[3],
                'position': row[4],
                'email': row[5],
                'phone': row[6],
                'image_path': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            })

        conn.close()
        return faces, total_count

    @staticmethod
    def get_departments() -> List[str]:
        """Get all unique departments"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT department
            FROM known_faces
            WHERE department IS NOT NULL AND department != ''
            ORDER BY department
        """)

        departments = [row[0] for row in cursor.fetchall()]
        conn.close()
        return departments

    @staticmethod
    def get_positions() -> List[str]:
        """Get all unique positions"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT position
            FROM known_faces
            WHERE position IS NOT NULL AND position != ''
            ORDER BY position
        """)

        positions = [row[0] for row in cursor.fetchall()]
        conn.close()
        return positions

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Total faces
        cursor.execute("SELECT COUNT(*) FROM known_faces")
        total_faces = cursor.fetchone()[0]

        # Faces by department
        cursor.execute("""
            SELECT department, COUNT(*)
            FROM known_faces
            WHERE department IS NOT NULL AND department != ''
            GROUP BY department
            ORDER BY COUNT(*) DESC
        """)
        departments = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Faces by position
        cursor.execute("""
            SELECT position, COUNT(*)
            FROM known_faces
            WHERE position IS NOT NULL AND position != ''
            GROUP BY position
            ORDER BY COUNT(*) DESC
        """)
        positions = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]

        # Recent additions (last 30 days)
        cursor.execute("""
            SELECT COUNT(*)
            FROM known_faces
            WHERE created_at >= datetime('now', '-30 days')
        """)
        recent_additions = cursor.fetchone()[0]

        conn.close()

        return {
            'total_faces': total_faces,
            'departments': departments,
            'positions': positions,
            'recent_additions': recent_additions
        }

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

    @staticmethod
    def search_history(start_date: str = "", end_date: str = "",
                      min_faces: int = 0, max_faces: int = 999,
                      limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Search recognition history with filters and pagination"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Build WHERE clause
        where_conditions = ["total_faces_detected >= ?", "total_faces_detected <= ?"]
        params = [min_faces, max_faces]

        if start_date:
            where_conditions.append("created_at >= ?")
            params.append(start_date)

        if end_date:
            where_conditions.append("created_at <= ?")
            params.append(end_date)

        where_clause = "WHERE " + " AND ".join(where_conditions)

        # Get total count
        count_query = f"""
            SELECT COUNT(*) FROM recognition_history {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Get paginated results
        search_query = f"""
            SELECT id, test_image_path, recognized_faces, total_faces_detected,
                   total_faces_recognized, processing_time, created_at
            FROM recognition_history
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(search_query, params + [limit, offset])

        history_entries = []
        for row in cursor.fetchall():
            history_entries.append({
                'id': row[0],
                'test_image_path': row[1],
                'recognized_faces': row[2],
                'total_faces_detected': row[3],
                'total_faces_recognized': row[4],
                'processing_time': row[5],
                'created_at': row[6]
            })

        conn.close()
        return history_entries, total_count

    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """Get recognition history statistics"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Total recognitions
        cursor.execute("SELECT COUNT(*) FROM recognition_history")
        total_recognitions = cursor.fetchone()[0]

        # Total faces processed
        cursor.execute("SELECT SUM(total_faces_detected) FROM recognition_history")
        result = cursor.fetchone()[0]
        total_faces_processed = result if result else 0

        # Total faces recognized
        cursor.execute("SELECT SUM(total_faces_recognized) FROM recognition_history")
        result = cursor.fetchone()[0]
        total_faces_recognized = result if result else 0

        # Average processing time
        cursor.execute("SELECT AVG(processing_time) FROM recognition_history")
        result = cursor.fetchone()[0]
        avg_processing_time = round(result, 3) if result else 0

        # Recognition rate
        recognition_rate = 0
        if total_faces_processed > 0:
            recognition_rate = round((total_faces_recognized / total_faces_processed) * 100, 2)

        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*)
            FROM recognition_history
            WHERE created_at >= datetime('now', '-7 days')
        """)
        recent_activity = cursor.fetchone()[0]

        # Daily activity for last 7 days
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM recognition_history
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        daily_activity = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]

        conn.close()

        return {
            'total_recognitions': total_recognitions,
            'total_faces_processed': total_faces_processed,
            'total_faces_recognized': total_faces_recognized,
            'recognition_rate': recognition_rate,
            'avg_processing_time': avg_processing_time,
            'recent_activity': recent_activity,
            'daily_activity': daily_activity
        }

# Initialize database when module is imported
if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
