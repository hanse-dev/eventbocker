from flask import Blueprint, jsonify

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/', methods=['GET'])
def list_events():
    """List all events."""
    return jsonify({"message": "Events listing endpoint"})

@bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event."""
    return jsonify({"message": f"Get event {event_id}"})
