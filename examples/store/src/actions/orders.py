"""The actions of the checkout, and of the orders this browser placed."""

import re
from datetime import UTC, datetime

from pydantic import BaseModel

from nexy import notFound
from nexy.decorators import Action
from nexy.http import Request
from src.actions.cart import COOKIE
from src.models.order_model import OrderModel
from src.services.order_service import Delivery, OrderService

# What each field of the form must hold: its longest value and what to say when it is empty.
FIELDS = {
    "name": (80, "Write the name the parcel goes to."),
    "email": (120, "Write the email address that gets the receipt."),
    "address": (200, "Write the street and the number."),
    "city": (80, "Write the city."),
    "postcode": (12, "Write the postal code."),
}
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class Placed(BaseModel):
    number: int = 0  # the order placed; 0 when it was not
    errors: dict[str, str] = {}  # each field to fix and why; "cart" for the cart itself


class OrderLine(BaseModel):
    slug: str
    name: str
    price_cents: int
    quantity: int
    total_cents: int


class Order(BaseModel):
    number: int
    placed_at: datetime
    name: str
    email: str
    address: str
    city: str
    postcode: str
    lines: list[OrderLine]
    subtotal_cents: int
    shipping_cents: int
    total_cents: int


class OrderSummary(BaseModel):
    number: int
    placed_at: datetime
    count: int
    total_cents: int


def placed_at(order: OrderModel) -> datetime:
    """When the order was placed, in UTC. SQLite gives the time back without its zone, and a
    browser would read such a time as its own local one."""
    return order.placed_at.replace(tzinfo=UTC)


def problems(delivery: Delivery) -> dict[str, str]:
    """What is wrong with each field of the form; empty when the parcel can leave."""
    errors = {}
    for field, (longest, missing) in FIELDS.items():
        value = getattr(delivery, field)
        if not value:
            errors[field] = missing
        elif len(value) > longest:
            errors[field] = f"Keep it under {longest} characters."
    if "email" not in errors and not EMAIL.fullmatch(delivery.email):
        errors["email"] = "Write an email address, such as ada@example.com."
    return errors


def order_of(order: OrderModel) -> Order:
    lines = [
        OrderLine(
            slug=line.slug,
            name=line.name,
            price_cents=line.price_cents,
            quantity=line.quantity,
            total_cents=line.total_cents,
        )
        for line in order.lines
    ]
    return Order(
        number=order.number,
        placed_at=placed_at(order),
        name=order.name,
        email=order.email,
        address=order.address,
        city=order.city,
        postcode=order.postcode,
        lines=lines,
        subtotal_cents=order.subtotal_cents,
        shipping_cents=order.shipping_cents,
        total_cents=order.total_cents,
    )


@Action
def place_order(
    name: str, email: str, address: str, city: str, postcode: str, *, request: Request
) -> Placed:
    """Turn the cart of this browser into an order, or say what to fix first."""
    given = (name, email, address, city, postcode)
    delivery = Delivery(*(value.strip() for value in given))
    errors = problems(delivery)
    if errors:
        return Placed(errors=errors)
    placed = OrderService.place(request.cookies.get(COOKIE, ""), delivery)
    if isinstance(placed, str):
        return Placed(errors={"cart": placed})
    return Placed(number=placed.number)


@Action
def orders(*, request: Request) -> list[OrderSummary]:
    """The orders this browser placed, newest first."""
    placed = OrderService.of(request.cookies.get(COOKIE, ""))
    return [
        OrderSummary(
            number=order.number,
            placed_at=placed_at(order),
            count=sum(line.quantity for line in order.lines),
            total_cents=order.total_cents,
        )
        for order in placed
    ]


@Action
def order(number: int, *, request: Request) -> Order:
    """One order of this browser; a 404 for any other, so nobody reads the address of another."""
    found = OrderService.find(request.cookies.get(COOKIE, ""), number)
    if found is None:
        notFound()
    return order_of(found)
