from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from ..extensions import db
from sqlalchemy.orm import validates
import pytz
from flask import current_app
import threading

def get_utc_now():
    """Get current UTC time."""
    return datetime.now(timezone.utc)

def get_local_now():
    """Get current local time."""
    return datetime.now().astimezone()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Add relationship to bookings
    bookings = db.relationship('Booking', backref='user', lazy=True, 
                             cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('username', name='uq_user_username'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.Column(db.Integer, default=0)
    room = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    
    # Add relationship to bookings
    event_bookings = db.relationship('Booking', backref='event', lazy=True, 
                                   cascade="all, delete-orphan")

    # Use thread-local storage for bypass flag to ensure thread safety
    _bypass_context = threading.local()

    @classmethod
    def bypass_validation(cls):
        """Context manager to bypass date validation."""
        class ValidationBypass:
            def __enter__(self):
                setattr(cls._bypass_context, 'bypass', True)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                setattr(cls._bypass_context, 'bypass', False)
                
        return ValidationBypass()

    @property
    def _bypass_validation(self):
        """Check if validation should be bypassed."""
        return getattr(self._bypass_context, 'bypass', False)

    @validates('date')
    def validate_date(self, key, date):
        """Validate that the event date is not in the past."""
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object")
        
        # Convert to timezone-aware if it's naive
        if not date.tzinfo:
            date = date.astimezone()
            
        # Skip validation if bypass flag is set
        if not self._bypass_validation:
            # Compare with local time
            if date < get_local_now():
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
        """Get all events that haven't happened yet."""
        now = get_local_now()
        query = cls.query.filter(cls.date >= now)
        if not include_invisible:
            query = query.filter_by(is_visible=True)
        return query.order_by(cls.date.asc()).all()

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, 
                       db.ForeignKey('user.id', ondelete='CASCADE', name='fk_booking_user'), 
                       nullable=True)  # Made nullable for anonymous bookings
    event_id = db.Column(db.Integer, 
                        db.ForeignKey('event.id', ondelete='CASCADE', name='fk_booking_event'), 
                        nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Added name field
    email = db.Column(db.String(120), nullable=False)  # Added email field
    phone = db.Column(db.String(20), nullable=False)   # Added phone field
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_event'),
    )
