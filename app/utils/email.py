from flask_mail import Mail, Message
from flask import current_app, render_template
from datetime import datetime
import logging

mail = Mail()

def init_mail(app):
    """Initialize mail with app configuration"""
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        app.logger.warning('E-Mail-Konfiguration unvollständig: MAIL_USERNAME oder MAIL_PASSWORD fehlt')
    mail.init_app(app)

def send_email(subject, recipients, template_prefix, **template_context):
    """
    Send an email using Flask-Mail with templates
    
    Args:
        subject (str): Email subject
        recipients (list): List of recipient email addresses
        template_prefix (str): Prefix for the template files (e.g., 'registration_confirmation')
        **template_context: Context variables for the template
    """
    # Check if emails are disabled
    if current_app.config.get('DISABLE_EMAILS', False):
        current_app.logger.info(f"Emails disabled. Would have sent email '{subject}' to {', '.join(recipients)}")
        return
        
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        current_app.logger.error("E-Mail-Konfiguration unvollständig: MAIL_USERNAME oder MAIL_PASSWORD fehlt")
        raise ValueError("E-Mail-Konfiguration unvollständig: MAIL_USERNAME oder MAIL_PASSWORD fehlt")
        
    try:
        # Render both text and HTML versions using templates
        txt = render_template(f"email/{template_prefix}.txt", **template_context)
        html = render_template(f"email/{template_prefix}.html", **template_context)
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=txt,
            html=html,
            sender=current_app.config['MAIL_USERNAME']
        )
        mail.send(msg)
        current_app.logger.info(f"E-Mail erfolgreich gesendet an {', '.join(recipients)}")
    except Exception as e:
        current_app.logger.error(f"E-Mail konnte nicht gesendet werden: {str(e)}")
        raise

def send_password_reset_email(user, token):
    """
    Send a password reset email to the user
    
    Args:
        user: User object containing email
        token: Password reset token
    """
    reset_url = f"{current_app.config['BASE_URL']}/reset-password/{token}"
    subject = "Passwort zurücksetzen"
    send_email(
        subject=subject,
        recipients=[user.email],
        template_prefix='password_reset',
        reset_url=reset_url
    )

def send_event_registration_confirmation(user_email, event):
    """
    Send a confirmation email to the user who registered for an event
    
    Args:
        user_email (str): Email address of the registered user
        event (Event): Event object containing event details
    """
    subject = f"Anmeldebestätigung - {event.title}"
    send_email(
        subject=subject,
        recipients=[user_email],
        template_prefix='registration_confirmation',
        event=event
    )

def send_admin_registration_notification(event, user):
    """
    Send a notification email to admin when a user registers for an event
    
    Args:
        event (Event): Event object containing event details
        user (dict): Dictionary containing user details (name, email, phone)
    """
    admin_email = current_app.config.get('ADMIN_EMAIL')
    if not admin_email:
        current_app.logger.warning('Admin-E-Mail nicht konfiguriert. Admin-Benachrichtigung wird übersprungen.')
        return
        
    subject = f"Neue Anmeldung - {event.title}"
    send_email(
        subject=subject,
        recipients=[admin_email],
        template_prefix='admin_notification',
        event=event,
        user=user
    )
