"""Every read and write of the carts. A cart is the lines that share a token, the one a cookie holds."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.configs.db import engine
from src.models.cart_model import CartLineModel
from src.models.product_model import ProductModel

# Delivery is free from $50 and costs $5 below.
FREE_SHIPPING_FROM = 5000
SHIPPING = 500


def shipping_for(subtotal_cents: int) -> int:
    """What delivery costs for goods worth `subtotal_cents`; nothing for an empty cart."""
    if subtotal_cents == 0 or subtotal_cents >= FREE_SHIPPING_FROM:
        return 0
    return SHIPPING


def short_of(product: ProductModel, quantity: int) -> str:
    """Why the cart keeps fewer than `quantity`, or an empty string when it keeps them all."""
    if quantity <= product.stock:
        return ""
    if product.stock == 0:
        return f"{product.name} is sold out."
    return f"Only {product.stock} left of {product.name}: your cart holds them all."


def hold(session: Session, cart: str, product: ProductModel, quantity: int) -> None:
    """Make the line of `product` hold `quantity`; zero takes it out of the cart."""
    line = session.scalar(
        select(CartLineModel).where(
            CartLineModel.cart == cart, CartLineModel.product_id == product.id
        )
    )
    if line is None and quantity > 0:
        session.add(CartLineModel(cart=cart, product=product, quantity=quantity))
    elif line is not None and quantity > 0:
        line.quantity = quantity
    elif line is not None:
        session.delete(line)


class CartService:
    @staticmethod
    def lines(cart: str) -> list[CartLineModel]:
        """The lines of `cart`, in the order they were added."""
        query = select(CartLineModel).where(CartLineModel.cart == cart).order_by(CartLineModel.id)
        with Session(engine) as session:
            return list(session.scalars(query))

    @staticmethod
    def put(cart: str, slug: str, quantity: int) -> str:
        """Hold `quantity` of a product, as many as the shelves have. Returns why fewer, or ""."""
        with Session(engine) as session:
            product = session.scalar(select(ProductModel).where(ProductModel.slug == slug))
            if product is None:
                return "This product is not sold here."
            hold(session, cart, product, min(max(quantity, 0), product.stock))
            session.commit()
            return short_of(product, quantity)

    @staticmethod
    def add(cart: str, slug: str, quantity: int = 1) -> str:
        """Add `quantity` to what the cart already holds of the product."""
        held = {line.product.slug: line.quantity for line in CartService.lines(cart)}
        return CartService.put(cart, slug, held.get(slug, 0) + quantity)
