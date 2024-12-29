"""Update datetime columns to store timezone info

Revision ID: 20241228_204500
Revises: 20241228_204219
Create Date: 2024-12-28 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20241228_204500'
down_revision = '20241228_204219'
branch_labels = None
depends_on = None


def upgrade():
    # Create temporary tables with timezone-aware datetime columns
    op.execute('''CREATE TABLE event_new (
        id INTEGER NOT NULL, 
        title VARCHAR(100) NOT NULL,
        description TEXT,
        date TIMESTAMP WITH TIME ZONE NOT NULL,
        capacity INTEGER NOT NULL,
        bookings INTEGER DEFAULT 0,
        room VARCHAR(100),
        address VARCHAR(200),
        is_visible BOOLEAN NOT NULL DEFAULT TRUE,
        price FLOAT NOT NULL DEFAULT 0.0,
        PRIMARY KEY (id)
    )''')
    
    op.execute('''CREATE TABLE booking_new (
        id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        FOREIGN KEY(event_id) REFERENCES event (id)
    )''')
    
    # Copy data from old tables to new tables
    op.execute('INSERT INTO event_new SELECT * FROM event')
    op.execute('INSERT INTO booking_new SELECT * FROM booking')
    
    # Drop old tables
    op.execute('DROP TABLE booking')
    op.execute('DROP TABLE event')
    
    # Rename new tables to original names
    op.execute('ALTER TABLE event_new RENAME TO event')
    op.execute('ALTER TABLE booking_new RENAME TO booking')


def downgrade():
    # Create temporary tables without timezone info
    op.execute('''CREATE TABLE event_new (
        id INTEGER NOT NULL, 
        title VARCHAR(100) NOT NULL,
        description TEXT,
        date TIMESTAMP NOT NULL,
        capacity INTEGER NOT NULL,
        bookings INTEGER DEFAULT 0,
        room VARCHAR(100),
        address VARCHAR(200),
        is_visible BOOLEAN NOT NULL DEFAULT TRUE,
        price FLOAT NOT NULL DEFAULT 0.0,
        PRIMARY KEY (id)
    )''')
    
    op.execute('''CREATE TABLE booking_new (
        id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        FOREIGN KEY(event_id) REFERENCES event (id)
    )''')
    
    # Copy data from current tables to new tables
    op.execute('INSERT INTO event_new SELECT * FROM event')
    op.execute('INSERT INTO booking_new SELECT * FROM booking')
    
    # Drop current tables
    op.execute('DROP TABLE booking')
    op.execute('DROP TABLE event')
    
    # Rename new tables to original names
    op.execute('ALTER TABLE event_new RENAME TO event')
    op.execute('ALTER TABLE booking_new RENAME TO booking')
