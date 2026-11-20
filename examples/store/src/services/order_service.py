"""Placing an order: the cart becomes an order, the shelves lose what it took, the cart empties."""

from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.configs.db import engine
from src.models.cart_model import CartLineModel
from src.models.order_model import FIRST_NUMBER, OrderLineModel, OrderModel
from src.models.product_model import ProductModel
from src.services.cart_service import shipping_for


@dataclass(frozen=True)
class Delivery:
    """Where an order goes."""

    name: str
    email: str
    address: str
    city: str
    postcode: str


def problem_with(lines: list[CartLineModel]) -> str:
    """Why these lines cannot become an order, or an empty string."""
    if not lines:
        return "Your cart is empty."
    for line in lines:
        if line.quantity > line.product.stock:
            left = line.product.stock
            return f"Only {left} left of {line.product.name}: change the quantity in your cart."
    return ""


def order_of(customer: str, delivery: Delivery, lines: list[CartLineModel]) -> OrderModel:
    """The order of the lines, at the prices of the day."""
    copied = [
        OrderLineModel(
            slug=line.product.slug,
            name=line.product.name,
            price_cents=line.product.price_cents,
            quantity=line.quantity,
        )
        for line in lines
    ]
    shipping = shipping_for(sum(line.total_cents for line in lines))
    return OrderModel(customer=customer, shipping_cents=shipping, lines=copied, **vars(delivery))


def take(session: Session, line: CartLineModel) -> bool:
    """Take the products of `line` off the shelves, if they are still there.

    The shelves are checked and changed in one statement: two checkouts at the same moment can
    never both take the last field bag.
    """
    taken = session.execute(
        update(ProductModel)
        .where(ProductModel.id == line.product_id, ProductModel.stock >= line.quantity)
        .values(stock=ProductModel.stock - line.quantity)
    )
    return taken.rowcount == 1


class OrderService:
    @staticmethod
    def place(cart: str, delivery: Delivery) -> OrderModel | str:
        """The order placed from `cart`, or why it was not: an empty cart, or a product gone."""
        with Session(engine, expire_on_commit=False) as session:
            query = select(CartLineModel).where(CartLineModel.cart == cart)
            lines = list(session.scalars(query.order_by(CartLineModel.id)))
            problem = problem_with(lines)
            if problem:
                return problem
            order = order_of(cart, delivery, lines)
            if not all(take(session, line) for line in lines):
                session.rollback()
                return "A product of your cart just ran out: look at your cart again."
            for line in lines:
                session.delete(line)
            session.add(order)
            session.commit()
            return order

    @staticmethod
    def of(customer: str) -> list[OrderModel]:
        """The orders `customer` placed, newest first."""
        query = select(OrderModel).where(OrderModel.customer == customer)
        with Session(engine) as session:
            return list(session.scalars(query.order_by(OrderModel.id.desc())))

    @staticmethod
    def find(customer: str, number: int) -> OrderModel | None:
        """Order `number`, when `customer` placed it: nobody reads the orders of another."""
        with Session(engine) as session:
            order = session.get(OrderModel, number - FIRST_NUMBER)
            return order if order is not None and order.customer == customer else None
