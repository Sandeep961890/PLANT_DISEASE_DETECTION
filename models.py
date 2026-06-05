"""
Database Models using SQLAlchemy ORM
Replaces raw SQL for better type safety and ORM patterns.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json


class User:
    """User model"""
    
    def __init__(self, id=None, username=None, email=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
    
    @staticmethod
    def hash_password(password):
        """Hash password for storage"""
        return generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Prediction:
    """Prediction model"""
    
    def __init__(self, id=None, user_id=None, crop=None, disease=None, 
                 confidence=None, image_filename=None, image_path=None, 
                 ai_advice=None, fertilizer_recommendation=None,
                 dosage=None, application_timing=None,
                 organic_alternative=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.crop = crop
        self.disease = disease
        self.confidence = confidence
        self.image_filename = image_filename
        self.image_path = image_path
        self.ai_advice = ai_advice
        self.fertilizer_recommendation = fertilizer_recommendation
        self.dosage = dosage
        self.application_timing = application_timing
        self.application_schedule = application_timing
        self.organic_alternative = organic_alternative
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'crop': self.crop,
            'disease': self.disease,
            'confidence': self.confidence,
            'confidence_percent': f"{self.confidence * 100:.2f}%" if self.confidence is not None else "0%",
            'image_filename': self.image_filename,
            'image_path': self.image_path,
            'ai_advice': self.ai_advice,
            'fertilizer_recommendation': self.fertilizer_recommendation,
            'dosage': self.dosage,
            'application_timing': self.application_timing,
            'application_schedule': self.application_schedule,
            'organic_alternative': self.organic_alternative,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Feedback:
    """Feedback model"""
    
    def __init__(self, id=None, prediction_id=None, user_feedback=None, 
                 rating=None, created_at=None):
        self.id = id
        self.prediction_id = prediction_id
        self.user_feedback = user_feedback
        self.rating = rating
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'user_feedback': self.user_feedback,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CropStat:
    """Crop statistics model"""
    
    def __init__(self, id=None, crop=None, disease=None, count=None, updated_at=None):
        self.id = id
        self.crop = crop
        self.disease = disease
        self.count = count or 1
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'crop': self.crop,
            'disease': self.disease,
            'count': self.count,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
