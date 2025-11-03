"""
Configuration file for the Apartment Sharing Platform
Contains all application settings and environment variables
"""
import os
from datetime import timedelta

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class with common settings"""
    
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'apartment_platform.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder for apartment images
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/images/apartments')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Scheduler configuration for monthly rent payouts
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Africa/Cairo"  # Adjust to your timezone
    
    # Application settings
    ITEMS_PER_PAGE = 12  # For pagination
    
    # Color palette (extracted from logo - adjust these hex codes based on actual logo)
    PRIMARY_GOLD = "#D4AF37"  # Gold color for primary elements
    ACCENT_BEIGE = "#F5E6D3"  # Beige for accents
    BACKGROUND_NAVY = "#0A1929"  # Deep navy background
    SECONDARY_NAVY = "#1A2332"  # Slightly lighter navy
    TEXT_LIGHT = "#E8E8E8"  # Light text color
    
    # Admin credentials (in production, use environment variables)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@apartmentshare.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'


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
