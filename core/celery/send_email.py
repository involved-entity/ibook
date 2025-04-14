import logging
import smtplib
from email.message import EmailMessage

from core.config import settings

logger = logging.getLogger(__name__)


def send_email(email_to: str, subject: str, html_content: str, from_email: str = None) -> None:
    if from_email is None:
        from_email = settings.smtp_from_email

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = email_to
    message["Subject"] = subject
    message.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_tls:
                server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {email_to}: {e}")
        raise e
