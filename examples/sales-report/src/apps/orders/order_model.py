"""The orders of the shop. An order holds one product, in one or more units."""

from datetime import date

from sqlmodel import Field, SQLModel

CHANNELS = ("Online", "Wholesale", "Cafe")


class OrderModel(SQLModel, table=True):
    __tablename__ = "orders"

    id: int | None = Field(default=None, primary_key=True)
    placed_on: date = Field(index=True)
    channel: str = Field(index=True, max_length=20)
    region: str = Field(max_length=20)
    product: str = Field(max_length=60)
    units: int
    revenue_cents: int
