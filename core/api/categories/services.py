from core.api.categories.schemas import CategoryCreateSchema, CategorySchema
from core.api.services import CRUDService
from core.database.models import Category


class CategoriesCRUDService(CRUDService):
    model = Category
    schema_class = CategorySchema
    create_schema_class = CategoryCreateSchema
