"""
Configuration Module

This module defines different configuration classes for various environments
(development, production, testing). It uses environment variables for sensitive
data and provides sensible defaults for development.

The configuration hierarchy is:
- Config (base class with common settings)
- DevelopmentConfig (for development environment)
- ProductionConfig (for production environment)
- TestConfig (for testing environment)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows for easy configuration management across different environments
load_dotenv()

class Config:
    """
    Base configuration class containing settings common to all environments.
    Uses environment variables with sensible defaults for development.
    """
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')  # Used for session security
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy event system (performance)
    
    # Admin credentials (should be changed in production)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    
    # Server configuration
    PORT = int(os.environ.get('PORT', 5001))
    
    # Email configuration
    DISABLE_EMAILS = os.environ.get('DISABLE_EMAILS', 'False').lower() == 'true'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5001')

class DevelopmentConfig(Config):
    """
    Development configuration with debugging enabled.
    Inherits from base Config class.
    """
    DEBUG = True
    
class ProductionConfig(Config):
    """
    Production configuration with secure settings.
    Inherits from base Config class.
    Should have DEBUG disabled and use secure values for sensitive settings.
    """
    DEBUG = False

class TestConfig(Config):
    """
    Test configuration for running unit tests.
    Uses in-memory SQLite database and test-specific settings.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'jwt-test-secret-key'
    MAIL_SUPPRESS_SEND = True  # Prevent sending actual emails during tests

# Configuration dictionary for easy access to different configs
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
