from pydantic import BaseModel, ConfigDict


class CategoryCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str


class CategorySchema(CategoryCreateSchema):
    id: int


class CategoryUpdateSchema(BaseModel):
    pass
