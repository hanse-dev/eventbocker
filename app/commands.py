import click
from flask.cli import with_appcontext
from .models.models import db, User

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """Create an admin user."""
    user = User.query.filter_by(username=username).first()
    if user:
        click.echo('User already exists')
        return

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo('Admin user created successfully')

@click.command('init-db')
@with_appcontext
def init_db():
    """Initialize the database."""
    db.create_all()
    click.echo('Database initialized.')
