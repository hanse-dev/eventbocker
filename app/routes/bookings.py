from flask import Blueprint, jsonify, request, current_app, redirect, url_for
from flask_login import current_user, login_required
from ..models import Event, Booking
from ..utils.email import send_event_registration_confirmation, send_admin_registration_notification
from ..extensions import db

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bp.route('/', methods=['GET'])
@login_required
def list_bookings():
    """List all bookings for the current user."""
    bookings = Booking.query.filter_by(email=current_user.email).all()
    return jsonify([booking.to_dict() for booking in bookings])

@bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def get_booking(booking_id):
    """Get a specific booking."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.email != current_user.email:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(booking.to_dict())

@bp.route('/register/<int:event_id>', methods=['POST'])
@login_required
def register_for_event(event_id):
    """Redirect to the main booking system."""
    return redirect(url_for('main.book_event', event_id=event_id))
