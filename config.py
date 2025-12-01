"""
Flask application configuration
"""
import os
from datetime import timedelta

# Get absolute path to project directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings"""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT configuration for mobile API
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database configuration - Use Flask instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'  # Relative path creates instance/app.db automatically
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for apartment images
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/apartments')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size for faster uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Scheduler configuration for monthly rent payouts
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Africa/Cairo"  # Adjust to your timezone
    
    # Application settings
    ITEMS_PER_PAGE = 12  # For pagination
    
    # Color palette (Black & Gold Theme)
    PRIMARY_GOLD = "#FFD700"  # Bright Gold
    ACCENT_GOLD = "#FDB931"  # Lighter Gold
    BACKGROUND_BLACK = "#000000"  # Pure Black
    SECONDARY_BLACK = "#1A1A1A"  # Dark Gray
    TEXT_LIGHT = "#FFFFFF"  # White text
    
    # Admin credentials (in production, use environment variables)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'amsprog2022@gmail.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'Zo2lot@123'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries
    SCHEDULER_ENABLED = True  # Enable scheduler in development


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SCHEDULER_ENABLED = False  # Disable scheduler in production (PythonAnywhere doesn't support it)
    # In production, ensure SECRET_KEY is set via environment variable
    

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
