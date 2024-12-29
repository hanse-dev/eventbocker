#!/bin/sh

# Initialize migrations if they don't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations directory..."
    flask db init
fi

# Run any pending migrations
echo "Running database migrations..."
flask db migrate -m "Auto-migration"
flask db upgrade

# Start Flask development server with debug mode and auto-reloading
exec python -m flask run --host=0.0.0.0 --port=${PORT:-5001} --debug --reload
