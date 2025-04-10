from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from core.api.books.schemas import BookCreateSchema, BookSchema
from core.database.models import Book, BookCategory, Category


def get_books_default_query() -> Select:
    return (
        select(Book)
        .options(joinedload(Book.seller), selectinload(Book.order_items), selectinload(Book.images))
        .outerjoin(Book.categories)
        .outerjoin(BookCategory.category)
        .add_columns(Category.name)
        .order_by(Book.id)
    )


async def get_books_list(session: AsyncSession) -> list[BookSchema]:
    books = await session.scalars(get_books_default_query())
    return [BookSchema.model_validate(book) for book in books]


async def create_book_entity(create_book_schema: BookCreateSchema, session: AsyncSession) -> BookSchema:
    book = Book(**create_book_schema.model_dump())
    book.seller_id = 1
    session.add(book)
    await session.commit()
    stmt = get_books_default_query().where(Book.id == book.id)
    book = await session.scalars(stmt)
    return BookSchema.model_validate(book)
