"""
SQLite Database Module
Manages all database operations for the Agricultural Disease Detection System.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """SQLite Database Manager"""
    
    def __init__(self, db_path: str = "instance/disease_detection.db"):
        """Initialize database connection"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                image_filename TEXT NOT NULL,
                image_path TEXT NOT NULL,
                ai_advice TEXT,
                disease_summary TEXT,
                causes TEXT,
                treatment TEXT,
                fertilizer_recommendation TEXT,
                severity TEXT,
                prevention_tips TEXT,
                recovery_plan TEXT,
                dosage TEXT,
                application_timing TEXT,
                organic_alternative TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        self._ensure_prediction_columns(cursor)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                user_feedback TEXT,
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE
            )
        """)
        
        # Crop statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crop_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fertilizer recommendation catalog
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fertilizer_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                fertilizer TEXT NOT NULL,
                dosage TEXT,
                timing TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Voice query history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                question TEXT NOT NULL,
                transcript TEXT,
                ai_response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()

    def _ensure_prediction_columns(self, cursor):
        """Safely add newer prediction columns during migration."""
        cursor.execute("PRAGMA table_info(predictions)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "disease_summary": "TEXT",
            "causes": "TEXT",
            "treatment": "TEXT",
            "fertilizer_recommendation": "TEXT",
            "fertilizer_name": "TEXT",
            "npk_values": "TEXT",
            "spraying_interval": "TEXT",
            "fertilizer_notes": "TEXT",
            "severity": "TEXT",
            "prevention_tips": "TEXT",
            "recovery_plan": "TEXT",
            "dosage": "TEXT",
            "application_timing": "TEXT",
            "organic_alternative": "TEXT",
            "probability_data": "TEXT",
            "report_path": "TEXT",
            "report_generated_at": "TIMESTAMP"
        }

        for column_name, column_definition in required_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE predictions ADD COLUMN {column_name} {column_definition}"
                )
    
    # =====================================================
    # USER OPERATIONS
    # =====================================================
    
    def add_user(self, username: str, email: str, password_hash: str) -> Optional[int]:
        """Add new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # =====================================================
    # PREDICTION OPERATIONS
    # =====================================================
    
    def add_prediction(
        self,
        user_id: int,
        crop: str,
        disease: str,
        confidence: float,
        image_filename: str,
        image_path: str,
        ai_advice: Optional[str] = None,
        disease_summary: Optional[str] = None,
        causes: Optional[str] = None,
        treatment: Optional[str] = None,
        fertilizer_recommendation: Optional[str] = None,
        fertilizer_name: Optional[str] = None,
        npk_values: Optional[str] = None,
        spraying_interval: Optional[str] = None,
        fertilizer_notes: Optional[str] = None,
        severity: Optional[str] = None,
        prevention_tips: Optional[str] = None,
        recovery_plan: Optional[str] = None,
        dosage: Optional[str] = None,
        application_timing: Optional[str] = None,
        organic_alternative: Optional[str] = None,
        probability_data: Optional[str] = None,
        report_path: Optional[str] = None,
        report_generated_at: Optional[str] = None
    ) -> Optional[int]:
        """Add disease prediction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions 
                (user_id, crop, disease, confidence, image_filename, image_path, ai_advice, disease_summary, causes, treatment, fertilizer_recommendation, fertilizer_name, npk_values, spraying_interval, fertilizer_notes, severity, prevention_tips, recovery_plan, dosage, application_timing, organic_alternative, probability_data, report_path, report_generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                crop,
                disease,
                confidence,
                image_filename,
                image_path,
                ai_advice,
                disease_summary,
                causes,
                treatment,
                fertilizer_recommendation,
                fertilizer_name,
                npk_values,
                spraying_interval,
                fertilizer_notes,
                severity,
                prevention_tips,
                recovery_plan,
                dosage,
                application_timing,
                organic_alternative,
                probability_data,
                report_path,
                report_generated_at,
            ))
            conn.commit()
            pred_id = cursor.lastrowid
            conn.close()
            
            # Update crop statistics
            self.update_crop_stats(crop, disease)
            
            return pred_id
        except Exception as e:
            print(f"[ERROR] Failed to add prediction: {e}")
            return None

    def update_prediction_report(
        self,
        prediction_id: int,
        report_path: str,
        report_generated_at: str
    ) -> bool:
        """Update report metadata for a prediction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE predictions SET report_path = ?, report_generated_at = ? WHERE id = ?",
                (report_path, report_generated_at, prediction_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to update prediction report metadata: {e}")
            return False
    
    def get_prediction(self, prediction_id: int) -> Optional[Dict]:
        """Get prediction by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        prediction = dict(row)
        if prediction.get('probability_data'):
            try:
                prediction['all_probabilities'] = json.loads(prediction['probability_data'])
            except Exception:
                prediction['all_probabilities'] = None
        else:
            prediction['all_probabilities'] = None
        return prediction
    
    def get_user_predictions(
        self,
        user_id: int,
        limit: int = 50,
        search: str = None,
        crop: str = None,
        status: str = None,
        start_date: str = None,
        end_date: str = None,
        sort_by: str = 'created_at',
        sort_order: str = 'DESC'
    ) -> List[Dict]:
        """Get user's predictions history with optional filtering"""
        allowed_sort = {
            'created_at': 'created_at',
            'crop': 'crop',
            'disease': 'disease',
            'confidence': 'confidence'
        }
        sort_column = allowed_sort.get(sort_by, 'created_at')
        sort_order = 'ASC' if str(sort_order).upper() == 'ASC' else 'DESC'

        query = ["SELECT * FROM predictions WHERE user_id = ?"]
        params = [user_id]

        if crop and crop.lower() != 'all':
            query.append("AND LOWER(crop) = ?")
            params.append(crop.lower())

        if status and status.lower() == 'healthy':
            query.append("AND LOWER(disease) LIKE '%healthy%'")
        elif status and status.lower() == 'diseased':
            query.append("AND LOWER(disease) NOT LIKE '%healthy%'")

        if search:
            search_value = f"%{search.lower()}%"
            query.append(
                "AND (LOWER(crop) LIKE ? OR LOWER(disease) LIKE ? OR LOWER(created_at) LIKE ? OR CAST(confidence * 100 AS TEXT) LIKE ? )"
            )
            params.extend([search_value, search_value, search_value, search_value])

        if start_date:
            query.append("AND datetime(created_at) >= datetime(?)")
            params.append(start_date)

        if end_date:
            query.append("AND datetime(created_at) <= datetime(?)")
            params.append(end_date)

        query.append(f"ORDER BY {sort_column} {sort_order}")

        if limit and limit > 0:
            query.append("LIMIT ?")
            params.append(limit)

        final_query = ' '.join(query)
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(final_query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_crop_predictions(self, crop: str, limit: int = 100) -> List[Dict]:
        """Get all predictions for a specific crop"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM predictions 
            WHERE crop = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (crop, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_fertilizer_recommendation(
        self,
        crop: str,
        disease: str,
        fertilizer: str,
        dosage: Optional[str] = None,
        timing: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """Persist fertilizer recommendation metadata."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fertilizer_recommendations
                (crop, disease, fertilizer, dosage, timing, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                crop,
                disease,
                fertilizer,
                dosage,
                timing,
                notes
            ))
            conn.commit()
            rec_id = cursor.lastrowid
            conn.close()
            return rec_id
        except Exception as e:
            print(f"[ERROR] Failed to add fertilizer recommendation: {e}")
            return None

    def get_fertilizer_recommendations(self, crop: str, disease: str, limit: int = 5) -> List[Dict]:
        """Retrieve recent fertilizer recommendations for a crop and disease."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, crop, disease, fertilizer, dosage, timing, notes, created_at
            FROM fertilizer_recommendations
            WHERE crop = ? AND disease = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (crop, disease, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_voice_query(
        self,
        user_id: int,
        crop: str,
        disease: str,
        question: str,
        transcript: Optional[str] = None,
        ai_response: Optional[str] = None
    ) -> Optional[int]:
        """Add a voice assistant query and response history record"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO voice_queries
                (user_id, crop, disease, question, transcript, ai_response)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                crop,
                disease,
                question,
                transcript,
                ai_response
            ))
            conn.commit()
            query_id = cursor.lastrowid
            conn.close()
            return query_id
        except Exception as e:
            print(f"[ERROR] Failed to add voice query: {e}")
            return None

    def get_voice_queries(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get recent voice assistant query history for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, crop, disease, question, transcript, ai_response, created_at
            FROM voice_queries
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # =====================================================
    # FEEDBACK OPERATIONS
    # =====================================================
    
    def add_feedback(
        self,
        prediction_id: int,
        user_feedback: Optional[str] = None,
        rating: Optional[int] = None
    ) -> Optional[int]:
        """Add feedback for a prediction"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (prediction_id, user_feedback, rating)
                VALUES (?, ?, ?)
            """, (prediction_id, user_feedback, rating))
            conn.commit()
            feedback_id = cursor.lastrowid
            conn.close()
            return feedback_id
        except Exception as e:
            print(f"[ERROR] Failed to add feedback: {e}")
            return None
    
    def get_prediction_feedback(self, prediction_id: int) -> Optional[Dict]:
        """Get feedback for a prediction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback WHERE prediction_id = ?", (prediction_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # =====================================================
    # STATISTICS OPERATIONS
    # =====================================================
    
    def update_crop_stats(self, crop: str, disease: str):
        """Update crop disease statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute(
                "SELECT id, count FROM crop_stats WHERE crop = ? AND disease = ?",
                (crop, disease)
            )
            row = cursor.fetchone()
            
            if row:
                new_count = row[1] + 1
                cursor.execute(
                    "UPDATE crop_stats SET count = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_count, row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO crop_stats (crop, disease, count) VALUES (?, ?, 1)",
                    (crop, disease)
                )
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERROR] Failed to update crop stats: {e}")
    
    def get_crop_stats(self, crop: str) -> List[Dict]:
        """Get disease statistics for a crop"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT disease, count FROM crop_stats WHERE crop = ? ORDER BY count DESC",
            (crop,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total predictions
        cursor.execute("SELECT COUNT(*) as count FROM predictions")
        total_preds = cursor.fetchone()[0]
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()[0]
        
        # Predictions by crop
        cursor.execute("""
            SELECT crop, COUNT(*) as count 
            FROM predictions 
            GROUP BY crop
        """)
        crop_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Top diseases
        cursor.execute("""
            SELECT disease, COUNT(*) as count 
            FROM predictions 
            GROUP BY disease 
            ORDER BY count DESC 
            LIMIT 10
        """)
        top_diseases = [{"disease": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_predictions": total_preds,
            "total_users": total_users,
            "crop_distribution": crop_dist,
            "top_diseases": top_diseases
        }
