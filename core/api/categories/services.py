from fastapi import HTTPException, status

from core.api.categories.schemas import CategoryCreateSchema, CategorySchema
from core.api.services import CRUDService
from core.database.models import Category


class CategoriesCRUDService(CRUDService):
    model = Category
    schema_class = CategorySchema
    create_schema_class = CategoryCreateSchema

    list_pagination = False
    use_cache = True

    create_entity_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="This name and/or slug already exists"
    )
