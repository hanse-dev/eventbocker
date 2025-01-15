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
# Environment Setup
# =================================================================

# Set default environment if not specified
FLASK_ENV=${FLASK_ENV:-production}
export FLASK_APP=app.app

cd /app

log "Running in ${FLASK_ENV} environment"

# =================================================================
# Database Migration Management
# =================================================================

log "Setting up database..."

# Create instance directory if it doesn't exist
mkdir -p /app/instance

# Initialize migrations if they don't exist
if [ ! -d "/app/migrations" ]; then
    log "Initializing migrations..."
    flask db init
fi

# Check for any pending changes and create a new migration if needed
if flask db current > /dev/null 2>&1; then
    log "Checking for model changes..."
    if flask db check > /dev/null 2>&1; then
        log "No model changes detected"
    else
        log "Model changes detected, creating new migration..."
        flask db migrate -m "auto migration $(date +%Y%m%d_%H%M%S)"
    fi
else
    log "No existing migrations found, creating initial migration..."
    flask db migrate -m "initial"
fi

# Apply any pending migrations
log "Applying migrations..."
flask db upgrade

# =================================================================
# Application Startup
# =================================================================

if [ "${FLASK_ENV}" = "development" ]; then
    # Start Flask development server with debugger
    log "Starting Flask development server..."
    exec python -m debugpy --listen 0.0.0.0:5678 -m flask run --host=0.0.0.0 --port=5001
else
    # Start Gunicorn for production
    log "Starting Gunicorn server..."
    exec gunicorn -w 4 -b 0.0.0.0:5001 --access-logfile - --error-logfile - --log-level info "app.app:create_app()"
fi
