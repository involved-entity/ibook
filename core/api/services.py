import typing

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Select, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.schemas import ListPaginatedResponse
from core.config import settings
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
    list_owner_only: bool = False
    retrieve_owner_only: bool = False
    use_custom_remove: bool = False

    list_pagination: bool = True
    commit_before_after_create_hook: bool = True

    create_model_dump_exclude: set[str] | None = None

    permission_denied_error: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )
    not_found_error: HTTPException = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    create_entity_error: HTTPException = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    def get_entities_default_query(self, query: typing.Optional[dict] = None) -> Select:
        return select(self.model).order_by(self.model.id.desc())

    async def get_entity_retrieve(self, query: Select, session: AsyncSession) -> M:
        result = await session.execute(query)
        entity = result.scalar_one_or_none()
        if not entity:
            raise self.not_found_error

        return entity

    async def get_entities_list(
        self, session: AsyncSession, query: dict, user: typing.Optional[User] = None
    ) -> dict[str, typing.Any]:
        if self.list_owner_only:
            stmt = (
                self.get_entities_default_query(query).where(getattr(self.model, self.user_field) == user.id)  # noqa
            )
        else:
            stmt = self.get_entities_default_query(query)

        if self.list_pagination and query.get("page") and query["page"].isnumeric():
            stmt = stmt.offset((int(query["page"]) - 1) * settings.pagination_page_size).limit(
                settings.pagination_page_size
            )

        total = await session.scalar(func.count(self.model.id))
        entities = await session.scalars(stmt)
        pages = (
            (total + settings.pagination_page_size - 1) // settings.pagination_page_size
            if self.list_pagination
            else None
        )

        return ListPaginatedResponse[self.schema_class](
            items=[self.schema_class.model_validate(entity) for entity in entities], total=total, pages=pages
        ).model_dump()

    async def retrieve_entity(self, entity_id: int, session: AsyncSession, user: User) -> S:
        entity = await self.get_entity_retrieve(
            self.get_entities_default_query().filter(self.model.id == entity_id), session
        )
        entity = self.check_permissions_to_retrieve_entity(entity, user)

        return self.schema_class.model_validate(entity).model_dump()

    def check_permissions_to_retrieve_entity(self, entity: M, user: User) -> M:
        if self.retrieve_owner_only and user not in (UserRole.ADMIN,) and user.id != getattr(entity, self.user_field):
            raise self.permission_denied_error

        return entity

    async def create_entity(self, create_entity_data: C, session: AsyncSession, user: User) -> S:
        entity = self.model(**create_entity_data.model_dump(exclude=self.create_model_dump_exclude))
        entity = await self.before_entity_create(entity, create_entity_data, user, session)
        session.add(entity)

        if self.commit_before_after_create_hook:
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise self.create_entity_error

        entity = await self.after_entity_create(entity, create_entity_data, user, session)
        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        entity = await session.scalar(stmt)
        return self.schema_class.model_validate(entity).model_dump()

    async def update_entity(self, entity_id: int, update_entity_data: U, session: AsyncSession, user: User) -> S:
        entity = await self.get_entity_retrieve(select(self.model).filter(self.model.id == entity_id), session)

        entity = await self.check_permissions_to_edit_entity(entity, user, session)
        entity = await self.before_entity_update(entity, update_entity_data, user, session)

        update_values = update_entity_data.model_dump(exclude_unset=True, exclude_none=True)

        if update_values:
            await session.execute(update(self.model).where(self.model.id == entity_id).values(**update_values))
            await session.commit()

        stmt = self.get_entities_default_query().where(self.model.id == entity.id)
        entity = await session.scalar(stmt)

        return self.schema_class.model_validate(entity).model_dump()

    async def remove_entity(self, entity_id: int, session: AsyncSession, user: User) -> None:
        entity = await session.get(self.model, entity_id)
        if not entity:
            raise self.not_found_error

        entity = await self.check_permissions_to_edit_entity(entity, user, session)

        if self.use_custom_remove:
            return await self.custom_remove(entity, session)

        await session.delete(entity)
        await session.commit()

    async def check_permissions_to_edit_entity(self, entity: M, user: User, session: AsyncSession) -> M:  # noqa
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
