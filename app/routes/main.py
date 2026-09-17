from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from ..models.models import Event, Booking, db
from datetime import datetime, timezone
from sqlalchemy import text
from ..utils.email import send_event_registration_confirmation, send_admin_registration_notification
from ..utils.utils import log_db_error
import traceback
import io
from openpyxl import Workbook

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
            
            flash('Veranstaltung erfolgreich erstellt!', 'success')
            return redirect(url_for('main.index'))
        except ValueError as e:
            db.session.rollback()
            log_db_error("Fehler bei der Erstellung der Veranstaltung", e)
            flash(str(e), 'danger')
            return render_template('create_event.html',
                                default_date=date_str,
                                form_data=request.form)
        except Exception as e:
            db.session.rollback()
            log_db_error("Fehler bei der Erstellung der Veranstaltung", e)
            flash('Ein Fehler ist aufgetreten, während die Veranstaltung erstellt wurde.', 'danger')
            return render_template('create_event.html', 
                                default_date=date_str,
                                form_data=request.form)
    
    default_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M')
    return render_template('create_event.html', default_date=default_date)

@bp.route('/event/<int:event_id>/book', methods=['GET', 'POST'])
def book_event(event_id):
    """Book an event."""
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        booking = Booking(event_id=event_id, name=name, email=email, phone=phone)

        try:
            # Atomically claim a spot: only increments if a free spot is still
            # available, so concurrent bookings can't oversell the event.
            result = db.session.execute(
                text('UPDATE event SET bookings = bookings + 1 WHERE id = :id AND bookings < capacity'),
                {'id': event_id}
            )
            if result.rowcount == 0:
                db.session.rollback()
                flash('Diese Veranstaltung ist leider ausgebucht!', 'error')
                return redirect(url_for('main.index'))

            db.session.add(booking)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            log_db_error("Fehler bei der Buchung", e)
            flash('Bei der Verarbeitung Ihrer Buchung ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut.', 'error')
            return redirect(url_for('main.book_event', event_id=event_id))

        # Booking is committed. Emails are a best-effort notification and must
        # not hold the DB transaction or a worker slot open on a slow/hanging
        # mail API call (this was blocking new bookings under load).
        try:
            send_event_registration_confirmation(email, event)
            user_data = {'name': name, 'email': email, 'phone': phone}
            send_admin_registration_notification(event, user_data)
        except Exception as e:
            current_app.logger.error(f"Buchung gespeichert, aber Versand der Bestätigungs-E-Mail fehlgeschlagen: {str(e)}\n{traceback.format_exc()}")

        return redirect(url_for('main.book_event', event_id=event_id, success='true'))

    return render_template('book_event.html', event=event)

@bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    # Use get() instead of get_or_404() for better performance
    event = Event.query.get(event_id)
    if not event:
        flash('Veranstaltung nicht gefunden.', 'danger')
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
            
            flash('Veranstaltung erfolgreich aktualisiert!', 'success')
            return redirect(url_for('main.index'))
            
        except ValueError as e:
            db.session.rollback()
            log_db_error("Fehler bei der Aktualisierung der Veranstaltung", e)
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback()
            log_db_error("Fehler bei der Aktualisierung der Veranstaltung", e)
            flash('Ein Fehler ist aufgetreten, während die Veranstaltung aktualisiert wurde.', 'danger')
    
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
            title=f"Kopie von {original_event.title}",
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
        
        flash('Veranstaltung erfolgreich kopiert!', 'success')
        return redirect(url_for('main.index'))
    except ValueError as e:
        db.session.rollback()
        log_db_error("Fehler bei der Kopie der Veranstaltung", e)
        flash(str(e), 'danger')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        log_db_error("Fehler bei der Kopie der Veranstaltung", e)
        flash('Ein Fehler ist aufgetreten, während die Veranstaltung kopiert wurde.', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/event/<int:event_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_visibility(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        event.is_visible = not event.is_visible
        db.session.commit()
        status = "sichtbar" if event.is_visible else "unsichtbar"
        flash(f'Veranstaltung ist jetzt {status}', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        log_db_error("Fehler bei der Aktualisierung der Sichtbarkeit der Veranstaltung", e)
        flash('Fehler bei der Aktualisierung der Sichtbarkeit der Veranstaltung', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/event/<int:event_id>/registrations')
@login_required
def view_registrations(event_id):
    event = Event.query.get_or_404(event_id)
    bookings = Booking.query.filter_by(event_id=event_id).order_by(Booking.created_at.desc()).all()
    return render_template('registrations.html', event=event, bookings=bookings)

@bp.route('/event/<int:event_id>/export')
@login_required
def export_registrations(event_id):
    """Export event registrations as Excel file."""
    # Ensure user is admin
    if not current_user.is_admin:
        flash('Zugriff verweigert. Sie benötigen Administratorrechte.', 'danger')
        return redirect(url_for('main.index'))
    
    event = Event.query.get_or_404(event_id)
    bookings = Booking.query.filter_by(event_id=event_id).order_by(Booking.created_at.desc()).all()
    
    # Create a workbook and select the active worksheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Registrierungen"
    
    # Add headers
    headers = ["Name", "Telefonnummer", "E-Mail"]
    for col_num, header in enumerate(headers, 1):
        worksheet.cell(row=1, column=col_num, value=header)
    
    # Add data
    for row_num, booking in enumerate(bookings, 2):
        worksheet.cell(row=row_num, column=1, value=booking.name)
        worksheet.cell(row=row_num, column=2, value=booking.phone)
        worksheet.cell(row=row_num, column=3, value=booking.email)
    
    # Create a BytesIO object to store the Excel file
    excel_file = io.BytesIO()
    workbook.save(excel_file)
    excel_file.seek(0)
    
    # Generate a filename with the event date in YYYY-MM-DD format
    event_date_str = event.date.strftime('%Y-%m-%d')
    filename = f"{event_date_str}-Anmeldungen.xlsx"
    
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

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
        log_db_error("Fehler bei der Löschung der Anmeldung", e)
        flash('Ein Fehler ist aufgetreten, während die Anmeldung gelöscht wurde.', 'error')
        return redirect(url_for('main.view_registrations', event_id=booking.event_id))

@bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        flash('Sie haben keine Berechtigung, Veranstaltungen zu löschen.', 'error')
        return redirect(url_for('main.index'))
    
    event = Event.query.get_or_404(event_id)
    try:
        # Delete associated bookings first
        Booking.query.filter_by(event_id=event_id).delete()
        
        # Delete the event
        db.session.delete(event)
        db.session.commit()
        
        flash('Veranstaltung erfolgreich gelöscht.', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        log_db_error("Fehler bei der Löschung der Veranstaltung", e)
        flash('Ein Fehler ist aufgetreten, während die Veranstaltung gelöscht wurde.', 'error')
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
        log_db_error("Fehler bei der Überprüfung der Gesundheit", e)
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503
