from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


class CategorySchemaCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str
