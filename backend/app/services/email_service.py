import os
from typing import Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.models.resume import EmailStatusEnum

# Microsoft Form link - can be configured via environment variable
DEFAULT_FORM_LINK = os.getenv("MICROSOFT_FORM_LINK", "https://forms.office.com/YourFormLinkHere")

class EmailService:
    """Service for sending screening form emails"""

    def __init__(self):
        self.form_link = DEFAULT_FORM_LINK
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)

    async def send_screening_form(
        self,
        candidate_email: str,
        job_title: str,
        form_link: Optional[str] = None
    ) -> bool:
        """
        Send screening form email to candidate

        Args:
            candidate_email: Candidate email address
            job_title: Job title
            form_link: Optional custom form link

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Check if SMTP credentials are configured
            if not self.smtp_username or not self.smtp_password:
                print("[EMAIL SERVICE] ERROR: SMTP credentials not configured")
                print("[EMAIL SERVICE] Please set SMTP_USERNAME and SMTP_PASSWORD environment variables")
                return False

            link = form_link or self.form_link

            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = candidate_email
            message["Subject"] = f"Screening Form for {job_title} Position"

            # Email body
            body = f"""
Dear Candidate,

Thank you for your interest in the {job_title} position.

Please complete our screening form to proceed with your application:

{link}

Best regards,
Recruitment Team
"""

            message.attach(MIMEText(body, "plain"))

            # Determine SSL/TLS based on port
            use_ssl = self.smtp_port == 465
            use_tls = self.smtp_port == 587
            connection_type = "SSL" if use_ssl else "TLS" if use_tls else "Unknown"

            print(f"[EMAIL SERVICE] Sending screening form to {candidate_email}")
            print(f"[EMAIL SERVICE] Job: {job_title}")
            print(f"[EMAIL SERVICE] Form Link: {link}")
            print(f"[EMAIL SERVICE] SMTP Server: {self.smtp_server}:{self.smtp_port} ({connection_type})")

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=587,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
            )


            print("[EMAIL SERVICE] Email sent successfully")
            return True

        except Exception as e:
            print(f"[EMAIL SERVICE] ERROR: Failed to send email: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_form_link(self) -> str:
        """Get the Microsoft Form link"""
        return self.form_link
 