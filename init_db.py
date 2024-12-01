from nada.app import create_app
from nada.app.database import init_database

app = create_app()
with app.app_context():
    init_database(app)
    print("Database initialized successfully!")
