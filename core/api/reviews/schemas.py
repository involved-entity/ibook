import datetime
import typing

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book_id: typing.Annotated[int, Field(gt=0)]
    rating: typing.Annotated[int, Field(gt=0, le=5)]
    text: str | None = None


class ReviewSchema(ReviewCreateSchema):
    user_id: int
    created_at: datetime.datetime
    id: int


class ReviewUpdateSchema(BaseModel):
    rating: typing.Annotated[int | None, Field(gt=0, le=5)] = None
    text: str | None = None
