from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.api.books.schemas import BookSchema
from core.database.models import Book, BookCategory, Category


async def get_books_list(session: AsyncSession) -> list[BookSchema]:
    stmt = (
        select(Book)
        .options(joinedload(Book.seller), selectinload(Book.order_items), selectinload(Book.images))
        .join(Book.categories)
        .join(BookCategory.category)
        .add_columns(Category.name)
        .order_by(Book.id)
    )
    books = await session.scalars(stmt)
    return [BookSchema.model_validate(book) for book in books]
