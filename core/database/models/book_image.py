from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import Book


class BookImage(Base):
    __tablename__ = "book_images"

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    url: Mapped[str] = mapped_column(String(255))
    is_main: Mapped[bool] = mapped_column(default=False)

    book: Mapped["Book"] = relationship(back_populates="images")

    __table_args__ = (Index("uq_book_main_image", book_id, unique=True, postgresql_where=(is_main == True)),)
