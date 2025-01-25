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

handle_database() {
    log "Managing database using init_migrations.py..."
    python3 /app/init_migrations.py
}

# =================================================================
# Main Script
# =================================================================

main() {
    log "Starting application initialization..."
    
    # Handle database setup and migrations
    handle_database
    
    # Start the application
    log "Starting Flask application..."
    exec flask run --host=0.0.0.0
}

# Run main function
main
