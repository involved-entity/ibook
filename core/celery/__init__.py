from celery import Celery

from core.celery.send_email import send_email
from core.config import settings

celery = Celery(
    "ibook-tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    broker_connection_retry_on_startup=True,
)


@celery.task
def send_email_task(email_to: str, subject: str, html_content: str) -> None:
    send_email(email_to, subject, html_content)
