#!/bin/sh

# Initialize the database
python -m flask --app nada/app init-db

# Start Flask development server with debug mode
exec python -m flask --app nada/app run --host=0.0.0.0 --port=${PORT} --debug
