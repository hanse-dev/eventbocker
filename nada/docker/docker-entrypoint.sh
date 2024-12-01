#!/bin/sh

# Initialize the database
python -c "from nada.app import create_app; app = create_app(); from nada.app.database import init_database; init_database(app)"

# Start the Flask application
exec python -m flask run --host=0.0.0.0 --port=${PORT:-8080}
