"""Database backup utilities."""
from typing import Dict, Any, List
import json
from sqlalchemy import text
from flask import current_app
from app.models.models import db

def backup_tables(tables: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Backup specified database tables.
    
    Args:
        tables: List of table names to backup
        
    Returns:
        Dictionary containing table data
    """
    data = {}
    
    for table in tables:
        try:
            result = db.session.execute(text(f'SELECT * FROM {table}')).fetchall()
            data[table] = [dict(row._mapping) for row in result]
            current_app.logger.info(f'Backed up {len(data[table])} rows from {table}')
        except Exception as e:
            current_app.logger.error(f'Could not backup table {table}: {str(e)}')
            
    return data

def save_backup(data: Dict[str, List[Dict[str, Any]]], backup_path: str) -> None:
    """Save backup data to file.
    
    Args:
        data: Dictionary containing table data
        backup_path: Path to save backup file
    """
    try:
        with open(backup_path, 'w') as f:
            json.dump(data, f, default=str)
        current_app.logger.info(f'Backup saved to {backup_path}')
    except Exception as e:
        current_app.logger.error(f'Failed to save backup: {str(e)}')
        raise

def backup_database(backup_path: str, tables: List[str] = None) -> None:
    """Backup database tables to file.
    
    Args:
        backup_path: Path to save backup file
        tables: Optional list of tables to backup, defaults to all tables
    """
    if tables is None:
        tables = ['user', 'event', 'booking']
        
    data = backup_tables(tables)
    save_backup(data, backup_path)
