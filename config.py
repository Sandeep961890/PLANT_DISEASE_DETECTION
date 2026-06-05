"""
Configuration Module
Centralized configuration for the Flask application.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    
    # Database settings
    DATABASE_PATH = os.path.join('instance', 'disease_detection.db')
    REPORTS_FOLDER = os.path.join(os.getcwd(), 'reports')
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Model settings
    MODEL_CONFIG = {
        "banana": {
            "model": "outputs/banana/banana_svm_model.pkl",
            "encoder": "outputs/banana/label_encoder.pkl",
            "diseases": ["Cordana", "Healthy", "Pestalotiopsis", "Sigatoka"]
        },
        "corn": {
            "model": "outputs/corn/corn_svm_model.pkl",
            "encoder": "outputs/corn/label_encoder.pkl",
            "diseases": ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]
        },
        "sugarcane": {
            "model": "outputs/sugarcane/sugarcane_svm_model.pkl",
            "encoder": "outputs/sugarcane/label_encoder.pkl",
            "diseases": ["BacterialBlights", "Healthy", "Mosaic", "RedRot", "Rust", "Yellow"]
        }
    }
    
    # Ollama settings
    OLLAMA_MODEL = "llava-llama3:8b"
    OLLAMA_TIMEOUT = 60  # seconds
    
    # Image processing settings
    IMAGE_SIZE = (224, 224)
    BATCH_SIZE = 32
    
    # Feature extractor settings
    FEATURE_EXTRACTOR_GPU = True
    
    # Ensure upload and report folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(REPORTS_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False

    SESSION_COOKIE_SECURE = True

    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'my_super_secret_dev_key'
    )

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = os.path.join('instance', 'test_disease_detection.db')
    WTF_CSRF_ENABLED = False


# Configuration selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env: str = None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
