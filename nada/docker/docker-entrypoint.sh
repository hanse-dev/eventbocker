#!/bin/bash
set -e

# Initialize the database if it doesn't exist
python -c "from nada.app import create_app; from nada.app.database import database_exists, init_database; app = create_app(); init_database(app) if not database_exists() else print('Database already exists')"

# Execute the main container command
exec "$@"
