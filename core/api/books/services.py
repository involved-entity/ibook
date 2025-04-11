from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from core.api.books.schemas import BookCreateSchema, BookSchema
from core.api.services import CRUDService
from core.database.models import Book, BookCategory, Category


class BooksCRUDService(CRUDService):
    model = Book
    schema_class = BookSchema
    create_schema_class = BookCreateSchema

    user_field = "seller_id"

    admin_or_owner_remove = True
    save_user_id_before_create = True

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
