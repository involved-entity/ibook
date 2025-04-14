import typing

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field


class BookImageSimplyfiedCreateSchema(BaseModel):
    file: UploadFile
    is_main: bool = False


class BookImageCreateSchema(BookImageSimplyfiedCreateSchema):
    book_id: typing.Annotated[int, Field(gt=0)]


class BookImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    url: str = Field(examples=["https://example.com/book1.jpg"])
    is_main: bool = Field(examples=[True, False])


class BookImageUpdateSchema(BaseModel):
    pass
