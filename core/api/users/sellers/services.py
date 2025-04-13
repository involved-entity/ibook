from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.users.sellers.schemas import SellerSchema
from core.database.models import Book, Review, User
from core.database.models.user import UserRole


async def get_seller_data(seller_id: int, session: AsyncSession) -> SellerSchema:
    book_avg_subq = (
        select(
            Book.id.label("book_id"),
            func.avg(Review.rating).label("book_avg_rating"),
        )
        .join(Review, Book.reviews)
        .where(Book.seller_id == seller_id)
        .group_by(Book.id)
        .subquery("book_avg_subq")
    )

    stmt = (
        select(
            User,
            func.count(Book.id).label("books_count"),
            func.avg(book_avg_subq.c.book_avg_rating).label("average_rating"),
        )
        .select_from(User)
        .outerjoin(Book, User.seller_books)
        .outerjoin(book_avg_subq, Book.id == book_avg_subq.c.book_id)
        .where(User.id == seller_id)
        .group_by(User.id)
    )

    result = await session.execute(stmt)
    row = result.mappings().first()

    if not row or row["User"].role != UserRole.SELLER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found.")

    seller = {
        **row["User"].__dict__,
        "registration_date": row["User"].registration_date,
        "books_count": row["books_count"],
        "average_rating": float(row["average_rating"]) if row["average_rating"] is not None else None,
    }

    return SellerSchema.model_validate(seller).model_dump()
