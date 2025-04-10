from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from core.api.books.schemas import BookCreateSchema, BookSchema
from core.api.services import CRUDService, M
from core.database.models import Book, BookCategory, Category


class BooksCRUDService(CRUDService):
    model = Book
    schema_class = BookSchema
    create_schema_class = BookCreateSchema

    def get_entities_default_query(self) -> Select:
        return (
            select(self.model)
            .options(
                joinedload(self.model.seller), selectinload(self.model.order_items), selectinload(self.model.images)
            )
            .outerjoin(self.model.categories)
            .outerjoin(BookCategory.category)
            .add_columns(Category.name)
            .order_by(self.model.id)
        )

    def before_entity_create(self, entity: M, session: AsyncSession) -> M:
        entity.seller_id = 1
        return entity
