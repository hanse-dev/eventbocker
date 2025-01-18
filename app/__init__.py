from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    with app.app_context():
        # Register blueprints
        from .routes.main import bp as main_bp
        from .routes.auth import bp as auth_bp
        from .routes.events import bp as events_bp
        from .routes.bookings import bp as bookings_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(events_bp)
        app.register_blueprint(bookings_bp)

        # Set up user loader for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            """Load a user given the ID."""
            from .models import User
            return User.query.get(int(user_id))

        # Initialize database
        from .database import init_database
        init_database()

    return app
