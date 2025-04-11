from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import Book, Category


class BookCategory(Base):
    __tablename__ = "book_categories"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    book: Mapped["Book"] = relationship(back_populates="categories")
    category: Mapped["Category"] = relationship(back_populates="books")

    __table_args__ = (UniqueConstraint("category_id", "book_id", name="uix_book_category"),)
