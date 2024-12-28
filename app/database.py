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

def init_database():
    """Initialize the database."""
    current_app.logger.info(f"Starting database initialization...")
    current_app.logger.info(f"Database URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
    current_app.logger.info(f"Instance path: {current_app.instance_path}")
    
    try:
        if not os.path.exists(current_app.instance_path):
            current_app.logger.info(f"Creating instance directory at {current_app.instance_path}")
            os.makedirs(current_app.instance_path)
            current_app.logger.info("Instance directory created successfully")
        
        current_app.logger.info("Creating database tables...")
        db.create_all()
        current_app.logger.info("Database tables created successfully")
        
        # Check if admin user exists
        admin = User.query.filter_by(username=current_app.config['ADMIN_USERNAME']).first()
        if not admin:
            current_app.logger.info("Creating admin user...")
            admin = User(username=current_app.config['ADMIN_USERNAME'])
            admin.set_password(current_app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info("Admin user created successfully")
        else:
            current_app.logger.info("Admin user already exists")
    except Exception as e:
        current_app.logger.error(f"Error initializing database: {str(e)}")
        raise
