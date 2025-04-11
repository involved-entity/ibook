import typing

from pydantic import BaseModel, ConfigDict


class SellerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: typing.Optional[str] = None
