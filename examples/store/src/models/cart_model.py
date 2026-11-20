"""What a visitor is about to buy. A cart is the lines that share a token, the one its cookie holds."""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base
from src.models.product_model import ProductModel


class CartLineModel(Base):
    __tablename__ = "cart_lines"
    __table_args__ = (UniqueConstraint("cart", "product_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cart: Mapped[str] = mapped_column(String(64), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    product: Mapped[ProductModel] = relationship(lazy="joined")

    @property
    def total_cents(self) -> int:
        return self.product.price_cents * self.quantity
