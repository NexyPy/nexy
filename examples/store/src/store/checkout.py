"""Check the checkout form, then turn the cart into an order kept in the database."""

import re
import secrets

from sqlmodel import Session, select

from src.configs import db
from src.models.order import Order, OrderLine
from src.store.cart import Summary

FIELDS = ("name", "email", "address", "city", "postal_code")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def problems(form: dict[str, str]) -> dict[str, str]:
    """What is wrong with each field of the form; empty when the order can be placed."""
    found = {field: "Fill this in." for field in FIELDS if not form.get(field, "").strip()}
    if "email" not in found and not EMAIL.match(form["email"].strip()):
        found["email"] = "Write an email like name@example.com."
    if any(len(form.get(field, "")) > 200 for field in FIELDS):
        found.setdefault("address", "Keep each field under 200 characters.")
    return found


def place(form: dict[str, str], cart: Summary) -> str:
    """Save the order and its lines; its number, for the confirmation page."""
    number = f"FS-{secrets.token_hex(3).upper()}"
    order = Order(
        number=number,
        subtotal_cents=cart.subtotal,
        shipping_cents=cart.shipping,
        **{field: form[field].strip() for field in FIELDS},
    )
    with Session(db.engine) as session:
        session.add(order)
        session.flush()
        session.add_all(
            OrderLine(
                order_id=order.id or 0,
                slug=line.product.slug,
                name=line.product.name,
                quantity=line.quantity,
                price_cents=line.product.price_cents,
            )
            for line in cart.lines
        )
        session.commit()
    return number


def receipt(number: str) -> tuple[Order, list[OrderLine]] | None:
    """An order and its lines, or None."""
    with Session(db.engine) as session:
        order = session.exec(select(Order).where(Order.number == number)).first()
        if order is None:
            return None
        lines = list(session.exec(select(OrderLine).where(OrderLine.order_id == order.id)).all())
    return order, lines
