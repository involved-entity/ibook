from datetime import datetime
from typing import Annotated, Any, Optional, Self

from pydantic import BaseModel, ConfigDict, Field

from core.api.categories.schemas import CategorySchema
from core.api.users.schemas import SellerSchema


class BookImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str = Field(examples=["https://example.com/book1.jpg"])
    is_main: bool = Field(examples=[True, False])


class BookCategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: CategorySchema


class BookBaseSchema(BaseModel):
    title: str = Field(examples=["Clean Code"], max_length=100)
    author: str = Field(examples=["Robert Martin"], max_length=50)
    description: Optional[str] = Field(
        default=None, examples=["A book about writing maintainable code"], max_length=1000
    )
    price: float = Field(examples=[29.99], gt=0)
    publication_year: Optional[int] = Field(default=None, examples=[2008], le=datetime.now().year)
    pages: Optional[int] = Field(default=None, examples=[464], gt=0)


class BookSchema(BookBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    seller: SellerSchema
    images: list[BookImageSchema] = Field(default_factory=list)
    categories: Any

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
        validated = super().model_validate(obj)
        validated.categories = [link.category.name for link in obj.categories if hasattr(link, "category")]
        return validated


class BookCreateSchema(BookBaseSchema):
    categories: Annotated[list[str], Field(examples=[["Programming", "Software-engineering"]], exclude=True)]


class BookUpdateSchema(BaseModel):
    title: Optional[str] = Field(default=None, examples=["Refactoring Improved"], max_length=100)
    author: Optional[str] = Field(default=None, examples=["Martin Fowler"], max_length=50)
    description: Optional[str] = Field(default=None, examples=["Updated edition of the classic book"], max_length=1000)
    price: Optional[float] = Field(default=None, examples=[34.99], gt=0)
    publication_year: Optional[int] = Field(default=None, examples=[2023], ge=1900, le=datetime.now().year)
    pages: Optional[int] = Field(default=None, examples=[500], gt=0)
