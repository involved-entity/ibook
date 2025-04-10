from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from core.api.authentication.dependencies import get_access_token_db
from core.config import settings
from core.database.models import Token


def get_database_strategy(
    access_token_db: AccessTokenDatabase[Token] = Depends(get_access_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=settings.access_token_lifetime)
