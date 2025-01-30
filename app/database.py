"""
Database Initialization Module

This module handles database initialization and setup, including:
- Creating necessary directories for file-based databases
- Creating database tables
- Setting up initial data (e.g., admin user)

The module is designed to work with both file-based and in-memory databases,
making it suitable for both production and testing environments.
"""

import os
import shutil
from flask import current_app
from .extensions import db, migrate
from .models.models import User

def init_database():
    """
    Initialize the database and run migrations.
    
    This function:
    1. Creates necessary directories for file-based databases
    2. Creates all database tables
    3. Sets up initial admin user (if not in testing mode)
    
    Returns:
        bool: True if initialization was successful
        
    Raises:
        Exception: If database initialization fails
    """
    current_app.logger.info("Starting database initialization...")
    current_app.logger.info(f"Database URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
    
    try:
        # Only create instance directory for file-based databases
        # In-memory databases (used in testing) don't need directory creation
        if not current_app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///:memory:'):
            current_app.logger.info(f"Instance path: {current_app.instance_path}")
            os.makedirs(current_app.instance_path, exist_ok=True)
        
        # Create all database tables defined in models
        current_app.logger.info("Creating database tables...")
        db.create_all()
        
        # Create admin user if it doesn't exist and we're not in testing mode
        # Skip admin creation in testing to keep tests focused and fast
        if not current_app.config.get('TESTING', False):
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
