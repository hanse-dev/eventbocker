import os
from flask import current_app
from .extensions import db, migrate
from .models.models import User
from flask_migrate import init as init_migrations_cmd
from flask_migrate import migrate as migrate_cmd
from flask_migrate import upgrade as upgrade_cmd

def database_exists():
    """Check if the database file exists."""
    if current_app:
        db_path = current_app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        return os.path.exists(db_path)
    return False

def init_migrations():
    """Initialize migrations if they don't exist."""
    if not os.path.exists('migrations/env.py'):
        current_app.logger.info("Initializing migrations directory...")
        init_migrations_cmd(directory='migrations')
        current_app.logger.info("Migrations directory initialized")

def run_migrations():
    """Run all pending migrations."""
    current_app.logger.info("Running database migrations...")
    try:
        migrate_cmd(directory='migrations', message='Auto-migration')
        upgrade_cmd(directory='migrations')
        current_app.logger.info("Database migrations completed")
    except Exception as e:
        current_app.logger.error(f"Error running migrations: {str(e)}")
        raise

def init_database():
    """Initialize the database and run migrations."""
    current_app.logger.info(f"Starting database initialization...")
    current_app.logger.info(f"Database URL: {current_app.config['SQLALCHEMY_DATABASE_URI']}")
    current_app.logger.info(f"Instance path: {current_app.instance_path}")
    
    try:
        # Create instance directory if it doesn't exist
        if not os.path.exists(current_app.instance_path):
            current_app.logger.info(f"Creating instance directory at {current_app.instance_path}")
            os.makedirs(current_app.instance_path)
            current_app.logger.info("Instance directory created successfully")
        
        # Initialize and run migrations
        init_migrations()
        run_migrations()
        
        # Check if admin user exists
        admin = User.query.filter_by(username=current_app.config['ADMIN_USERNAME']).first()
        if not admin:
            current_app.logger.info("Creating admin user...")
            admin = User(
                username=current_app.config['ADMIN_USERNAME'],
                is_admin=True  # Set admin flag
            )
            admin.set_password(current_app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            current_app.logger.info("Admin user created successfully")
        else:
            # Ensure existing admin user has admin privileges
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                current_app.logger.info("Updated existing user to admin")
            current_app.logger.info("Admin user already exists")
    except Exception as e:
        current_app.logger.error(f"Error initializing database: {str(e)}")
        raise
