import typing
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.api.addresses.schemas import AddressSchema
from core.api.order_items.schemas import OrderItemsCreateWithoutOrderIDSchema, OrderItemsSchema
from core.database.models.order import OrderStatus


class OrderCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    address_id: typing.Annotated[int, Field(gt=0)]
    items: list[OrderItemsCreateWithoutOrderIDSchema] | None = None


class OrderSchema(OrderCreateSchema):
    created_at: datetime
    updated_at: datetime
    status: OrderStatus
    tracking_number: str | None = None
    items: list[OrderItemsSchema] | None = None
    address: AddressSchema
    payment: list | None = None
    id: int


class OrderUpdateSchema(OrderCreateSchema):
    address_id: typing.Annotated[int | None, Field(gt=0, default=None)] = None
    status: OrderStatus | None = None
    tracking_number: str | None = None
