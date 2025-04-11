import typing

from pydantic import BaseModel, ConfigDict, Field


class AddressSchemaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: typing.Annotated[str, Field(max_length=100)]
    street: typing.Annotated[str, Field(max_length=100)]
    house: typing.Annotated[str, Field(max_length=20)]
    apartment: typing.Annotated[str | None, Field(max_length=20, default=None)] = None
    postal_code: typing.Annotated[str, Field(max_length=20)]
    is_primary: typing.Annotated[bool, Field(default=False)] = False


class AddressSchema(AddressSchemaCreate):
    id: int
