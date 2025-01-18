import os
import shutil
from flask import current_app
from .extensions import db, migrate
from .models.models import User

def init_database():
    """Initialize the database and run migrations."""
    current_app.logger.info("Starting database initialization...")
    current_app.logger.info(f"Database URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
    current_app.logger.info(f"Instance path: {current_app.instance_path}")
    
    try:
        # Ensure instance directory exists
        os.makedirs(current_app.instance_path, exist_ok=True)
        
        # Create tables
        current_app.logger.info("Creating database tables...")
        db.create_all()
        
        # Create admin user if it doesn't exist
        with current_app.app_context():
            admin = User.query.filter_by(username=current_app.config['ADMIN_USERNAME']).first()
            if not admin:
                current_app.logger.info("Creating admin user...")
                admin = User(
                    username=current_app.config['ADMIN_USERNAME'],
                    is_admin=True
                )
                admin.set_password(current_app.config['ADMIN_PASSWORD'])
                db.session.add(admin)
                db.session.commit()
                current_app.logger.info("Admin user created successfully")
            
        return True
    except Exception as e:
        current_app.logger.error(f"Database initialization failed: {str(e)}")
        raise
