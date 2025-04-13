import typing
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SellerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: typing.Optional[str] = None
    registration_date: datetime
    books_count: int
    average_rating: typing.Optional[float]
