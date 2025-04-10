import logging
from typing import Optional

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from core.config import settings
from core.database.models import User

logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    verification_token_secret = settings.verification_token_secret
    reset_password_token_secret = settings.reset_password_token_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.warning("User %r has registered.", user.id)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        logger.warning("User %r has forgot their password. Reset token: %r", user.id, token)

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logger.warning("Verification requested for user %r. Verification token: %r", user.id, token)
