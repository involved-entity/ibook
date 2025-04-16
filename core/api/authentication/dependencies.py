from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.authentication.user_manager import UserManager
from core.database import get_session
from core.database.models import Token, User


async def get_access_token_db(session: AsyncSession = Depends(get_session)):
    yield Token.get_db(session)


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield User.get_db(session)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
