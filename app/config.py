import os
import json
from dotenv import load_dotenv
from flask import current_app
import time

# Load environment variables from .env file
load_dotenv()

# Load JSON configuration
def load_json_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        if os.path.exists(config_path):
            # Get the modification time of the file
            mod_time = os.path.getmtime(config_path)
            
            # Read the file with explicit encoding
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Store the modification time in the config data for tracking
            config_data['_last_modified'] = mod_time
            return config_data
        else:
            return {
                "website": {
                    "name": "Veranstaltungsmanager",
                    "title": "Veranstaltungsverwaltung",
                    "description": "Plattform zur Verwaltung von Veranstaltungen und Buchungen",
                    "welcome_heading": "Willkommen bei Event Management",
                    "welcome_text": "Durchstöbern und buchen Sie kommende Veranstaltungen."
                },
                "contact": {
                    "email": "",
                    "phone": ""
                },
                "appearance": {
                    "primary_color": "#212529",
                    "secondary_color": "#6c757d",
                    "button_color": "#0080ff",
                    "logo_icon": "bi-calendar-event"
                },
                "_last_modified": time.time()
            }
    except Exception as e:
        print(f"Error loading JSON config: {e}")
        return {"_last_modified": time.time()}

# Function to reload configuration
def reload_config():
    """Reload the configuration from the JSON file and update the Flask app config."""
    if current_app:
        # Force reload by clearing any cached data
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        
        # Ensure the file exists
        if not os.path.exists(config_path):
            current_app.logger.error(f"Configuration file not found at {config_path}")
            return False
            
        try:
            # Load fresh configuration data
            with open(config_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            
            # Update application configuration
            current_app.config['WEBSITE_NAME'] = json_config.get('website', {}).get('name', 'Veranstaltungsmanager')
            current_app.config['WEBSITE_TITLE'] = json_config.get('website', {}).get('title', 'Veranstaltungsverwaltung')
            current_app.config['WEBSITE_DESCRIPTION'] = json_config.get('website', {}).get('description', 'Plattform zur Verwaltung von Veranstaltungen und Buchungen')
            current_app.config['WEBSITE_WELCOME_HEADING'] = json_config.get('website', {}).get('welcome_heading', 'Willkommen bei Event Management')
            current_app.config['WEBSITE_WELCOME_TEXT'] = json_config.get('website', {}).get('welcome_text', 'Durchstöbern und buchen Sie kommende Veranstaltungen.')
            current_app.config['CONTACT_EMAIL'] = json_config.get('contact', {}).get('email', '')
            current_app.config['CONTACT_PHONE'] = json_config.get('contact', {}).get('phone', '')
            current_app.config['PRIMARY_COLOR'] = json_config.get('appearance', {}).get('primary_color', '#212529')
            current_app.config['SECONDARY_COLOR'] = json_config.get('appearance', {}).get('secondary_color', '#6c757d')
            current_app.config['BUTTON_COLOR'] = json_config.get('appearance', {}).get('button_color', '#0080ff')
            current_app.config['LOGO_ICON'] = json_config.get('appearance', {}).get('logo_icon', 'bi-calendar-event')
            
            current_app.logger.info(f"Configuration reloaded successfully from {config_path}")
            return True
        except Exception as e:
            current_app.logger.error(f"Error reloading configuration: {e}")
            return False
    return False

# Load the JSON configuration
json_config = load_json_config()

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
    
    # Website configuration from JSON
    WEBSITE_NAME = json_config.get('website', {}).get('name', 'Veranstaltungsmanager')
    WEBSITE_TITLE = json_config.get('website', {}).get('title', 'Veranstaltungsverwaltung')
    WEBSITE_DESCRIPTION = json_config.get('website', {}).get('description', 'Plattform zur Verwaltung von Veranstaltungen und Buchungen')
    WEBSITE_WELCOME_HEADING = json_config.get('website', {}).get('welcome_heading', 'Willkommen bei Event Management')
    WEBSITE_WELCOME_TEXT = json_config.get('website', {}).get('welcome_text', 'Durchstöbern und buchen Sie kommende Veranstaltungen.')
    
    # Contact information
    CONTACT_EMAIL = json_config.get('contact', {}).get('email', '')
    CONTACT_PHONE = json_config.get('contact', {}).get('phone', '')
    
    # Appearance settings
    PRIMARY_COLOR = json_config.get('appearance', {}).get('primary_color', '#212529')
    SECONDARY_COLOR = json_config.get('appearance', {}).get('secondary_color', '#6c757d')
    BUTTON_COLOR = json_config.get('appearance', {}).get('button_color', '#0080ff')
    LOGO_ICON = json_config.get('appearance', {}).get('logo_icon', 'bi-calendar-event')

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
