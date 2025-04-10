import typing

from pydantic import BaseModel


class SellerSchema(BaseModel):
    first_name: str
    last_name: typing.Optional[str]
