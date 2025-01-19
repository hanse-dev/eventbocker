"""Database restoration utilities."""
from typing import Dict, Any
import json
from datetime import datetime
from flask import current_app
from app.models.models import db, User, Event, Booking
from app.utils.utils import get_utc_now

def load_backup(backup_path: str) -> Dict[str, Any]:
    """Load backup data from file.
    
    Args:
        backup_path: Path to backup file
        
    Returns:
        Dictionary containing backup data
    """
    try:
        with open(backup_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f'Failed to load backup: {str(e)}')
        raise

def restore_users(data: Dict[str, Any]) -> Dict[int, int]:
    """Restore user data from backup.
    
    Args:
        data: Backup data dictionary
        
    Returns:
        Dictionary mapping old user IDs to new user IDs
    """
    user_id_map = {}
    
    if 'user' not in data:
        return user_id_map
        
    current_app.logger.info('Restoring users...')
    for row in data['user']:
        old_id = row.pop('id')
        username = row.get('username')
        
        # Skip if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            current_app.logger.info(f'User {username} already exists, skipping...')
            user_id_map[old_id] = existing_user.id
            continue
        
        user = User(**row)
        db.session.add(user)
        db.session.flush()
        user_id_map[old_id] = user.id
        
    db.session.commit()
    return user_id_map

def restore_events(data: Dict[str, Any]) -> Dict[int, int]:
    """Restore event data from backup.
    
    Args:
        data: Backup data dictionary
        
    Returns:
        Dictionary mapping old event IDs to new event IDs
    """
    event_id_map = {}
    
    if 'event' not in data:
        return event_id_map
        
    current_app.logger.info('Restoring events...')
    with Event.bypass_validation():
        for row in data['event']:
            old_id = row.pop('id')
            if 'date' in row:
                row['date'] = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
            event = Event(**row)
            db.session.add(event)
            db.session.flush()
            event_id_map[old_id] = event.id
            
        db.session.commit()
    return event_id_map

def restore_bookings(data: Dict[str, Any], event_id_map: Dict[int, int]) -> Dict[int, int]:
    """Restore booking data from backup.
    
    Args:
        data: Backup data dictionary
        event_id_map: Dictionary mapping old event IDs to new event IDs
        
    Returns:
        Dictionary mapping old booking IDs to new booking IDs
    """
    booking_id_map = {}
    
    if 'booking' not in data:
        return booking_id_map
        
    current_app.logger.info('Restoring bookings...')
    for row in data.get('booking', []):
        try:
            if not row or 'event_id' not in row:
                current_app.logger.warning('Skipping invalid booking data:', row)
                continue
                
            old_id = row.pop('id', None)
            event_id = event_id_map.get(row['event_id'])
            
            if not event_id:
                current_app.logger.warning(f'Skipping booking - missing mapped event ID: {row["event_id"]}')
                continue
                
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
            current_app.logger.error(f'Error restoring booking: {str(e)}')
            continue
    
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Error committing bookings: {str(e)}')
        db.session.rollback()
        
    return booking_id_map

def restore_database(backup_path: str) -> None:
    """Restore database from backup file.
    
    Args:
        backup_path: Path to backup file
    """
    try:
        data = load_backup(backup_path)
        user_id_map = restore_users(data)
        event_id_map = restore_events(data)
        booking_id_map = restore_bookings(data, event_id_map)
        current_app.logger.info('Data restoration complete')
    except Exception as e:
        current_app.logger.error(f'Error restoring data: {str(e)}')
        db.session.rollback()
        raise
