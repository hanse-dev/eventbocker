from flask import current_app, render_template
from datetime import datetime
import logging
import os
from mailjet_rest import Client

class EmailService:
    _instance = None

    def __init__(self):
        """Initialize the Mailjet client with API credentials"""
        self.api_key = current_app.config.get('MAILJET_API_KEY') or os.environ.get('MAILJET_API_KEY')
        self.api_secret = current_app.config.get('MAILJET_API_SECRET') or os.environ.get('MAILJET_API_SECRET')
        
        if not self.api_key or not self.api_secret:
            raise ValueError('Mailjet configuration incomplete: MAILJET_API_KEY and MAILJET_API_SECRET are required')
            
        self.client = Client(auth=(self.api_key, self.api_secret), version='v3.1')

    @classmethod
    def get_instance(cls):
        """Get singleton instance of EmailService"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

def send_email(subject, recipients, template_prefix, **template_context):
    """
    Send an email using Mailjet with templates
    
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

    try:
        # Render both text and HTML versions using templates
        txt = render_template(f"email/{template_prefix}.txt", **template_context)
        html = render_template(f"email/{template_prefix}.html", **template_context)
        
        email_service = EmailService.get_instance()
        
        # Prepare recipients for Mailjet format
        recipients_data = [{"Email": email} for email in recipients]
        
        data = {
            "Messages": [{
                "From": {
                    "Email": current_app.config['MAIL_USERNAME'],
                    "Name": current_app.config.get('MAIL_DEFAULT_SENDER', current_app.config['MAIL_USERNAME'])
                },
                "To": recipients_data,
                "Subject": subject,
                "TextPart": txt,
                "HTMLPart": html
            }]
        }
        
        response = email_service.client.send.create(data=data)
        if response.status_code > 299:
            raise Exception(f"Mailjet API error: {response.json()}")
            
        current_app.logger.info(f"Email successfully sent to {', '.join(recipients)}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
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
