"""The products on the shelves. A price is a number of cents: money never goes through a float."""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40), index=True)
    price_cents: Mapped[int]
    summary: Mapped[str] = mapped_column(String(200))
    details: Mapped[list[str]] = mapped_column(JSON, default=list)
    stock: Mapped[int]

    @property
    def image(self) -> str:
        """The picture of the product, served from `public/products/`."""
        return f"/products/{self.slug}.svg"
