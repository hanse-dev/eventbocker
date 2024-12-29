from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from ..extensions import db
from sqlalchemy.orm import validates

def get_utc_now():
    """Get current UTC time."""
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)  # Store timezone-aware datetime
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.Column(db.Integer, default=0)
    room = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)

    @validates('date')
    def validate_date(self, key, date):
        """Validate that the event date is not in the past."""
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")
        
        if not date.tzinfo:
            raise ValueError("Date must be timezone-aware")
            
        if date < get_utc_now():
            raise ValueError("Event date cannot be in the past")
            
        return date

    @validates('capacity')
    def validate_capacity(self, key, capacity):
        """Validate that capacity is positive."""
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        return capacity

    @validates('price')
    def validate_price(self, key, price):
        """Validate that price is not negative."""
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price

    @classmethod
    def get_future_events(cls, include_invisible=False):
        """Get all events that haven't happened yet.
        
        Args:
            include_invisible (bool): If True, include invisible events (admin only)
        
        Returns:
            List of Event objects that are in the future, ordered by date
        """
        now = get_utc_now()  # Use our utility function
        query = cls.query.filter(cls.date >= now)
        if not include_invisible:
            query = query.filter_by(is_visible=True)
        return query.order_by(cls.date.asc()).all()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
