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
from app.utils.db.backup import backup_database

app = create_app()
with app.app_context():
    backup_database('/app/instance/backup.json')
"
}

restore_data() {
    log "Restoring database data..."
    python3 -c "
from app.app import create_app
from app.utils.db.restore import restore_database

app = create_app()
with app.app_context():
    restore_database('/app/instance/backup.json')
"
}

clean_database() {
    log "Cleaning database state..."
    # Backup data first
    if [ -f "/app/instance/data.db" ]; then
        backup_data
    fi
    
    python3 -c "
from app.app import create_app
from app.utils.db.management import clean_database

app = create_app()
with app.app_context():
    clean_database('/app/migrations', '/app/instance/data.db')
"
}

init_fresh_database() {
    log "Initializing fresh database..."
    python3 -c "
from app.app import create_app
from app.utils.db.management import init_database

app = create_app()
with app.app_context():
    init_database()
"
}

init_fresh_migrations() {
    log "Initializing fresh migrations..."
    # Initialize migrations directory
    flask db init
}

handle_migrations() {
    # Check if migrations directory exists
    if [ ! -d "/app/migrations" ]; then
        init_fresh_migrations
    fi
    
    # Generate and apply migrations
    flask db migrate
    flask db upgrade
}

# =================================================================
# Main Script
# =================================================================

main() {
    # Clean and initialize database if needed
    if [ ! -f "/app/instance/data.db" ]; then
        init_fresh_database
        handle_migrations
        if [ -f "/app/instance/backup.json" ]; then
            restore_data
        fi
    fi
    
    # Start the application
    exec gunicorn -b 0.0.0.0:5001 "app.app:create_app()"
}

# Run main function
main
