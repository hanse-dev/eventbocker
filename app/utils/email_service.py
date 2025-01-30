from typing import List, Dict, Optional, Union
import os
from mailjet_rest import Client

class EmailService:
    def __init__(self):
        """Initialize the Mailjet client with API credentials."""
        api_key = os.environ.get('MAILJET_API_KEY')
        api_secret = os.environ.get('MAILJET_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("Mailjet API credentials not found in environment variables")
        
        self.client = Client(auth=(api_key, api_secret), version='v3.1')

    def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        template_id: Optional[int] = None,
        template_vars: Optional[Dict] = None
    ) -> Dict:
        """
        Send an email using Mailjet API.
        
        Args:
            to_email: Recipient email address or list of addresses
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email address (optional, uses default if not provided)
            from_name: Sender name (optional)
            template_id: Mailjet template ID (optional)
            template_vars: Variables for template (optional)
            
        Returns:
            Dict containing API response
        """
        if isinstance(to_email, str):
            to_email = [to_email]

        # Prepare recipients
        recipients = [{"Email": email} for email in to_email]

        # Base email data
        data = {
            "Messages": [{
                "To": recipients,
                "Subject": subject,
                "HTMLPart": html_content,
            }]
        }

        # Add sender information if provided
        if from_email:
            data["Messages"][0]["From"] = {
                "Email": from_email,
                "Name": from_name or from_email
            }

        # Add template if provided
        if template_id:
            data["Messages"][0]["TemplateID"] = template_id
            if template_vars:
                data["Messages"][0]["Variables"] = template_vars

        try:
            response = self.client.send.create(data=data)
            return response.json()
        except Exception as e:
            # Log the error and re-raise
            print(f"Error sending email: {str(e)}")
            raise

    def create_contact(self, email: str, name: Optional[str] = None) -> Dict:
        """
        Add a contact to Mailjet contact list.
        
        Args:
            email: Contact email address
            name: Contact name (optional)
            
        Returns:
            Dict containing API response
        """
        data = {
            "Email": email
        }
        if name:
            data["Name"] = name

        try:
            response = self.client.contact.create(data=data)
            return response.json()
        except Exception as e:
            print(f"Error creating contact: {str(e)}")
            raise
