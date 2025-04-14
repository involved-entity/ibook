import typing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from core.api.book_images.services import save_uploaded_book_image
from core.api.books.schemas import BookCreateSchema, BookSchema
from core.api.services import C, CRUDService, M
from core.database.models import Book, BookCategory, Category, User


class BooksCRUDService(CRUDService):
    model = Book
    schema_class = BookSchema
    create_schema_class = BookCreateSchema

    user_field = "seller_id"

    admin_or_owner_to_edit = True
    save_user_id_before_create = True

    def get_entities_default_query(self, query: typing.Optional[dict] = None) -> Select:
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.seller),
                selectinload(self.model.order_items),
                selectinload(self.model.images),
                selectinload(self.model.categories).joinedload(BookCategory.category),
            )
            .order_by(self.model.id)
        )

        if query.get("author"):
            stmt = stmt.filter(self.model.author.ilike(f"%{query['author']}%"))
        if query.get("title"):
            stmt = stmt.filter(self.model.title.ilike(f"%{query['title']}%"))
        if query.get("seller_id") and query["seller_id"].isnumeric():
            stmt = stmt.where(self.model.seller_id == int(query["seller_id"]))

        return stmt

    async def after_entity_create(self, entity: M, create_entity: C, user: User, session: AsyncSession) -> M:
        if create_entity.categories:
            stmt = select(Category).where(Category.name.in_(create_entity.categories))
            existing_categories = await session.scalars(stmt)

            for category in existing_categories:
                book_category = BookCategory(book_id=entity.id, category_id=category.id)  # noqa
                session.add(book_category)

            await session.commit()

        if create_entity.images:
            for img_data in create_entity.images:
                book_image = await save_uploaded_book_image(img_data.file, entity.id, img_data.is_main)  # noqa
                session.add(book_image)

            await session.commit()

        return entity
