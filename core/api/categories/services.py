from core.api.categories.schemas import CategorySchema, CategorySchemaCreate
from core.api.services import CRUDService
from core.database.models import Category


class CategoriesCRUDService(CRUDService):
    model = Category
    schema_class = CategorySchema
    create_schema_class = CategorySchemaCreate
