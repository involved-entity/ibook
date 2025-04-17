from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

if settings.testing:
    engine = create_async_engine(settings.test_database_url, echo=settings.debug)
else:
    engine = create_async_engine(settings.database_url, echo=settings.debug)

session = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with session() as s:
        yield s
