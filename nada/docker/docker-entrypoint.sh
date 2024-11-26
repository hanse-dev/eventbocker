#!/bin/sh

# Initialize the database and create admin user
python << END
from nada.app.app import app
from nada.app.extensions import db
from nada.app.models.models import User
import os

with app.app_context():
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(username=admin_username)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{admin_username}' created successfully")
    else:
        print(f"Admin user '{admin_username}' already exists")
END

# Execute the CMD
exec "$@"
