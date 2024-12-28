#!/usr/bin/env python3
"""Database initialization script.

This script initializes the SQLite database for the application.
It creates all necessary tables and sets up initial data if needed.
"""

from app import create_app
from app.database import init_database

def main():
    """Initialize the database with required tables and initial data."""
    try:
        app = create_app()
        with app.app_context():
            init_database()
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
