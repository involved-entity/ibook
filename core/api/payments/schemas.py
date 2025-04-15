import typing
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.database.models.payment import PaymentStatus


class PaymentBase(BaseModel):
    amount: typing.Annotated[float, Field(ge=10)]
    currency: str = "usd"
    order_id: typing.Annotated[int, Field(gt=0)]


class PaymentCreateSchema(PaymentBase):
    pass


class PaymentSchema(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: str
    created_at: datetime
    status: PaymentStatus


class PaymentCreateResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_secret: str
