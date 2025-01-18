import os
import sys
import shutil
import glob
import subprocess
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
import sqlite3
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logger.debug(f"Added {project_root} to Python path")

# Set database path based on environment
is_docker = os.path.exists('/.dockerenv')
instance_path = os.path.join(project_root, 'instance')
os.makedirs(instance_path, exist_ok=True)

if is_docker:
    db_path = '/app/instance/data.db'
    db_uri = f'sqlite:////{db_path}'  # Four slashes for absolute path in Docker
else:
    db_path = os.path.join(instance_path, 'data.db')
    db_uri = f'sqlite:///{db_path}'  # Three slashes for relative path locally

# Set the database URL environment variable
os.environ['DATABASE_URL'] = db_uri
logger.debug(f"Set DATABASE_URL to {db_uri}")

try:
    from app.models.models import db, User, Event, Booking
    from app.app import create_app
    logger.debug("Successfully imported app modules")
except Exception as e:
    logger.error(f"Failed to import app modules: {str(e)}")
    raise

def backup_data(db):
    """Backup all data from the database."""
    data = {}
    tables = ['user', 'event', 'booking']
    
    for table in tables:
        try:
            result = db.session.execute(text(f'SELECT * FROM {table}')).fetchall()
            # Convert row objects to dictionaries
            data[table] = [dict(row._mapping) for row in result]
            logger.info(f"Backed up {len(data[table])} rows from {table}")
        except Exception as e:
            logger.warning(f"Could not backup table {table}: {str(e)}")
    
    return data

def ensure_schema_exists(app, db):
    """Ensure all tables exist with correct schema"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Schema created successfully")
            
            # Debug: show tables
            inspector = db.inspect(db.engine)
            for table_name in inspector.get_table_names():
                logger.debug(f"Table: {table_name}")
                for column in inspector.get_columns(table_name):
                    logger.debug(f"  Column: {column['name']} ({column['type']})")
        except Exception as e:
            logger.error(f"Failed to create schema: {str(e)}")
            raise

def run_flask_command(command, env=None):
    """Run a Flask CLI command"""
    try:
        # Prepare environment
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        
        # Add project root to PYTHONPATH
        if 'PYTHONPATH' in cmd_env:
            cmd_env['PYTHONPATH'] = f"{project_root}{os.pathsep}{cmd_env['PYTHONPATH']}"
        else:
            cmd_env['PYTHONPATH'] = project_root
        
        logger.debug(f"Running command: flask {command}")
        logger.debug(f"Environment: PYTHONPATH={cmd_env.get('PYTHONPATH')}")
        logger.debug(f"Environment: FLASK_APP={cmd_env.get('FLASK_APP')}")
        
        result = subprocess.run(
            f"flask {command}",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            env=cmd_env
        )
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        return False

def clean_database(db_path):
    """Clean up database connections and remove file"""
    try:
        # Close all database connections
        from sqlalchemy import create_engine
        engine = create_engine(f'sqlite:///{db_path}')
        with engine.connect() as conn:
            # Drop all tables to ensure a clean slate
            conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
            conn.execute(text('DROP TABLE IF EXISTS booking'))
            conn.execute(text('DROP TABLE IF EXISTS event'))
            conn.execute(text('DROP TABLE IF EXISTS user'))
            conn.commit()
        engine.dispose()
        logger.debug("Closed database connections")
        
        # Backup existing database
        if os.path.exists(db_path):
            logger.info("Backing up existing database...")
            backup_path = f"{db_path}.bak"
            shutil.copy2(db_path, backup_path)
            logger.debug(f"Created backup at {backup_path}")
            
            try:
                os.remove(db_path)
                logger.info("Removed existing database file")
            except Exception as e:
                logger.warning(f"Could not remove database file, trying to force close connections...")
                # Try to force close any remaining connections
                import sqlite3
                try:
                    conn = sqlite3.connect(db_path)
                    conn.close()
                except:
                    pass
                try:
                    os.remove(db_path)
                    logger.info("Successfully removed database file after closing connections")
                except Exception as e:
                    logger.warning(f"Still could not remove database file: {str(e)}")
    except Exception as e:
        logger.error(f"Error cleaning database: {str(e)}")
        raise

def restore_data(db, data):
    """Restore data to the database with schema migration."""
    try:
        # Track ID mappings for foreign key relationships
        user_id_map = {}  # old_id -> new_id
        event_id_map = {}  # old_id -> new_id
        
        # First restore users since they are referenced by bookings
        if 'user' in data:
            logger.info("Restoring user data...")
            for row in data['user']:
                old_id = row.pop('id')  # Remove id from the data
                user = User(**row)
                db.session.add(user)
                db.session.flush()  # Get the new ID
                user_id_map[old_id] = user.id
                logger.debug(f"Mapped user ID {old_id} -> {user.id}")
            db.session.commit()

        # Then restore events
        if 'event' in data:
            logger.info("Restoring event data...")
            for row in data['event']:
                old_id = row.pop('id')  # Remove id from the data
                event = Event(**row)
                db.session.add(event)
                db.session.flush()  # Get the new ID
                event_id_map[old_id] = event.id
                logger.debug(f"Mapped event ID {old_id} -> {event.id}")
            db.session.commit()

        # Finally restore bookings with updated schema
        if 'booking' in data:
            logger.info("Restoring booking data...")
            for row in data['booking']:
                old_event_id = row.pop('event_id')
                new_event_id = event_id_map.get(old_event_id)
                
                if not new_event_id:
                    logger.warning(f"Could not find mapped event ID for booking (old event_id: {old_event_id})")
                    continue
                
                # Get the user ID from the admin user for legacy bookings
                admin_id = next((new_id for old_id, new_id in user_id_map.items() 
                               if data['user'][old_id-1]['is_admin']), None)
                
                if not admin_id:
                    logger.warning("No admin user found for legacy bookings")
                    continue
                
                booking = Booking(
                    event_id=new_event_id,
                    user_id=admin_id,
                    created_at=row.get('created_at', datetime.utcnow())
                )
                db.session.add(booking)
            db.session.commit()

        logger.info("Data restoration complete")
    except Exception as e:
        logger.error(f"Error restoring data: {str(e)}")
        db.session.rollback()
        raise

def main():
    try:
        # Set environment variables
        os.environ['FLASK_APP'] = 'app.app:create_app'
        os.environ['FLASK_DEBUG'] = '0'  # Disable debug mode for migrations
        logger.debug(f"Set FLASK_APP to {os.environ['FLASK_APP']}")
        
        # Initialize Flask app
        app = create_app()
        logger.debug("Created Flask app")
        
        # Ensure instance directory exists
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        os.makedirs(instance_path, exist_ok=True)
        logger.debug(f"Created instance directory at {instance_path}")
        
        # Initialize migrations
        migrate = Migrate(app, db)
        logger.debug("Initialized Flask extensions")
        
        with app.app_context():
            # Backup existing data
            logger.info("Backing up existing data...")
            data = backup_data(db)
            
            # Remove existing migrations
            migrations_dir = 'migrations'
            if os.path.exists(migrations_dir):
                logger.info("Removing existing migrations...")
                shutil.rmtree(migrations_dir)
            
            # Clean up database and drop alembic_version table
            clean_database(db_path)
            
            # Create fresh database
            logger.info("Creating fresh database...")
            db.create_all()
            
            # Initialize new migrations
            logger.info("Initializing new migrations...")
            if not run_flask_command('db init', {'FLASK_APP': 'app.app:create_app'}):
                return
            
            # Create migration
            logger.info("Creating migration...")
            if not run_flask_command('db migrate -m "initial migration"', {'FLASK_APP': 'app.app:create_app'}):
                return
            
            # Apply migration
            logger.info("Applying migration...")
            if not run_flask_command('db upgrade', {'FLASK_APP': 'app.app:create_app'}):
                return
            
            # Make sure database is empty before restoring
            logger.info("Ensuring database is empty...")
            db.drop_all()
            db.create_all()
            
            # Restore data
            if data:
                logger.info("Restoring data...")
                restore_data(db, data)
            
            logger.info("Migration setup complete with data preserved.")
            
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
