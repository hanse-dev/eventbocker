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

# Start the application with gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:${PORT:-5001} \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level warning \
    'app:create_app()'
