"""Change the cart and place the order. The cart lives in the session cookie."""

from nexy import useSession
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.store import cart as carts
from src.store import session
from src.store.checkout import FIELDS, place, problems


def go(path: str) -> RedirectResponse:
    return RedirectResponse(path, status_code=303)


@Action
async def add_to_cart(slug: str, quantity: int = 1) -> dict[str, int]:
    """Called by the Add to cart button; answers how many things the cart now holds."""
    items = carts.add(session.cart(), slug, quantity)
    session.save_cart(items)
    return {"count": carts.summary(items).count}


@Action
async def set_quantity(slug: str, quantity: int) -> RedirectResponse:
    """The quantity form of the cart page; 0 removes the product."""
    session.save_cart(carts.put(session.cart(), slug, quantity))
    return go("/cart")


@Action
async def place_order(
    name: str = "", email: str = "", address: str = "", city: str = "", postal_code: str = ""
) -> RedirectResponse:
    form = dict(zip(FIELDS, (name, email, address, city, postal_code), strict=True))
    summary = carts.summary(session.cart())
    if not summary.lines:
        return go("/cart")
    wrong = problems(form)
    if wrong:
        useSession()["checkout"] = {"values": form, "errors": wrong}
        return go("/checkout")
    number = place(form, summary)
    session.save_cart({})
    session.remember_order(number)
    useSession().pop("checkout", None)
    return go(f"/orders/{number}")
