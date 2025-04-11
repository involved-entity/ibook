from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class AddressBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: Annotated[str, Field(max_length=100, examples=["Moscow"])]
    street: Annotated[str, Field(max_length=100, examples=["Lenina"])]
    house: Annotated[str, Field(max_length=20, examples=["15A"])]
    postal_code: Annotated[str, Field(max_length=20, examples=["123456"])]


class AddressCreateSchema(AddressBaseSchema):
    apartment: Annotated[Optional[str], Field(max_length=20, examples=["42"], default=None)] = None
    is_primary: Annotated[bool, Field(examples=[False], default=False)] = False


class AddressSchema(AddressCreateSchema):
    id: int


class AddressUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: Annotated[Optional[str], Field(max_length=100)] = None
    street: Annotated[Optional[str], Field(max_length=100)] = None
    house: Annotated[Optional[str], Field(max_length=20)] = None
    apartment: Annotated[Optional[str], Field(max_length=20)] = None
    postal_code: Annotated[Optional[str], Field(max_length=20)] = None
    is_primary: Annotated[Optional[bool], Field()] = None
