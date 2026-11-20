"""The orders placed. A line keeps the name and the price of the day: a later price change leaves a
past order as it was."""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

# The first order is number 1001: a shop that starts at 1 looks like it sold nothing.
FIRST_NUMBER = 1000


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120))
    address: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(80))
    postcode: Mapped[str] = mapped_column(String(12))
    shipping_cents: Mapped[int]
    placed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    lines: Mapped[list["OrderLineModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def number(self) -> int:
        return FIRST_NUMBER + self.id

    @property
    def subtotal_cents(self) -> int:
        return sum(line.total_cents for line in self.lines)

    @property
    def total_cents(self) -> int:
        return self.subtotal_cents + self.shipping_cents


class OrderLineModel(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    slug: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(120))
    price_cents: Mapped[int]
    quantity: Mapped[int]
    order: Mapped[OrderModel] = relationship(back_populates="lines")

    @property
    def total_cents(self) -> int:
        return self.price_cents * self.quantity
