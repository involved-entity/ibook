from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base

if TYPE_CHECKING:
    from core.database.models import Address, OrderItem, Payment, User


class OrderStatus(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.CREATED)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        server_onupdate=func.now(),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
    )
    tracking_number: Mapped[str] = mapped_column(String(50), nullable=True)

    user: Mapped["User"] = relationship(back_populates="orders")
    address: Mapped["Address"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")
    payment: Mapped["Payment"] = relationship(back_populates="order")
