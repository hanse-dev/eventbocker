"""Add is_admin to User model

Revision ID: 20241228_204219
Revises: 
Create Date: 2024-12-28 20:42:19.123456

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241228_204219'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create a temporary table with the new schema
    op.execute('CREATE TABLE user_new (id INTEGER NOT NULL, username VARCHAR(80) NOT NULL, password_hash VARCHAR(120) NOT NULL, is_admin BOOLEAN NOT NULL DEFAULT FALSE, PRIMARY KEY (id), UNIQUE (username))')
    
    # Copy data from the old table to the new table
    op.execute('INSERT INTO user_new (id, username, password_hash, is_admin) SELECT id, username, password_hash, FALSE FROM user')
    
    # Drop the old table
    op.execute('DROP TABLE user')
    
    # Rename the new table to the original name
    op.execute('ALTER TABLE user_new RENAME TO user')


def downgrade():
    # Create a temporary table without the is_admin column
    op.execute('CREATE TABLE user_new (id INTEGER NOT NULL, username VARCHAR(80) NOT NULL, password_hash VARCHAR(120) NOT NULL, PRIMARY KEY (id), UNIQUE (username))')
    
    # Copy data from the current table to the new table
    op.execute('INSERT INTO user_new (id, username, password_hash) SELECT id, username, password_hash FROM user')
    
    # Drop the current table
    op.execute('DROP TABLE user')
    
    # Rename the new table to the original name
    op.execute('ALTER TABLE user_new RENAME TO user')
