"""
Scheduler module for handling scheduled tasks like sending reminder emails.
"""
from flask import current_app
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine
import pytz
import logging

from ..models.models import Event, Booking, db
from .email import send_event_reminder

# Configure logger
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None

def init_scheduler(app):
    """
    Initialize the scheduler with the Flask app context.
    
    Args:
        app: Flask application instance
    """
    global scheduler
    
    if scheduler is not None:
        logger.info("Scheduler already initialized")
        return scheduler
    
    logger.info("Initializing scheduler")
    
    # Create jobstore using the same database as the application
    jobstore_url = app.config.get('DATABASE_URL')
    jobstore = SQLAlchemyJobStore(url=jobstore_url)
    
    # Create scheduler with SQLAlchemy jobstore
    scheduler = BackgroundScheduler(
        jobstores={'default': jobstore},
        timezone=pytz.timezone('Europe/Berlin')  # Set to local timezone
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Schedule daily check for events that need reminders
    scheduler.add_job(
        func=schedule_event_reminders,
        trigger=CronTrigger(hour=0, minute=0),  # Run daily at midnight
        id='daily_reminder_check',
        replace_existing=True,
        args=[app]
    )
    
    # Run once at startup to schedule any pending reminders
    with app.app_context():
        schedule_event_reminders(app)
    
    return scheduler

def schedule_event_reminders(app):
    """
    Check for upcoming events and schedule reminder emails.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        # Check if reminders are enabled
        if not current_app.config.get('ENABLE_REMINDERS', True):
            logger.info("Reminders are disabled. Skipping reminder scheduling.")
            return
            
        logger.info("Checking for events that need reminders")
        
        # Get events happening in the next 2 days
        now = datetime.now(pytz.timezone('Europe/Berlin'))
        two_days_from_now = now + timedelta(days=2)
        
        upcoming_events = Event.query.filter(
            Event.date > now,
            Event.date <= two_days_from_now
        ).all()
        
        for event in upcoming_events:
            # Calculate when the reminder should be sent (1 day before at 6 PM)
            reminder_time = event.date.replace(hour=18, minute=0, second=0) - timedelta(days=1)
            
            # Skip if reminder time is in the past
            if reminder_time <= now:
                continue
            
            # Get all bookings for this event
            bookings = Booking.query.filter_by(event_id=event.id).all()
            
            for booking in bookings:
                # Create a unique job ID for each reminder
                job_id = f"reminder_event_{event.id}_booking_{booking.id}"
                
                # Check if job already exists
                if scheduler.get_job(job_id):
                    logger.info(f"Reminder already scheduled for booking {booking.id} of event {event.id}")
                    continue
                
                # Schedule the reminder
                scheduler.add_job(
                    func=send_reminder_email,
                    trigger=DateTrigger(run_date=reminder_time),
                    id=job_id,
                    replace_existing=True,
                    args=[app, booking.email, event.id]
                )
                
                logger.info(f"Scheduled reminder for booking {booking.id} of event {event.id} at {reminder_time}")

def send_reminder_email(app, email, event_id):
    """
    Send a reminder email for an event.
    
    Args:
        app: Flask application instance
        email: Recipient email address
        event_id: ID of the event
    """
    with app.app_context():
        # Check if reminders are still enabled
        if not current_app.config.get('ENABLE_REMINDERS', True):
            logger.info(f"Reminders are disabled. Skipping reminder for event {event_id} to {email}")
            return
            
        try:
            event = Event.query.get(event_id)
            if not event:
                logger.error(f"Event {event_id} not found when sending reminder")
                return
            
            logger.info(f"Sending reminder email for event {event.title} to {email}")
            send_event_reminder(email, event)
            logger.info(f"Reminder email sent successfully to {email} for event {event.title}")
        except Exception as e:
            logger.error(f"Error sending reminder email: {str(e)}")

def get_scheduler_status():
    """
    Get the status of the scheduler.
    
    Returns:
        dict: Status information about the scheduler
    """
    if scheduler is None:
        return {
            'status': 'not_initialized',
            'enabled': False,
            'jobs': 0
        }
    
    return {
        'status': 'running' if scheduler.running else 'stopped',
        'enabled': current_app.config.get('ENABLE_REMINDERS', True),
        'jobs': len(scheduler.get_jobs())
    }
