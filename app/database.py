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

def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    if not database_exists():
        current_app.logger.info("Database does not exist. Creating...")
        try:
            # Create all tables directly for fresh installation
            db.create_all()
            current_app.logger.info("Database created successfully")
            
            # Create admin user directly since this is first-time setup
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
            current_app.logger.error(f"Error creating database: {str(e)}")
            raise
    return False

def clean_failed_migration():
    """Clean up any failed migration artifacts."""
    try:
        # Check if we're in a failed migration state
        engine = db.get_engine()
        inspector = db.inspect(engine)
        tables = inspector.get_table_names()
        
        # List of tables to handle migrations for
        migration_tables = ['user', 'event', 'booking']
        
        for table in migration_tables:
            temp_table = f"{table}_new"
            if temp_table in tables and table not in tables:
                current_app.logger.info(f"Found incomplete {table} migration, fixing...")
                with engine.connect() as conn:
                    conn.execute(db.text(f'ALTER TABLE {temp_table} RENAME TO {table}'))
                    conn.commit()
                current_app.logger.info(f"Fixed incomplete {table} migration")
            elif temp_table in tables:
                current_app.logger.info(f"Cleaning up {table} migration artifacts...")
                with engine.connect() as conn:
                    conn.execute(db.text(f'DROP TABLE IF EXISTS {temp_table}'))
                    conn.commit()
                current_app.logger.info(f"Cleaned up {table} migration artifacts")
    except Exception as e:
        current_app.logger.error(f"Error cleaning migration: {str(e)}")
        raise

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
        # Clean up any failed migrations first
        clean_failed_migration()
        
        # Only run migrations if it's not a fresh database
        if os.path.exists('migrations/versions'):
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
        
        # Initialize migrations directory if needed
        init_migrations()
        
        # Create database and run migrations as needed
        is_fresh_db = create_database_if_not_exists()
        if not is_fresh_db:
            run_migrations()
            
            # Check if admin user exists (only for existing databases)
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
            elif not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                current_app.logger.info("Updated existing user to admin")
    except Exception as e:
        current_app.logger.error(f"Error initializing database: {str(e)}")
        raise
