import typing
from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field

from core.api.categories.schemas import CategorySchema
from core.api.users.schemas import SellerSchema


class BookImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    is_main: bool


class BookCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: CategorySchema


class BookSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    author: str
    description: typing.Optional[str]
    price: float
    publication_year: typing.Optional[int]
    pages: typing.Optional[int]
    created_at: datetime
    updated_at: datetime

    seller: SellerSchema
    categories: list[str]
    images: list[BookImageSchema]

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        book = super().model_validate(obj)
        book.categories = [link.category.name for link in obj.categories]
        return book


class BookCreateSchema(BaseModel):
    title: str
    author: str
    description: typing.Optional[str] = None
    price: float
    publication_year: typing.Optional[int] = None
    pages: typing.Optional[int] = None

    categories: typing.Annotated[list[str], Field(exclude=True)]
