import typing

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Base, User
from core.database.models.user import UserRole

M = typing.TypeVar("M", bound=Base)
S = typing.TypeVar("S", bound=BaseModel)
C = typing.TypeVar("C", bound=BaseModel)


class CRUDService:
    model: typing.Type[M]
    schema_class: typing.Type[S]
    create_schema_class: typing.Type[C]

    user_field: str = ""

    admin_or_owner_remove: bool = False
    save_user_id_before_create: bool = False
    binded_to_user: bool = False

    permission_denied_error: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )

    def get_entities_default_query(self) -> Select:
        return select(self.model).order_by(self.model.id)

    async def get_entities_list(self, session: AsyncSession, user: typing.Optional[User] = None) -> list[S]:
        if self.binded_to_user:
            entities = await session.scalars(
                self.get_entities_default_query().where(getattr(self.model, self.user_field) == user.id)  # noqa
            )
        else:
            entities = await session.scalars(self.get_entities_default_query())

        return [self.schema_class.model_validate(entity).model_dump() for entity in entities]

    async def create_entity(self, create_entity: C, session: AsyncSession, user: User) -> S:
        entity = self.model(**create_entity.model_dump())
        entity = self.before_entity_create(entity, user)
        session.add(entity)
        await session.commit()
        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        book = await session.scalar(stmt)
        return self.schema_class.model_validate(book).model_dump()

    async def remove_entity(self, entity_id: int, session: AsyncSession, user: User) -> None:
        entity = await session.get(self.model, entity_id)

        if self.binded_to_user and not (user.role == UserRole.ADMIN or getattr(entity, self.user_field) == user.id):
            raise self.permission_denied_error

        entity = self.check_permissions_to_remove_entity(entity, user)
        await session.delete(entity)
        await session.commit()

    def check_permissions_to_remove_entity(self, entity: M, user: User) -> M:  # noqa
        if self.admin_or_owner_remove and not (
            user.role == UserRole.ADMIN or user.id == getattr(entity, self.user_field)
        ):
            raise self.permission_denied_error

        return entity

    def before_entity_create(self, entity: M, user: User) -> M:
        if self.save_user_id_before_create:
            setattr(entity, self.user_field, user.id)

        return entity
