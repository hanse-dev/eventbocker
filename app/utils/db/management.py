"""Database management utilities."""
import os
from flask import current_app
from app.models.models import db

def clean_database(migrations_path: str, db_path: str) -> None:
    """Clean database state by dropping all tables and removing migrations.
    
    Args:
        migrations_path: Path to migrations directory
        db_path: Path to database file
    """
    # Drop all tables if they exist
    with current_app.app_context():
        db.drop_all()
    
    # Remove migration files
    if os.path.exists(migrations_path):
        for file in os.listdir(migrations_path):
            file_path = os.path.join(migrations_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    # Remove the database file
    if os.path.exists(db_path):
        os.remove(db_path)

def init_database() -> None:
    """Initialize fresh database by creating all tables."""
    with current_app.app_context():
        db.create_all()
        db.session.commit()
