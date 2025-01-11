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
# Database Migration Management
# =================================================================

export FLASK_APP=app.app
cd /app

log "Setting up database..."

# Create instance directory if it doesn't exist
mkdir -p /app/instance

# Clean up any existing migrations
if [ -d "/app/migrations" ]; then
    log "Removing existing migrations directory..."
    rm -rf /app/migrations
fi

# Initialize migrations
log "Initializing migrations..."
flask db init

# Create initial migration
log "Creating initial migration..."
flask db migrate -m "initial"

# Apply migrations
log "Applying migrations..."
flask db upgrade

# =================================================================
# Application Startup
# =================================================================

# Start Gunicorn
log "Starting Gunicorn server..."
exec gunicorn -w 4 -b 0.0.0.0:5001 --access-logfile - --error-logfile - --log-level info "app.app:create_app()"
