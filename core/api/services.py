import typing

from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Base
from core.database.models import User

M = typing.TypeVar("M", bound=Base)
S = typing.TypeVar("S", bound=BaseModel)
C = typing.TypeVar("C", bound=BaseModel)


class CRUDService:
    model: typing.Type[M]
    schema_class: typing.Type[S]
    create_schema_class: typing.Type[C]

    def get_entities_default_query(self) -> Select:
        raise NotImplementedError

    async def get_entities_list(self, session: AsyncSession) -> list[S]:
        entites = await session.scalars(self.get_entities_default_query())
        return [self.schema_class.model_validate(entity).model_dump() for entity in entites]

    async def create_entity(self, create_entity: C, session: AsyncSession, user: User) -> S:
        entity = self.model(**create_entity.model_dump())
        entity = self.before_entity_create(entity, session, user)
        session.add(entity)
        await session.commit()
        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        book = await session.scalar(stmt)
        return self.schema_class.model_validate(book).model_dump()

    def before_entity_create(self, entity: M, session: AsyncSession, user: User) -> M:
        return entity
