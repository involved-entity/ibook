import typing

from pydantic import BaseModel, ConfigDict, Field


class OrderItemsCreateWithoutOrderIDSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: typing.Annotated[int, Field(gt=0)]
    quantity: typing.Annotated[int, Field(gt=0, default=1)] = 1


class OrderItemsCreateSchema(OrderItemsCreateWithoutOrderIDSchema):
    order_id: typing.Annotated[int, Field(gt=0)]


class OrderItemsSchema(OrderItemsCreateSchema):
    id: int
    price: int


class OrderItemsUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    quantity: typing.Annotated[int | None, Field(gt=0, default=None)] = None
    price: typing.Annotated[int | None, Field(gt=0, default=None)] = None
