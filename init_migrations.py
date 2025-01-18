import os
import shutil
import glob
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy import text
import sqlite3

def get_migration_revision():
    """Get the revision ID from the latest migration file."""
    migration_files = glob.glob('migrations/versions/*.py')
    if not migration_files:
        return None
    
    # Read the latest migration file
    with open(migration_files[0], 'r') as f:
        content = f.read()
        # Extract revision ID from the file
        for line in content.split('\n'):
            if line.startswith('revision = '):
                return line.split("'")[1]
    return None

def init_migrations(force=True):
    # Create a minimal Flask app
    app = Flask(__name__)
    
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Get the database path
    db_path = os.path.join(instance_path, 'data.db')
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db = SQLAlchemy(app)
    
    # Define models here to ensure they're registered with this SQLAlchemy instance
    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(128))
        is_admin = db.Column(db.Boolean, default=False)
        email = db.Column(db.String(120))
        is_active = db.Column(db.Boolean, default=True)
        
    class Event(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.DateTime, nullable=False)
        capacity = db.Column(db.Integer)
        is_active = db.Column(db.Boolean, default=True)
        
    class Booking(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
        booking_date = db.Column(db.DateTime, nullable=False)
        status = db.Column(db.String(20), nullable=False)
        
    migrate_instance = Migrate(app, db)
    
    with app.app_context():
        # Drop alembic_version table if it exists
        db.session.execute(text('DROP TABLE IF EXISTS alembic_version'))
        db.session.commit()
        
        # Drop existing tables if they exist
        db.session.execute(text('DROP TABLE IF EXISTS booking'))
        db.session.execute(text('DROP TABLE IF EXISTS event'))
        db.session.execute(text('DROP TABLE IF EXISTS user'))
        db.session.commit()
        
        if force and os.path.exists('migrations'):
            print("Removing existing migrations directory...")
            shutil.rmtree('migrations')
        
        if not os.path.exists('migrations'):
            print("Initializing migrations directory...")
            init()
            
            print("Creating initial migration...")
            migrate(message='initial')
            
            # Get the revision ID from the generated migration
            revision = get_migration_revision()
            if revision:
                print(f"Setting migration version to: {revision}")
                db.session.execute(text('CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)'))
                db.session.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{revision}')"))
                db.session.commit()
                
                print("Applying initial migration...")
                upgrade()
            
            print("Migration setup complete.")
        else:
            print("Migrations directory already exists. No action needed.")

if __name__ == '__main__':
    init_migrations(force=True)
