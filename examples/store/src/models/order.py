from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def _now() -> datetime:
    return datetime.now(UTC)


class Order(SQLModel, table=True):
    """An order placed at checkout: who it goes to, and what it cost."""

    id: int | None = Field(default=None, primary_key=True)
    number: str = Field(unique=True, index=True)
    name: str
    email: str
    address: str
    city: str
    postal_code: str
    subtotal_cents: int
    shipping_cents: int
    created_at: datetime = Field(default_factory=_now)


class OrderLine(SQLModel, table=True):
    """One product of an order, with its name and price as they were when it was bought."""

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    slug: str
    name: str
    quantity: int
    price_cents: int
