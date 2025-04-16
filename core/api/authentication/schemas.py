import typing
from enum import Enum

from fastapi_users import schemas
from pydantic import Field, field_validator


class UserCreateRole(str, Enum):
    SELLER = "SELLER"
    CUSTOMER = "CUSTOMER"


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    first_name: typing.Annotated[str, Field(max_length=50, examples=["John"])]
    last_name: typing.Annotated[str, Field(max_length=50, examples=["Cena"], default=None)] = None
    phone: typing.Annotated[str, Field(max_length=20, examples=["+79991234567"])]
    role: typing.Annotated[UserCreateRole, Field(default=UserCreateRole.CUSTOMER, examples=["SELLER", "CUSTOMER"])] = (
        UserCreateRole.CUSTOMER
    )

    @classmethod
    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.startswith("+"):
            raise ValueError("Phone must start with +")
        return v


class UserUpdate(schemas.BaseUserUpdate):
    pass
