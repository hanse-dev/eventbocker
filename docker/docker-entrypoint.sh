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

# Debug: Check database file
if [ -f "/app/instance/data.db" ]; then
    log "Database file exists"
    # Debug: List tables in database
    echo ".tables" | sqlite3 /app/instance/data.db || true
else
    log "Database file does not exist"
fi

# Initialize database tables
log "Initializing database tables..."
python3 -c "
from app.app import create_app
from app.models.models import db
app = create_app()
with app.app_context():
    db.create_all()
" || log "Warning: Table creation failed, but continuing..."

# Check if migrations exist and apply them if needed
if [ -d "/app/migrations" ]; then
    log "Checking for pending migrations..."
    cd /app && flask db upgrade || {
        log "Warning: Migration upgrade failed, but continuing..."
    }
    
    # Debug: Check database after migration
    log "Database state after migration:"
    echo ".tables" | sqlite3 /app/instance/data.db || true
fi

# Debug: Show final database state
log "Final database state:"
echo ".tables" | sqlite3 /app/instance/data.db || true
if echo ".tables" | sqlite3 /app/instance/data.db | grep -q "event"; then
    log "Event table exists, showing contents:"
    echo "SELECT id, title, date, is_visible FROM event;" | sqlite3 /app/instance/data.db || true
else
    log "Event table does not exist"
fi

# =================================================================
# Application Startup
# =================================================================

if [ "${FLASK_ENV}" = "development" ]; then
    # Development mode is handled by docker-compose.override.yml
    log "Development mode startup skipped (handled by override)"
    exit 0
else
    # Start Gunicorn for production
    log "Starting Gunicorn server..."
    exec gunicorn -w 4 -b 0.0.0.0:5001 --access-logfile - --error-logfile - --log-level info "app.app:create_app()"
fi
