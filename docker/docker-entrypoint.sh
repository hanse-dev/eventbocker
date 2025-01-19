#!/bin/bash
# Enable strict mode
set -euo pipefail

# =================================================================
# Utility Functions
# =================================================================

# Logging function for consistent log format
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Error handler function for better debugging
error_handler() {
    local line_no=$1
    local error_code=$2
    log "Error (code: $error_code) occurred in script at line: $line_no"
    exit $error_code
}

# Set up error handling
trap 'error_handler ${LINENO} $?' ERR

# =================================================================
# Database Functions
# =================================================================

backup_data() {
    log "Backing up database data..."
    python3 -c "
from app.app import create_app
from app.models.models import db, User, Event, Booking
from sqlalchemy import text
import json
from datetime import datetime

app = create_app()
with app.app_context():
    data = {}
    tables = ['user', 'event', 'booking']
    
    for table in tables:
        try:
            result = db.session.execute(text(f'SELECT * FROM {table}')).fetchall()
            data[table] = [dict(row._mapping) for row in result]
            print(f'Backed up {len(data[table])} rows from {table}')
        except Exception as e:
            print(f'Could not backup table {table}: {str(e)}')
    
    # Save to file
    with open('/app/instance/backup.json', 'w') as f:
        json.dump(data, f, default=str)
"
}

restore_data() {
    log "Restoring database data..."
    python3 -c "
from app.app import create_app
from app.models.models import db, User, Event, Booking
import json
from datetime import datetime
import pytz
from app.utils.utils import get_utc_now

app = create_app()
with app.app_context():
    try:
        with open('/app/instance/backup.json', 'r') as f:
            data = json.load(f)
        
        # Track ID mappings
        user_id_map = {}
        event_id_map = {}
        booking_id_map = {}
        
        # Restore users
        if 'user' in data:
            print('Restoring users...')
            for row in data['user']:
                old_id = row.pop('id')
                username = row.get('username')
                
                # Skip if user already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    print(f'User {username} already exists, skipping...')
                    user_id_map[old_id] = existing_user.id
                    continue
                
                user = User(**row)
                db.session.add(user)
                db.session.flush()
                user_id_map[old_id] = user.id
            db.session.commit()

        # Restore events
        if 'event' in data:
            print('Restoring events...')
            with Event.bypass_validation():
                for row in data['event']:
                    old_id = row.pop('id')
                    # Convert date string to datetime
                    if 'date' in row:
                        row['date'] = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                    event = Event(**row)
                    db.session.add(event)
                    db.session.flush()
                    event_id_map[old_id] = event.id
                db.session.commit()

        # Restore bookings
        if 'booking' in data:
            print('Restoring bookings...')
            for row in data.get('booking', []):
                try:
                    if not row or 'event_id' not in row:
                        print('Skipping invalid booking data:', row)
                        continue
                        
                    old_id = row.pop('id', None)
                    event_id = event_id_map.get(row['event_id'])
                    
                    if not event_id:
                        print(f'Skipping booking - missing mapped event ID: {row["event_id"]}')
                        continue
                        
                    row['event_id'] = event_id
                    
                    # Convert created_at to datetime if present
                    if 'created_at' in row:
                        row['created_at'] = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                    
                    # Create booking with the new fields
                    booking = Booking(
                        event_id=event_id,
                        name=row['name'],
                        email=row['email'],
                        phone=row['phone'],
                        created_at=row.get('created_at', get_utc_now())
                    )
                    
                    db.session.add(booking)
                    if old_id:
                        db.session.flush()
                        booking_id_map[old_id] = booking.id
                except Exception as e:
                    print(f'Error restoring booking: {str(e)}')
                    continue
            
            try:
                db.session.commit()
            except Exception as e:
                print(f'Error committing bookings: {str(e)}')
                db.session.rollback()
            
        print('Data restoration complete')
    except Exception as e:
        print(f'Error restoring data: {str(e)}')
        db.session.rollback()
        raise
"
}

clean_database() {
    log "Cleaning database state..."
    # Backup data first
    if [ -f "/app/instance/data.db" ]; then
        backup_data
    fi
    
    # Drop all tables if they exist
    python3 -c "
from app.app import create_app
from app.models.models import db
app = create_app()
with app.app_context():
    db.drop_all()
"
    # Remove migration files
    rm -rf /app/migrations/*
    # Remove the database file
    rm -f /app/instance/data.db
}

init_fresh_database() {
    log "Initializing fresh database..."
    # Create tables in the correct order
    python3 -c "
from app.app import create_app
from app.models.models import db
app = create_app()
with app.app_context():
    db.create_all()
    db.session.commit()
"
}

init_fresh_migrations() {
    log "Initializing fresh migrations..."
    
    # Clean everything first
    clean_database
    
    # Initialize migrations
    export PYTHONPATH=/app
    flask db init
    
    # Create fresh database with tables
    init_fresh_database
    
    # Create initial migration
    flask db migrate -m "Initial migration"
    
    # Apply migration
    flask db upgrade
    
    # Restore data if backup exists
    if [ -f "/app/instance/backup.json" ]; then
        restore_data
    fi
}

handle_migrations() {
    # Create instance directory if it doesn't exist
    mkdir -p /app/instance
    
    # Check if database file exists
    if [ ! -f "/app/instance/data.db" ]; then
        log "Database file not found. Initializing fresh database..."
        init_fresh_migrations
        return
    fi
    
    # Check if migrations directory exists and has versions
    if [ ! -d "/app/migrations/versions" ] || [ -z "$(ls -A /app/migrations/versions 2>/dev/null)" ]; then
        log "No migration versions found. Initializing fresh migrations..."
        init_fresh_migrations
        return
    fi
    
    # Try to upgrade existing migrations
    log "Attempting database upgrade..."
    if ! flask db upgrade; then
        log "Warning: Migration upgrade failed, attempting fresh initialization..."
        init_fresh_migrations
    fi
}

# =================================================================
# Main Script
# =================================================================

main() {
    log "Starting application initialization..."
    
    # Set Python path
    export PYTHONPATH=/app
    
    # Handle migrations
    handle_migrations
    
    # Start the Flask application
    log "Starting Flask application..."
    exec flask run --host=0.0.0.0 --port=${PORT:-5001}
}

# Run main function
main
