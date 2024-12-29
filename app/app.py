from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .commands import create_admin, init_db
from .database import init_database
import os
import logging

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Set up logging to only show warnings and above
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Also set Flask's logger to warning level
    app.logger.setLevel(logging.WARNING)
    
    # Reduce logging level of werkzeug (Flask's development server)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    # Load the default configuration
    app.config.from_object('app.config.Config')

    # Override config with test config if passed
    if test_config is not None:
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register blueprints
    from .routes import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    @login_manager.user_loader
    def load_user(user_id):
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
    app.run(debug=False, host='0.0.0.0', port=port)
