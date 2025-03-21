import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(test_config=None, init_db=True):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    from .config import config, load_json_config
    
    # Load JSON configuration
    json_config = load_json_config()
    
    # Set configuration values from JSON
    app.config['WEBSITE_NAME'] = json_config.get('website', {}).get('name', 'Veranstaltungsmanager')
    app.config['WEBSITE_TITLE'] = json_config.get('website', {}).get('title', 'Veranstaltungsverwaltung')
    app.config['WEBSITE_DESCRIPTION'] = json_config.get('website', {}).get('description', '')
    app.config['WEBSITE_WELCOME_HEADING'] = json_config.get('website', {}).get('welcome_heading', '')
    app.config['WEBSITE_WELCOME_TEXT'] = json_config.get('website', {}).get('welcome_text', '')
    app.config['CONTACT_EMAIL'] = json_config.get('contact', {}).get('email', '')
    app.config['CONTACT_PHONE'] = json_config.get('contact', {}).get('phone', '')
    app.config['PRIMARY_COLOR'] = json_config.get('appearance', {}).get('primary_color', '#212529')
    app.config['SECONDARY_COLOR'] = json_config.get('appearance', {}).get('secondary_color', '#ffffff')
    app.config['LOGO_ICON'] = json_config.get('appearance', {}).get('logo_icon', 'bi-calendar-event')
    
    # Load configuration based on environment
    env = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[env])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Register blueprints
        from .routes.main import bp as main_bp
        from .routes.auth import bp as auth_bp
        from .routes.events import bp as events_bp
        from .routes.bookings import bp as bookings_bp
        from .routes.config import bp as config_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(events_bp)
        app.register_blueprint(bookings_bp)
        app.register_blueprint(config_bp)

        # Set up user loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            """Load a user given the ID."""
            from .models import User
            return User.query.get(int(user_id))
            
        # Add context processor for configuration
        @app.context_processor
        def inject_config():
            """Inject configuration into all templates."""
            return {
                'config': app.config
            }

        # Initialize database only if requested
        if init_db:
            from .database import init_database
            init_database()
            
    return app
