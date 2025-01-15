from flask_mail import Mail, Message
from flask import current_app
from datetime import datetime

mail = Mail()

def send_email(subject, recipients, body, html=None):
    """
    Send an email using Flask-Mail
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        body (str): Plain text email body
        html (str, optional): HTML version of the email body
    """
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        html=html
    )
    mail.send(msg)

def send_password_reset_email(user, token):
    """
    Send a password reset email to the user
    
    Args:
        user: User object containing email
        token: Password reset token
    """
    reset_url = f"{current_app.config['BASE_URL']}/reset-password/{token}"
    subject = "Password Reset Request"
    body = f"""To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
"""
    html = f"""
    <p>To reset your password, click the following link:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not make this request, please ignore this email.</p>
    """
    send_email(subject, [user.email], body, html)

def send_event_registration_confirmation(user_email, event):
    """
    Send a confirmation email to the user who registered for an event
    
    Args:
        user_email (str): Email address of the registered user
        event (Event): Event object containing event details
    """
    subject = f"Registration Confirmation - {event.title}"
    body = f"""
Thank you for registering for {event.title}!

Event Details:
- Date: {event.date.strftime('%B %d, %Y')}
- Time: {event.date.strftime('%I:%M %p')}
- Location: {event.room or 'TBA'}
- Address: {event.address or 'TBA'}

We look forward to seeing you there!

Best regards,
The Event Team
"""
    html = f"""
    <h2>Thank you for registering for {event.title}!</h2>
    
    <h3>Event Details:</h3>
    <ul>
        <li><strong>Date:</strong> {event.date.strftime('%B %d, %Y')}</li>
        <li><strong>Time:</strong> {event.date.strftime('%I:%M %p')}</li>
        <li><strong>Location:</strong> {event.room or 'TBA'}</li>
        <li><strong>Address:</strong> {event.address or 'TBA'}</li>
    </ul>
    
    <p>We look forward to seeing you there!</p>
    
    <p>Best regards,<br>
    The Event Team</p>
    """
    send_email(subject, [user_email], body, html)

def send_admin_registration_notification(event, user):
    """
    Send a notification email to admin when a user registers for an event
    
    Args:
        event (Event): Event object containing event details
        user (User): User object containing user details
    """
    admin_email = current_app.config['ADMIN_EMAIL']
    if not admin_email:
        return
        
    subject = f"New Event Registration - {event.title}"
    body = f"""
New registration for {event.title}

User Details:
- Name: {user.name}
- Email: {user.email}

Event Details:
- Date: {event.date.strftime('%B %d, %Y')}
- Time: {event.time.strftime('%I:%M %p')}
- Location: {event.location}

Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    html = f"""
    <h2>New registration for {event.title}</h2>
    
    <h3>User Details:</h3>
    <ul>
        <li><strong>Name:</strong> {user.name}</li>
        <li><strong>Email:</strong> {user.email}</li>
    </ul>
    
    <h3>Event Details:</h3>
    <ul>
        <li><strong>Date:</strong> {event.date.strftime('%B %d, %Y')}</li>
        <li><strong>Time:</strong> {event.time.strftime('%I:%M %p')}</li>
        <li><strong>Location:</strong> {event.location}</li>
    </ul>
    
    <p><strong>Registration Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """
    send_email(subject, [admin_email], body, html)
