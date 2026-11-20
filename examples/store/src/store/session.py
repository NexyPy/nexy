"""What the shop keeps in the session cookie: the cart, and the orders this visitor placed."""

from nexy import useSession


def cart() -> dict[str, int]:
    return dict(useSession().get("cart", {}))


def save_cart(items: dict[str, int]) -> None:
    useSession()["cart"] = items


def remember_order(number: str) -> None:
    """Only the visitor who placed an order sees its page: its number is kept in the session."""
    session = useSession()
    session["orders"] = [*session.get("orders", []), number][-20:]


def placed(number: str) -> bool:
    return number in useSession().get("orders", [])
