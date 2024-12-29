from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models.models import Event, Booking, db
from datetime import datetime, timezone
from sqlalchemy import text

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated and current_user.is_admin:
        # Admin sees all future events, including invisible ones
        events = Event.get_future_events(include_invisible=True)
    else:
        # Non-admin users only see visible future events
        events = Event.get_future_events(include_invisible=False)
    return render_template('index.html', events=events)

@bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        capacity = int(request.form.get('capacity', 10))
        room = request.form.get('room')
        address = request.form.get('address')
        price = float(request.form.get('price', 0))
        
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        event = Event(
            title=title,
            description=description,
            date=date,
            capacity=capacity,
            room=room,
            address=address,
            price=price
        )
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('main.index'))
    
    default_date = datetime.now().strftime('%Y-%m-%dT%H:%M')
    return render_template('create_event.html', default_date=default_date)

@bp.route('/event/<int:event_id>/book', methods=['GET', 'POST'])
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        if event.bookings >= event.capacity:
            flash('Sorry, this event is fully booked!', 'error')
            return redirect(url_for('main.index'))
        
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        booking = Booking(event_id=event_id, name=name, email=email, phone=phone)
        event.bookings += 1
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('main.book_event', event_id=event_id))
    
    return render_template('book_event.html', event=event)

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        date_str = request.form['date']
        event.capacity = int(request.form.get('capacity', 10))
        event.room = request.form.get('room')
        event.address = request.form.get('address')
        event.price = float(request.form.get('price', 0))
        
        event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        db.session.commit()
        
        flash('Event updated successfully!', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_event.html', event=event)

@bp.route('/event/<int:event_id>/copy', methods=['POST'])
@login_required
def copy_event(event_id):
    # Get the original event
    original_event = Event.query.get_or_404(event_id)
    
    # Create a new event with the same details
    new_event = Event(
        title=f"Copy of {original_event.title}",
        description=original_event.description,
        date=original_event.date,
        capacity=original_event.capacity,
        room=original_event.room,
        address=original_event.address,
        price=original_event.price,
        bookings=0  # Start with 0 bookings
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    flash('Event copied successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/event/<int:event_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_visibility(event_id):
    event = Event.query.get_or_404(event_id)
    event.is_visible = not event.is_visible
    db.session.commit()
    flash('Event visibility updated successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/event/<int:event_id>/registrations')
@login_required
def view_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    bookings = Booking.query.filter_by(event_id=event_id).order_by(Booking.created_at.desc()).all()
    return render_template('registrations.html', event=event, bookings=bookings)

@bp.route('/booking/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    event = Event.query.get(booking.event_id)
    
    # Decrement the bookings count
    event.bookings = max(0, event.bookings - 1)
    
    # Delete the booking
    db.session.delete(booking)
    db.session.commit()
    
    flash('Anmeldung erfolgreich gelöscht.', 'success')
    return redirect(url_for('main.view_registrations', event_id=booking.event_id))

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Delete associated bookings first
    Booking.query.filter_by(event_id=event_id).delete()
    
    # Delete the event
    db.session.delete(event)
    db.session.commit()
    
    flash('Event successfully deleted.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/health')
def health_check():
    """Health check endpoint for Docker container."""
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503
