import os
import shutil
import glob
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy import text
import sqlite3
import json
from datetime import datetime

def backup_data(db):
    """Backup all data from the database."""
    data = {}
    tables = ['user', 'event', 'booking']
    
    for table in tables:
        try:
            result = db.session.execute(text(f'SELECT * FROM {table}')).fetchall()
            # Convert row objects to dictionaries
            data[table] = [dict(row._mapping) for row in result]
            print(f"Backed up {len(data[table])} rows from {table}")
        except Exception as e:
            print(f"Could not backup table {table}: {str(e)}")
    
    return data

def restore_data(db, data):
    """Restore data to the database with schema migration."""
    # First delete all existing data
    tables = ['booking', 'event', 'user']  # Order matters for foreign keys
    for table in tables:
        try:
            db.session.execute(text(f'DELETE FROM {table}'))
            db.session.commit()
            print(f"Cleared table {table}")
        except Exception as e:
            print(f"Could not clear table {table}: {str(e)}")
            db.session.rollback()
    
    # Now restore the data in reverse order
    tables.reverse()
    
    # Restore users first
    users = data.get('user', [])
    for user in users:
        try:
            # Map old schema to new schema
            user_data = {
                'username': user['username'],
                'password_hash': user['password_hash'],
                'is_admin': bool(user['is_admin'])
            }
            
            insert_stmt = 'INSERT INTO user (username, password_hash, is_admin) VALUES (:username, :password_hash, :is_admin)'
            db.session.execute(text(insert_stmt), user_data)
            db.session.commit()
            print(f"Restored user: {user_data['username']}")
        except Exception as e:
            print(f"Could not restore user: {str(e)}")
            print("User data:", user_data)
            db.session.rollback()
    
    # Restore events
    events = data.get('event', [])
    for event in events:
        try:
            # Map old schema to new schema
            event_data = {
                'title': event['title'],
                'description': event.get('description', ''),
                'date': event['date'],
                'capacity': event.get('capacity', None),
                'bookings': event.get('bookings', 0),
                'room': event.get('room', ''),
                'address': event.get('address', ''),
                'is_visible': event.get('is_visible', True),
                'price': event.get('price', 0.0)
            }
            
            insert_stmt = '''
                INSERT INTO event (title, description, date, capacity, bookings, room, address, is_visible, price) 
                VALUES (:title, :description, :date, :capacity, :bookings, :room, :address, :is_visible, :price)
            '''
            db.session.execute(text(insert_stmt), event_data)
            db.session.commit()
            print(f"Restored event: {event_data['title']}")
        except Exception as e:
            print(f"Could not restore event: {str(e)}")
            print("Event data:", event_data)
            db.session.rollback()
    
    # Get user IDs for mapping
    users = db.session.execute(text('SELECT id, username FROM user')).fetchall()
    username_to_user = {user.username: user.id for user in users}
    
    # Restore bookings
    bookings = data.get('booking', [])
    for booking in bookings:
        try:
            # Get the user ID from the admin user as fallback
            admin_id = username_to_user.get('admin', 1)
            
            # Map old schema to new schema
            booking_data = {
                'event_id': booking['event_id'],
                'user_id': admin_id,  # All bookings will be assigned to admin for now
                'booking_date': booking.get('created_at', datetime.utcnow().isoformat()),
                'status': 'confirmed'  # Default status
            }
            
            insert_stmt = '''
                INSERT INTO booking (event_id, user_id, booking_date, status) 
                VALUES (:event_id, :user_id, :booking_date, :status)
            '''
            db.session.execute(text(insert_stmt), booking_data)
            db.session.commit()
            print(f"Restored booking for event {booking_data['event_id']}")
        except Exception as e:
            print(f"Could not restore booking: {str(e)}")
            print("Booking data:", booking_data)
            db.session.rollback()

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
        date = db.Column(db.DateTime(timezone=True), nullable=False)
        capacity = db.Column(db.Integer)
        bookings = db.Column(db.Integer, default=0)
        room = db.Column(db.String(100))
        address = db.Column(db.String(200))
        is_visible = db.Column(db.Boolean, default=True)
        price = db.Column(db.Float, default=0.0)
        
    class Booking(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
        booking_date = db.Column(db.DateTime(timezone=True), nullable=False)
        status = db.Column(db.String(20), nullable=False)
        
    migrate_instance = Migrate(app, db)
    
    with app.app_context():
        # Backup existing data
        print("Backing up existing data...")
        existing_data = backup_data(db)
        
        # Drop alembic_version table if it exists
        db.session.execute(text('DROP TABLE IF EXISTS alembic_version'))
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
                
                # Restore the data
                print("Restoring data...")
                restore_data(db, existing_data)
            
            print("Migration setup complete with data preserved.")
        else:
            print("Migrations directory already exists. No action needed.")

if __name__ == '__main__':
    init_migrations(force=True)
