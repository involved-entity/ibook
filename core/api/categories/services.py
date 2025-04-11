from sqlalchemy import select
from sqlalchemy.sql.selectable import Select

from core.api.categories.schemas import CategorySchema, CategorySchemaCreate
from core.api.services import CRUDService
from core.database.models import Category


class CategoriesCRUDService(CRUDService):
    model = Category
    schema_class = CategorySchema
    create_schema_class = CategorySchemaCreate

    def get_entities_default_query(self) -> Select:
        return select(self.model).order_by(self.model.id)
