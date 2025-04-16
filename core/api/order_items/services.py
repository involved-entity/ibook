from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.order_items.schemas import OrderItemsCreateSchema, OrderItemsSchema, OrderItemsUpdateSchema
from core.api.services import C, CRUDService, M, U
from core.database.models import Book, Order, OrderItem, User
from core.database.models.order import OrderStatus
from core.database.models.user import UserRole


class OrderItemsCRUDService(CRUDService):
    model = OrderItem
    schema_class = OrderItemsSchema
    create_schema_class = OrderItemsCreateSchema
    update_schema_class = OrderItemsUpdateSchema

    create_entity_error = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order or book not found.")
    not_found_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is cancelled.")

    async def _check_perms_to_order(self, order_id: int, user: User, session: AsyncSession) -> Order | None:  # noqa
        order = await session.get(Order, order_id)
        perms_check = user.role != UserRole.ADMIN and user.id != order.user_id
        order_status_check = order.status == OrderStatus.CANCELLED

        if perms_check:
            raise self.permission_denied_error
        elif order_status_check:
            raise self.not_found_error

        return order

    async def check_permissions_to_edit_entity(self, entity: M, user: User, session: AsyncSession) -> M:
        await self._check_perms_to_order(entity.order_id, user, session)

        return entity

    async def before_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        order = await self._check_perms_to_order(create_entity.order_id, user, session)
        book = await session.get(Book, create_entity.book_id)

        if not book:
            raise self.create_entity_error

        entity.order_id = order.id
        entity.price = book.price

        return entity

    async def before_entity_update(self, entity: M, update_entity: U, user: User, session: AsyncSession) -> M:
        if update_entity.price and user.role != UserRole.ADMIN:
            update_entity.price = None

        return entity
