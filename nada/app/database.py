import os
from flask import current_app
from .extensions import db
from .models.models import User

def database_exists():
    """Check if the database file exists."""
    if current_app:
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        return os.path.exists(db_path)
    return False

def init_database(app):
    """Initialize the database."""
    with app.app_context():
        app.logger.info(f"Starting database initialization...")
        app.logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        app.logger.info(f"Instance path: {app.instance_path}")
        
        try:
            if not os.path.exists(app.instance_path):
                app.logger.info(f"Creating instance directory at {app.instance_path}")
                os.makedirs(app.instance_path)
                app.logger.info("Instance directory created successfully")
        except Exception as e:
            app.logger.error(f"Error creating instance directory: {str(e)}")
            raise

        try:
            app.logger.info("Creating database tables...")
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            raise

        try:
            # Check if admin user exists
            admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
            if not admin:
                app.logger.info("Creating admin user...")
                admin = User(username=app.config['ADMIN_USERNAME'])
                admin.set_password(app.config['ADMIN_PASSWORD'])
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Admin user created successfully")
            else:
                app.logger.info("Admin user already exists")
        except Exception as e:
            app.logger.error(f"Error managing admin user: {str(e)}")
            raise
