import os
from typing import Optional
from datetime import datetime
from app.models.resume import EmailStatusEnum

# Microsoft Form link - can be configured via environment variable
DEFAULT_FORM_LINK = os.getenv("MICROSOFT_FORM_LINK", "https://forms.office.com/YourFormLinkHere")

class EmailService:
    """Service for sending screening form emails"""
    
    def __init__(self):
        self.form_link = DEFAULT_FORM_LINK
    
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
        # For now, this is a mock implementation
        # In production, integrate with SMTP/SendGrid/etc.
        
        link = form_link or self.form_link
        
        # Mock email sending - in production, use actual email service
        print(f"[EMAIL SERVICE] Sending screening form to {candidate_email}")
        print(f"[EMAIL SERVICE] Job: {job_title}")
        print(f"[EMAIL SERVICE] Form Link: {link}")
        
        # Simulate email sending
        # In real implementation:
        # - Use aiosmtplib or SendGrid API
        # - Handle errors gracefully
        # - Log email status
        
        return True
    
    def get_form_link(self) -> str:
        """Get the Microsoft Form link"""
        return self.form_link
