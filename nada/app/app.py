from flask import Flask
from .config import Config
from .extensions import db, login_manager
from .models.models import User
from .commands import create_admin, init_db
from .database import init_database
import os

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Set up logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Load the default configuration
    app.config.from_object('nada.app.config.Config')

    # Override config with test config if passed
    if test_config is not None:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .routes import main, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)

    # Register CLI commands
    app.cli.add_command(create_admin)
    app.cli.add_command(init_db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Initialize database and admin user
    init_database(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
