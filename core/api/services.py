import typing

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Base, User
from core.database.models.user import UserRole

M = typing.TypeVar("M", bound=Base)
S = typing.TypeVar("S", bound=BaseModel)
C = typing.TypeVar("C", bound=BaseModel)
U = typing.TypeVar("U", bound=BaseModel)


class CRUDService:
    model: typing.Type[M]
    schema_class: typing.Type[S]
    create_schema_class: typing.Type[C]
    update_schema_class: typing.Type[U]

    user_field: str = ""

    admin_or_owner_to_edit: bool = False
    save_user_id_before_create: bool = False
    list_binded_to_user: bool = False
    use_custom_remove: bool = False

    permission_denied_error: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )
    not_found_error: HTTPException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    create_entity_error: HTTPException = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def get_entities_default_query(self) -> Select:
        return select(self.model).order_by(self.model.id)

    async def get_entities_list(self, session: AsyncSession, user: typing.Optional[User] = None) -> list[S]:
        if self.list_binded_to_user:
            entities = await session.scalars(
                self.get_entities_default_query().where(getattr(self.model, self.user_field) == user.id)  # noqa
            )
        else:
            entities = await session.scalars(self.get_entities_default_query())

        return [self.schema_class.model_validate(entity).model_dump() for entity in entities]

    async def create_entity(self, create_entity_data: C, session: AsyncSession, user: User) -> S:
        entity = self.model(**create_entity_data.model_dump())
        entity = await self.before_entity_create(entity, create_entity_data, user, session)
        session.add(entity)

        try:
            await session.commit()
        except IntegrityError:
            raise self.create_entity_error

        entity = await self.after_entity_create(entity, create_entity_data, user, session)
        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        entity = await session.scalar(stmt)
        return self.schema_class.model_validate(entity).model_dump()

    async def update_entity(self, entity_id: int, update_entity_data: U, session: AsyncSession, user: User) -> S:
        result = await session.execute(select(self.model).filter(self.model.id == entity_id))
        entity = result.scalar_one_or_none()
        if not entity:
            raise self.not_found_error

        entity = self.check_permissions_to_edit_entity(entity, user)
        entity = await self.before_entity_update(entity, update_entity_data, user, session)

        update_values = update_entity_data.model_dump(exclude_unset=True, exclude_none=True)

        await session.execute(update(self.model).where(self.model.id == entity_id).values(**update_values))
        await session.commit()

        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        entity = await session.scalar(stmt)

        return self.schema_class.model_validate(entity).model_dump()

    async def remove_entity(self, entity_id: int, session: AsyncSession, user: User) -> None:
        entity = await session.get(self.model, entity_id)
        if not entity:
            raise self.not_found_error

        entity = self.check_permissions_to_edit_entity(entity, user)

        if self.use_custom_remove:
            return await self.custom_remove(entity, session)

        await session.delete(entity)
        await session.commit()

    def check_permissions_to_edit_entity(self, entity: M, user: User) -> M:  # noqa
        if self.admin_or_owner_to_edit and not (
            user.role == UserRole.ADMIN or user.id == getattr(entity, self.user_field)
        ):
            raise self.permission_denied_error

        return entity

    async def before_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:  # noqa
        if self.save_user_id_before_create:
            setattr(entity, self.user_field, user.id)

        return entity

    async def after_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        return entity

    async def before_entity_update(self, entity: M, update_entity: U, user: User, session: AsyncSession) -> M:  # noqa
        return entity

    async def custom_remove(self, entity: M, session: AsyncSession) -> None:
        raise NotImplementedError()
