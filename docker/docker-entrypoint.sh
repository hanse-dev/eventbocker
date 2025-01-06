#!/bin/sh
# Enable exit on error
set -e

# =================================================================
# Utility Functions
# =================================================================

# Logging function for consistent log format
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Error handler function for better debugging
handle_error() {
    log "Error occurred in script at line: ${1}"
    exit 1
}

# Set up error handling trap
trap 'handle_error ${LINENO}' ERR

# =================================================================
# Database Connection Check
# =================================================================

# Wait for database to be ready (skip for SQLite)
if [ -n "$DATABASE_URL" ] && [ "$DATABASE_URL" != "sqlite:////app/instance/data.db" ]; then
    log "Waiting for database to be ready..."
    max_retries=30
    counter=0
    # Try to connect to database with increasing delay
    until flask db current > /dev/null 2>&1 || [ $counter -eq $max_retries ]; do
        counter=$((counter+1))
        log "Attempt $counter/$max_retries: waiting for database..."
        sleep 1
    done
    if [ $counter -eq $max_retries ]; then
        log "Failed to connect to database after $max_retries attempts"
        exit 1
    fi
fi

# =================================================================
# Database Migration Management
# =================================================================

# Initialize database migrations if not already done
if [ ! -d "migrations" ]; then
    log "Initializing migrations directory..."
    flask db init
fi

# Apply any pending database migrations
log "Running database migrations..."
flask db migrate -m "Auto-migration" || log "No new migrations needed"
flask db upgrade

# =================================================================
# Application Server Startup
# =================================================================

# Start the appropriate server based on environment
if [ "$FLASK_ENV" = "production" ]; then
    log "Starting Gunicorn server in production mode..."
    # Start Gunicorn with production settings
    exec gunicorn --bind 0.0.0.0:${PORT:-5001} \
        --workers 4 \                    # Number of worker processes
        --threads 2 \                    # Number of threads per worker
        --timeout 60 \                   # Worker timeout in seconds
        --access-logfile - \             # Send access logs to stdout
        --error-logfile - \              # Send error logs to stdout
        --log-level warning \            # Set log level
        --capture-output \               # Capture stdout/stderr from workers
        --enable-stdio-inheritance \      # Enable stdio inheritance for better logging
        'app:create_app()'
else
    log "Starting Flask development server..."
    if [ "$FLASK_DEBUG" = "1" ]; then
        # Start with remote debugging enabled
        log "Debug mode enabled, starting with debugger..."
        exec python -m debugpy --listen 0.0.0.0:5678 --wait-for-client \
            -m flask run --host=0.0.0.0 --port=${PORT:-5001} --debug --reload
    else
        # Start regular development server
        exec python -m flask run --host=0.0.0.0 --port=${PORT:-5001} --debug --reload
    fi
fi
