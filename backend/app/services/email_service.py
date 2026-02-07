"""Email service for sending transactional emails using SendGrid"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@skillstudio.com")
        self.from_name = os.getenv("FROM_NAME", "SkillStudio")
        
        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        if not self.api_key:
            logger.warning("SendGrid API key not configured. Emails will be logged only.")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send an email via SendGrid"""
        try:
            if not self.api_key:
                logger.info(f"[EMAIL] To: {to_email}, Subject: {subject}")
                logger.info(f"[EMAIL] Content: {plain_content or html_content[:100]}...")
                return True
            
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if plain_content:
                message.plain_text_content = Content("text/plain", plain_content)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    message.add_attachment(attachment)
            
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            logger.info(f"Email sent to {to_email}: {response.status_code}")
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        template = self.jinja_env.get_template("welcome.html")
        html_content = template.render(
            user_name=user_name,
            platform_name="SkillStudio",
            login_url=f"{settings.FRONTEND_URL}/login",
            dashboard_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        return await self.send_email(
            to_email=user_email,
            subject="Welcome to SkillStudio - Start Your Learning Journey! 🚀",
            html_content=html_content
        )
    
    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        template = self.jinja_env.get_template("password_reset.html")
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_content = template.render(
            user_name=user_name,
            reset_url=reset_url,
            expiry_hours=24
        )
        
        return await self.send_email(
            to_email=user_email,
            subject="Reset Your SkillStudio Password",
            html_content=html_content
        )
    
    async def send_course_completion_email(
        self,
        user_email: str,
        user_name: str,
        course_title: str,
        completion_date: str,
        certificate_url: Optional[str] = None
    ) -> bool:
        """Send course completion congratulations email"""
        template = self.jinja_env.get_template("course_completion.html")
        html_content = template.render(
            user_name=user_name,
            course_title=course_title,
            completion_date=completion_date,
            certificate_url=certificate_url,
            dashboard_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        return await self.send_email(
            to_email=user_email,
            subject=f"🎉 Congratulations! You've completed {course_title}",
            html_content=html_content
        )
    
    async def send_weekly_progress_report(
        self,
        user_email: str,
        user_name: str,
        report_data: Dict[str, Any]
    ) -> bool:
        """Send weekly learning progress report"""
        template = self.jinja_env.get_template("weekly_progress.html")
        html_content = template.render(
            user_name=user_name,
            courses_completed=report_data.get("courses_completed", 0),
            lessons_completed=report_data.get("lessons_completed", 0),
            total_study_time=report_data.get("total_study_time", 0),
            assessments_taken=report_data.get("assessments_taken", 0),
            skill_improvements=report_data.get("skill_improvements", []),
            recommended_courses=report_data.get("recommended_courses", []),
            dashboard_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        return await self.send_email(
            to_email=user_email,
            subject="📊 Your Weekly Learning Progress Report",
            html_content=html_content
        )
    
    async def send_notification_email(
        self,
        user_email: str,
        user_name: str,
        notification_type: str,
        notification_data: Dict[str, Any]
    ) -> bool:
        """Send notification email based on type"""
        template = self.jinja_env.get_template("notification.html")
        html_content = template.render(
            user_name=user_name,
            notification_type=notification_type,
            notification_data=notification_data,
            dashboard_url=f"{settings.FRONTEND_URL}/dashboard"
        )
        
        subject_map = {
            "new_course": "🎓 New Course Available",
            "assignment_due": "⏰ Assignment Due Soon",
            "new_message": "💬 You have a new message",
            "course_update": "📝 Course Update",
            "achievement": "🏆 New Achievement Unlocked"
        }
        
        subject = subject_map.get(notification_type, "New Notification")
        
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )
    
    async def send_enrollment_confirmation(
        self,
        user_email: str,
        user_name: str,
        course_title: str,
        instructor_name: str,
        start_date: Optional[str] = None
    ) -> bool:
        """Send course enrollment confirmation email"""
        template = self.jinja_env.get_template("enrollment_confirmation.html")
        html_content = template.render(
            user_name=user_name,
            course_title=course_title,
            instructor_name=instructor_name,
            start_date=start_date,
            course_url=f"{settings.FRONTEND_URL}/dashboard/my-courses"
        )
        
        return await self.send_email(
            to_email=user_email,
            subject=f"✅ Enrollment Confirmed: {course_title}",
            html_content=html_content
        )
    
    async def send_instructor_payout_notification(
        self,
        instructor_email: str,
        instructor_name: str,
        payout_amount: float,
        payout_date: str,
        transaction_id: str
    ) -> bool:
        """Send payout notification to instructor"""
        template = self.jinja_env.get_template("instructor_payout.html")
        html_content = template.render(
            instructor_name=instructor_name,
            payout_amount=payout_amount,
            payout_date=payout_date,
            transaction_id=transaction_id,
            dashboard_url=f"{settings.FRONTEND_URL}/instructor/earnings"
        )
        
        return await self.send_email(
            to_email=instructor_email,
            subject=f"💰 Payout Processed: ${payout_amount}",
            html_content=html_content
        )


# Global email service instance
email_service = EmailService()
