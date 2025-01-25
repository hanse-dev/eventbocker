#!/usr/bin/env python3
"""
Database Migration Manager

This module handles database migrations, backups, and data restoration for the Flask application.
It provides a robust way to:
1. Backup existing database data
2. Manage database schema migrations
3. Restore data after migrations
4. Handle different environments (development, docker)
"""

import os
import sys
import shutil
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuration manager for database settings."""
    
    def __init__(self):
        # Add project root to Python path
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)
            logger.debug(f"Added {self.project_root} to Python path")
        
        # Set up paths
        self.is_docker = os.path.exists('/.dockerenv')
        self.instance_path = os.path.join(self.project_root, 'instance')
        os.makedirs(self.instance_path, exist_ok=True)
        
        # Set database path
        self.db_path = '/app/instance/data.db' if self.is_docker else os.path.join(self.instance_path, 'data.db')
        self.db_uri = f'sqlite:///{self.db_path}'
        os.environ['DATABASE_URL'] = self.db_uri
        logger.debug(f"Database URI: {self.db_uri}")

class DatabaseBackup:
    """Handles database backup and restore operations."""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
    
    def export_tables(self, tables: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Export data from specified tables or all tables if none specified."""
        data = {}
        if tables is None:
            tables = self.db.metadata.tables.keys()
        
        for table in tables:
            try:
                result = self.db.session.execute(text(f'SELECT * FROM {table}')).fetchall()
                data[table] = [dict(row._mapping) for row in result]
                logger.info(f'Exported {len(data[table])} rows from {table}')
            except Exception as e:
                logger.error(f'Failed to export table {table}: {str(e)}')
        
        return data
    
    def save_to_file(self, data: Dict[str, List[Dict[str, Any]]], backup_path: str) -> None:
        """Save backup data to a JSON file."""
        try:
            with open(backup_path, 'w') as f:
                json.dump(data, f, default=str)
            logger.info(f'Backup saved to {backup_path}')
        except Exception as e:
            logger.error(f'Failed to save backup: {str(e)}')
            raise
    
    def load_from_file(self, backup_path: str) -> Dict[str, Any]:
        """Load backup data from a JSON file."""
        try:
            with open(backup_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f'Failed to load backup: {str(e)}')
            raise

class DatabaseRestore:
    """Handles database restoration process."""
    
    def __init__(self, db: SQLAlchemy):
        from app.models.models import User, Event, Booking
        self.db = db
        self.User = User
        self.Event = Event
        self.Booking = Booking
    
    def restore_data(self, data: Dict[str, Any]) -> None:
        """Restore database from backup data with proper foreign key handling."""
        try:
            # Clear existing data
            self._clear_tables()
            
            # Restore data with proper order
            id_maps = self._restore_users(data)
            id_maps.update(self._restore_events(data))
            self._restore_bookings(data, id_maps)
            
            self.db.session.commit()
            logger.info("Data restoration completed successfully")
        except Exception as e:
            logger.error(f"Error during restoration: {str(e)}")
            self.db.session.rollback()
            raise
    
    def _clear_tables(self) -> None:
        """Clear all tables in reverse dependency order."""
        for table in reversed(self.db.metadata.sorted_tables):
            self.db.session.execute(table.delete())
    
    def _restore_users(self, data: Dict[str, Any]) -> Dict[str, Dict[int, int]]:
        """Restore user data and return ID mappings."""
        id_maps = {'user': {}}
        if 'user' not in data:
            return id_maps
        
        for row in data['user']:
            old_id = row.pop('id')
            username = row.get('username')
            existing_user = self.User.query.filter_by(username=username).first()
            
            if existing_user:
                id_maps['user'][old_id] = existing_user.id
                continue
            
            user = self.User(**row)
            self.db.session.add(user)
            self.db.session.flush()
            id_maps['user'][old_id] = user.id
        
        return id_maps
    
    def _restore_events(self, data: Dict[str, Any]) -> Dict[str, Dict[int, int]]:
        """Restore event data and return ID mappings."""
        id_maps = {'event': {}}
        if 'event' not in data:
            return id_maps
        
        for row in data['event']:
            old_id = row.pop('id')
            event = self.Event(**row)
            self.db.session.add(event)
            self.db.session.flush()
            id_maps['event'][old_id] = event.id
        
        return id_maps
    
    def _restore_bookings(self, data: Dict[str, Any], id_maps: Dict[str, Dict[int, int]]) -> None:
        """Restore booking data using ID mappings."""
        if 'booking' not in data:
            return
        
        for row in data['booking']:
            old_id = row.pop('id')
            if 'event_id' in row and row['event_id'] in id_maps['event']:
                row['event_id'] = id_maps['event'][row['event_id']]
            booking = self.Booking(**row)
            self.db.session.add(booking)

class MigrationManager:
    """Manages the database migration process."""
    
    def __init__(self):
        # Import app modules
        try:
            from app.models.models import db
            from app.app import create_app
            self.db = db
            self.create_app = create_app
        except Exception as e:
            logger.error(f"Failed to import app modules: {str(e)}")
            raise
        
        # Initialize components
        self.config = DatabaseConfig()
        self.app = self.create_app()
        self.backup = DatabaseBackup(self.db)
        self.restore = DatabaseRestore(self.db)
        self.migrate = Migrate(self.app, self.db)
    
    def run_migration(self) -> bool:
        """Execute the migration process."""
        try:
            with self.app.app_context():
                # Backup existing data
                if os.path.exists(self.config.db_path):
                    logger.info("Backing up existing data...")
                    data = self.backup.export_tables()
                else:
                    data = None
                
                # Clean existing migrations
                if os.path.exists('migrations'):
                    logger.info("Removing existing migrations...")
                    shutil.rmtree('migrations')
                
                # Initialize new migrations
                logger.info("Initializing migrations...")
                self._run_flask_command('db init')
                self._run_flask_command('db migrate -m "migration"')
                self._run_flask_command('db upgrade')
                
                # Restore data if we had a backup
                if data:
                    logger.info("Restoring data from backup...")
                    self.restore.restore_data(data)
                
                logger.info("Migration completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            return False
    
    def _run_flask_command(self, command: str) -> bool:
        """Run a Flask CLI command."""
        try:
            os.system(f'flask {command}')
            return True
        except Exception as e:
            logger.error(f"Failed to run command '{command}': {str(e)}")
            return False

def main():
    """Main entry point for database migration."""
    manager = MigrationManager()
    success = manager.run_migration()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
