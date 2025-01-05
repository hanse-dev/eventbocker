from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from ..models import Event, Booking
from ..utils.email import send_event_registration_confirmation, send_admin_registration_notification
from .. import db

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bp.route('/', methods=['GET'])
@login_required
def list_bookings():
    """List all bookings for the current user."""
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return jsonify([booking.to_dict() for booking in bookings])

@bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a specific booking."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(booking.to_dict())

@bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_for_event(event_id):
    """Register current user for an event."""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is already registered
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        event_id=event_id
    ).first()
    
    if existing_booking:
        return jsonify({"error": "Already registered for this event"}), 400
        
    # Create new booking
    booking = Booking(
        user_id=current_user.id,
        event_id=event_id
    )
    
    try:
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email to user
        send_event_registration_confirmation(current_user.email, event)
        
        # Send notification to admin
        send_admin_registration_notification(event, current_user)
        
        return jsonify(booking.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
