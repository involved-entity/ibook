from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.addresses.schemas import AddressCreateSchema, AddressSchema, AddressUpdateSchema
from core.api.services import C, CRUDService, M, U
from core.database.models import Address, User


class AddressesCRUDService(CRUDService):
    model = Address
    schema_class = AddressSchema
    create_schema_class = AddressCreateSchema
    update_schema_class = AddressUpdateSchema

    user_field = "user_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True
    list_owner_only = True
    retrieve_owner_only = True

    async def _check_primary_field_constraint(self, schema: C | U, user: User, session: AsyncSession) -> None:  # noqa
        if schema.is_primary:
            stmt = select(Address).where(Address.user_id == user.id, Address.is_primary == True)
            primary = await session.scalar(stmt)

            if primary:
                primary.is_primary = False
                session.add(primary)

    async def before_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        entity = await super().before_entity_create(entity, create_entity, user, session)
        await self._check_primary_field_constraint(create_entity, user, session)
        return entity

    async def before_entity_update(self, entity: M, update_entity: U, user: User, session: AsyncSession) -> M:
        await self._check_primary_field_constraint(update_entity, user, session)
        return entity
