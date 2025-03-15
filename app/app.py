from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .commands import create_admin, init_db
from .database import init_database
import os
import logging

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Register blueprints
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.events import bp as events_bp
    from .routes.bookings import bp as bookings_bp
    from .routes.files import bp as files_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(files_bp)

    # Configure upload directory
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Set up user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user given the ID."""
        from .models import User
        return User.query.get(int(user_id))

    return app

def init_app():
    """Initialize the application, including database setup."""
    app = create_app()
    with app.app_context():
        from .database import init_database
        init_database()
    return app

# Create the Flask application instance
app = init_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
