import typing

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: typing.Annotated[str, Field(examples=["Trillers"])]
    slug: typing.Annotated[str, Field(examples=["trillers"])]


class CategorySchema(CategoryCreateSchema):
    id: int


class CategoryUpdateSchema(BaseModel):
    pass
