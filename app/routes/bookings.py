from flask import Blueprint, jsonify

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bp.route('/', methods=['GET'])
def list_bookings():
    """List all bookings."""
    return jsonify({"message": "Bookings listing endpoint"})

@bp.route('/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get a specific booking."""
    return jsonify({"message": f"Get booking {booking_id}"})
