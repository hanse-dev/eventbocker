from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from ..models.models import Event, Booking, db
from datetime import datetime, timezone
from sqlalchemy import text
from ..utils.email import send_event_registration_confirmation
import traceback

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated and current_user.is_admin:
        # Admin sees all future events, including invisible ones
        events = Event.get_future_events(include_invisible=True)
        return render_template('index.html', events=events)
    else:
        # Non-admin users only see visible future events
        events = Event.get_future_events(include_invisible=False)
        return render_template('index.html', events=events)

@bp.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            date_str = request.form['date']
            capacity = int(request.form.get('capacity', 10))
            room = request.form.get('room')
            address = request.form.get('address')
            price = float(request.form.get('price', 0))
            
            # Parse the date and make it timezone-aware
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
            
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
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f"Error in create_event: {str(e)}\n{traceback.format_exc()}")
            flash(str(e), 'danger')
            return render_template('create_event.html', 
                                default_date=date_str,
                                form_data=request.form)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in create_event: {str(e)}\n{traceback.format_exc()}")
            flash('An error occurred while creating the event.', 'danger')
            return render_template('create_event.html', 
                                default_date=date_str,
                                form_data=request.form)
    
    default_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M')
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
        
        try:
            # Start transaction
            db.session.begin_nested()  # Create a savepoint
            
            # Add booking and increment counter
            db.session.add(booking)
            event.bookings += 1
            
            # Try to send email first before committing
            send_event_registration_confirmation(email, event)
            
            # If email sent successfully, commit the transaction
            db.session.commit()
            
            flash('Booking successful! A confirmation email has been sent to your email address.', 'success')
            return redirect(url_for('main.book_event', event_id=event_id))
            
        except Exception as e:
            # Roll back to the savepoint
            db.session.rollback()
            current_app.logger.error(f"Error in book_event: {str(e)}\n{traceback.format_exc()}")
            flash('An error occurred while processing your booking. Please try again.', 'error')
            return redirect(url_for('main.book_event', event_id=event_id))
    
    return render_template('book_event.html', event=event)

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # Use get() instead of get_or_404() for better performance
    event = Event.query.get(event_id)
    if not event:
        flash('Event not found.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Batch update attributes
            form_data = {
                'title': request.form['title'],
                'description': request.form['description'],
                'capacity': int(request.form.get('capacity', 10)),
                'room': request.form.get('room'),
                'address': request.form.get('address'),
                'price': float(request.form.get('price', 0))
            }
            
            # Update all fields at once
            for key, value in form_data.items():
                setattr(event, key, value)
            
            # Handle date separately due to timezone
            date_str = request.form['date']
            event.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M').replace(tzinfo=timezone.utc)
            
            # Use a single commit for all changes
            db.session.commit()
            
            flash('Event updated successfully!', 'success')
            return redirect(url_for('main.index'))
            
        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f"Error in edit_event: {str(e)}\n{traceback.format_exc()}")
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in edit_event: {str(e)}\n{traceback.format_exc()}")
            flash('An error occurred while updating the event.', 'danger')
    
    return render_template('edit_event.html', event=event)

@bp.route('/event/<int:event_id>/copy', methods=['POST'])
@login_required
def copy_event(event_id):
    try:
        # Get the original event
        original_event = Event.query.get_or_404(event_id)
        
        # Ensure the date is timezone-aware
        event_date = original_event.date
        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)
        
        # Create a new event with the same details
        new_event = Event(
            title=f"Copy of {original_event.title}",
            description=original_event.description,
            date=event_date,
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
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Error in copy_event: {str(e)}\n{traceback.format_exc()}")
        flash(str(e), 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in copy_event: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while copying the event.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/event/<int:event_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_visibility(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        event.is_visible = not event.is_visible
        db.session.commit()
        status = "visible" if event.is_visible else "hidden"
        flash(f'Event is now {status}', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in toggle_visibility: {str(e)}\n{traceback.format_exc()}")
        flash('Error updating event visibility', 'danger')
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
    try:
        db.session.delete(booking)
        db.session.commit()
        flash('Anmeldung erfolgreich gelöscht.', 'success')
        return redirect(url_for('main.view_registrations', event_id=booking.event_id))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_booking: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while deleting the booking.', 'error')
        return redirect(url_for('main.view_registrations', event_id=booking.event_id))

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        flash('You do not have permission to delete events.', 'error')
        return redirect(url_for('main.index'))
    
    event = Event.query.get_or_404(event_id)
    try:
        # Delete associated bookings first
        Booking.query.filter_by(event_id=event_id).delete()
        
        # Delete the event
        db.session.delete(event)
        db.session.commit()
        
        flash('Event successfully deleted.', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_event: {str(e)}\n{traceback.format_exc()}")
        flash('An error occurred while deleting the event.', 'error')
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
        current_app.logger.error(f"Error in health_check: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503
