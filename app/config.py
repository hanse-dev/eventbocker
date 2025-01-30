import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    
    # Server configuration
    PORT = int(os.environ.get('PORT', 5001))
    
    # Email configuration
    DISABLE_EMAILS = os.environ.get('DISABLE_EMAILS', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Used as default sender
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Mailjet configuration
    MAILJET_API_KEY = os.environ.get('MAILJET_API_KEY')
    MAILJET_API_SECRET = os.environ.get('MAILJET_API_SECRET')
    
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5001')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Set default configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
