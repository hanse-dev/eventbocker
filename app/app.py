"""
Flask Application Factory Module

This module contains the application factory and related setup code for the Flask application.
It follows the factory pattern to allow for multiple instances of the app (e.g., testing, development, production).

The create_app function is the core of this module, responsible for:
1. Creating the Flask application instance
2. Loading configuration
3. Initializing extensions (database, login, mail)
4. Registering blueprints (routes)
5. Setting up CLI commands
"""

from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .commands import create_admin, init_db
from .database import init_database
from .utils.email import mail
import os
import logging

def create_app(config_object=None):
    """
    Create and configure an instance of the Flask application.
    
    Args:
        config_object: Configuration object to use. If None, uses default Config.
                      This allows for different configs in different environments
                      (e.g., testing, development, production)
    
    Returns:
        Flask application instance fully configured and ready to run
    """
    app = Flask(__name__)
    
    # Load the default configuration or use provided config object
    # This allows for different configurations in different environments
    if config_object is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_object)

    # Initialize Flask extensions
    # These provide core functionality like database access and authentication
    db.init_app(app)          # SQLAlchemy for database operations
    migrate.init_app(app, db) # Alembic for database migrations
    login_manager.init_app(app) # Flask-Login for user session management
    mail.init_app(app)        # Flask-Mail for email functionality
    
    # Register blueprints
    # Blueprints organize routes into logical groups
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.events import bp as events_bp
    from .routes.bookings import bp as bookings_bp
    
    app.register_blueprint(main_bp)     # Main routes (home, about, etc.)
    app.register_blueprint(auth_bp)     # Authentication routes
    app.register_blueprint(events_bp)   # Event management routes
    app.register_blueprint(bookings_bp) # Booking management routes

    # Set up user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user given the ID."""
        from .models import User
        return User.query.get(int(user_id))

    # Add CLI commands for database management and admin creation
    app.cli.add_command(create_admin)
    app.cli.add_command(init_db)

    return app

# Only initialize database when running the actual application
# This prevents database initialization during testing or when importing the module
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        init_database()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
