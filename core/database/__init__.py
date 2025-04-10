from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


@asynccontextmanager
async def get_session_manager() -> AsyncGenerator[AsyncSession]:
    async with session() as s:
        yield s


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session() as s:
        yield s
