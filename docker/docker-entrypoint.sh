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
# Main Functions
# =================================================================

handle_database() {
    log "Managing database using init_migrations.py..."
    python init_migrations.py
}

start_production_server() {
    log "Starting production server with gunicorn..."
    exec gunicorn \
        --bind "0.0.0.0:${PORT:-5001}" \
        --workers 4 \
        --threads 2 \
        --timeout 60 \
        --access-logfile - \
        --error-logfile - \
        "wsgi:app"
}

start_development_server() {
    log "Starting development server..."
    exec "$@"
}

# =================================================================
# Main Script
# =================================================================

main() {
    log "Starting application initialization..."
    
    # Always handle database first
    handle_database
    
    # Check environment and start appropriate server
    if [ "${FLASK_ENV:-production}" = "production" ]; then
        if [ "$1" = "gunicorn" ]; then
            start_production_server
        else
            exec "$@"
        fi
    else
        start_development_server "$@"
    fi
}

# Run main function with all script arguments
main "$@"
