import typing

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.api.orders.schemas import OrderCreateSchema, OrderSchema, OrderUpdateSchema
from core.api.services import C, CRUDService, M, U
from core.database.models import Address, Book, Order, OrderItem, User
from core.database.models.order import OrderStatus
from core.database.models.user import UserRole


class OrdersCRUDService(CRUDService):
    model = Order
    schema_class = OrderSchema
    create_schema_class = OrderCreateSchema
    update_schema_class = OrderUpdateSchema

    user_field = "user_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True
    list_owner_only = True
    retrieve_owner_only = True
    use_custom_remove = True

    create_model_dump_exclude = {"items"}

    create_entity_error = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found.")

    def get_entities_default_query(self, query: typing.Optional[dict] = None) -> Select:
        return (
            select(self.model)
            .options(
                joinedload(self.model.address),
                selectinload(self.model.payments),
                selectinload(self.model.items),
            )
            .filter(self.model.status != OrderStatus.CANCELLED)
            .order_by(self.model.id)
        )

    async def _check_address_perms(self, address_id: int, user: User, session: AsyncSession) -> bool:  # noqa
        address = await session.get(Address, address_id)
        return bool(address.user_id == user.id)

    async def before_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        entity = await super().before_entity_create(entity, create_entity, user, session)

        if not await self._check_address_perms(create_entity.address_id, user, session):
            raise self.permission_denied_error

        return entity

    async def after_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        if create_entity.model_dump(include={"items"}).get("items"):
            items = create_entity.model_dump(include={"items"})["items"]
            stmt = select(Book).where(Book.id.in_(item["book_id"] for item in items))
            books = await session.scalars(stmt)
            book_dict = {book.id: book for book in books}

            for order_item in items:
                book = book_dict.get(order_item["book_id"])

                if book:
                    item = OrderItem(
                        order_id=entity.id,  # noqa
                        price=book.price,
                        **order_item,
                    )
                    session.add(item)

            await session.commit()

        return entity

    async def before_entity_update(self, entity: M, update_entity: U, user: User, session: AsyncSession) -> M:
        if update_entity.address_id and not await self._check_address_perms(update_entity.address_id, user, session):
            update_entity.address_id = None

        if update_entity.status:
            if not (
                user.role == UserRole.ADMIN or update_entity.status in (OrderStatus.CREATED, OrderStatus.CANCELLED)
            ):
                update_entity.status = None

        if update_entity.tracking_number:
            if not user.role == UserRole.ADMIN:
                update_entity.tracking_number = None

        return entity

    async def custom_remove(self, entity: M, session: AsyncSession) -> None:
        entity.status = OrderStatus.CANCELLED
        session.add(entity)
        await session.commit()
