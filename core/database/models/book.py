from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import BookCategory, BookImage, OrderItem, User


class Book(Base):
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    publication_year: Mapped[int] = mapped_column(nullable=True)
    pages: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(UTC),
        server_onupdate=func.now(),
        onupdate=lambda: datetime.now(UTC),
    )

    seller: Mapped["User"] = relationship(back_populates="seller_books")
    categories: Mapped[list["BookCategory"]] = relationship(back_populates="book")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="book")
    images: Mapped[list["BookImage"]] = relationship(back_populates="book")
