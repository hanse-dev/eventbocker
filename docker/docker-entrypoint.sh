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

# Initialize database tables
log "Initializing database tables..."
python3 -c "
from app.app import create_app
from app.models.models import db
app = create_app()
with app.app_context():
    db.create_all()
" || log "Warning: Table creation failed, but continuing..."

# Initialize migrations if they don't exist
if [ ! -d "/app/migrations" ]; then
    log "Initializing new migrations..."
    flask db init || log "Warning: Migration initialization failed, but continuing..."
fi

# Check current migration state
log "Checking migration state..."
current_version=$(echo "SELECT version_num FROM alembic_version;" | sqlite3 /app/instance/data.db 2>/dev/null || echo "none")
log "Current database version: ${current_version}"

if [ "${current_version}" = "none" ]; then
    # No version - create and apply initial migration
    log "No version found, creating initial migration..."
    flask db migrate -m "initial migration" || log "Warning: Migration creation failed, but continuing..."
    flask db stamp head || log "Warning: Version stamping failed, but continuing..."
    flask db upgrade || log "Warning: Migration upgrade failed, but continuing..."
else
    # Version exists - check for and apply any pending migrations
    log "Checking for pending migrations..."
    flask db upgrade || {
        log "Warning: Migration upgrade failed, attempting to stamp and upgrade..."
        flask db stamp head
        flask db upgrade || log "Warning: Migration upgrade failed, but continuing..."
    }
fi

# Verify final database state
log "Final database state:"
echo ".tables" | sqlite3 /app/instance/data.db || true

# =================================================================
# Start Application
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
