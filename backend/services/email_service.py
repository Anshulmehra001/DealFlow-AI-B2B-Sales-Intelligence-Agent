"""
Email service for sending automated emails
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
import logging
from datetime import datetime, date

from backend.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via Gmail SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.daily_sent_count = 0
        self.last_reset_date = date.today()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within daily email limit"""
        # Reset counter if it's a new day
        if date.today() != self.last_reset_date:
            self.daily_sent_count = 0
            self.last_reset_date = date.today()
        
        if self.daily_sent_count >= settings.EMAIL_DAILY_LIMIT:
            logger.warning(f"Daily email limit reached: {settings.EMAIL_DAILY_LIMIT}")
            return False
        return True
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send an email"""
        
        if not settings.ENABLE_EMAIL_SENDING:
            logger.info(f"Email sending disabled. Would send to: {to_email}")
            return True
        
        if not self._check_rate_limit():
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Add body
            if body_text:
                part1 = MIMEText(body_text, "plain")
                message.attach(part1)
            
            part2 = MIMEText(body_html, "html")
            message.attach(part2)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=True
            )
            
            self.daily_sent_count += 1
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject_template: str,
        body_template: str
    ) -> Dict[str, int]:
        """Send bulk personalized emails"""
        results = {"sent": 0, "failed": 0}
        
        for recipient in recipients:
            # Personalize subject and body
            subject = subject_template.format(**recipient)
            body = body_template.format(**recipient)
            
            success = await self.send_email(
                to_email=recipient["email"],
                subject=subject,
                body_html=body
            )
            
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def generate_initial_outreach_email(
        self,
        company_name: str,
        contact_name: str,
        pain_points: List[str]
    ) -> Dict[str, str]:
        """Generate initial outreach email"""
        
        subject = f"Quick question about {company_name}'s sales process"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {contact_name},</p>
            
            <p>I noticed that {company_name} is growing rapidly, and I wanted to reach out.</p>
            
            <p>Many companies at your stage struggle with:</p>
            <ul>
                {"".join([f"<li>{point}</li>" for point in pain_points])}
            </ul>
            
            <p>We've helped similar B2B companies increase their sales efficiency by 40% using AI-powered automation.</p>
            
            <p>Would you be open to a quick 15-minute call next week to explore if this could help {company_name}?</p>
            
            <p>Best regards,<br>
            {self.from_name}</p>
            
            <p style="font-size: 12px; color: #666;">
                P.S. If this isn't relevant, just let me know and I won't follow up.
            </p>
        </body>
        </html>
        """
        
        return {"subject": subject, "body_html": body_html}
    
    def generate_follow_up_email(
        self,
        company_name: str,
        contact_name: str,
        previous_context: str
    ) -> Dict[str, str]:
        """Generate follow-up email"""
        
        subject = f"Following up - {company_name}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {contact_name},</p>
            
            <p>I wanted to follow up on my previous email about helping {company_name} improve sales efficiency.</p>
            
            <p>{previous_context}</p>
            
            <p>I have a few time slots available this week:</p>
            <ul>
                <li>Tuesday at 2 PM</li>
                <li>Wednesday at 10 AM</li>
                <li>Thursday at 3 PM</li>
            </ul>
            
            <p>Would any of these work for a quick call?</p>
            
            <p>Best regards,<br>
            {self.from_name}</p>
        </body>
        </html>
        """
        
        return {"subject": subject, "body_html": body_html}
    
    def generate_proposal_email(
        self,
        company_name: str,
        contact_name: str,
        deal_value: float,
        key_benefits: List[str]
    ) -> Dict[str, str]:
        """Generate proposal email"""
        
        subject = f"Proposal for {company_name} - ${deal_value:,.0f}"
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Hi {contact_name},</p>
            
            <p>Thank you for the great conversation! As discussed, here's our proposal for {company_name}.</p>
            
            <h3>Key Benefits:</h3>
            <ul>
                {"".join([f"<li>{benefit}</li>" for benefit in key_benefits])}
            </ul>
            
            <h3>Investment:</h3>
            <p><strong>${deal_value:,.0f}</strong> annually</p>
            
            <p>This includes:</p>
            <ul>
                <li>Full platform access</li>
                <li>Dedicated account manager</li>
                <li>24/7 support</li>
                <li>Quarterly business reviews</li>
            </ul>
            
            <p>I'm confident this will deliver significant ROI for {company_name}. Let's schedule a call to discuss next steps.</p>
            
            <p>Best regards,<br>
            {self.from_name}</p>
        </body>
        </html>
        """
        
        return {"subject": subject, "body_html": body_html}


# Global email service instance
email_service = EmailService()
