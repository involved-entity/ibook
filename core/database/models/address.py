from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import Order, User


class Address(Base):
    __tablename__ = "addresses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    city: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(100))
    house: Mapped[str] = mapped_column(String(20))
    apartment: Mapped[str] = mapped_column(String(20), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20))
    is_primary: Mapped[bool] = mapped_column(default=False)

    user: Mapped[User] = relationship(back_populates="addresses")
    orders: Mapped[list[Order]] = relationship(back_populates="address")

    __table_args__ = (Index("uq_user_primary_address", user_id, unique=True, postgresql_where=(is_primary is True)),)
