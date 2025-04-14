import logging
from pathlib import Path
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from jinja2 import Environment, FileSystemLoader

from core.celery import send_email_task
from core.config import settings
from core.database.models import User

logger = logging.getLogger(__name__)

templates_path = Path(__file__).parent.parent.parent / "celery" / "email_templates"
env = Environment(loader=FileSystemLoader(templates_path), autoescape=True)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    verification_token_secret = settings.verification_token_secret
    reset_password_token_secret = settings.reset_password_token_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.warning("User %r has registered.", user.id)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        template = env.get_template(settings.jinja_password_reset_template)
        html_content = template.render(
            user=user, token=token, reset_url=f"{settings.frontend_url}/reset-password?token={token}"
        )

        send_email_task.delay(email_to=user.email, subject="Password Reset", html_content=html_content)

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        template = env.get_template(settings.jinja_password_verify_template)
        html_content = template.render(
            user=user, token=token, verify_url=f"{settings.frontend_url}/verify-email?token={token}"
        )

        send_email_task.delay(email_to=user.email, subject="Verify Your Email", html_content=html_content)
