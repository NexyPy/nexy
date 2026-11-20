"""The cart: `{slug: quantity}` kept in the session cookie, so it needs no account."""

from dataclasses import dataclass

from src.store.catalog import Product, find

MAX_QUANTITY = 10
FREE_SHIPPING = 5000
SHIPPING = 500


@dataclass(frozen=True)
class Line:
    product: Product
    quantity: int

    @property
    def total(self) -> int:
        return self.product.price_cents * self.quantity


@dataclass(frozen=True)
class Summary:
    lines: list[Line]
    count: int
    subtotal: int
    shipping: int
    total: int


def put(cart: dict[str, int], slug: str, quantity: int) -> dict[str, int]:
    """The cart with `quantity` of `slug`: 0 removes it, an unknown product changes nothing."""
    if find(slug) is None:
        return dict(cart)
    kept = {key: value for key, value in cart.items() if key != slug}
    if quantity > 0:
        kept[slug] = min(quantity, MAX_QUANTITY)
    return kept


def add(cart: dict[str, int], slug: str, quantity: int = 1) -> dict[str, int]:
    return put(cart, slug, cart.get(slug, 0) + max(quantity, 0))


def summary(cart: dict[str, int]) -> Summary:
    """The lines of the cart, and what it costs with shipping (free from $50)."""
    lines = [Line(product, count) for slug, count in cart.items() if (product := find(slug))]
    subtotal = sum(line.total for line in lines)
    shipping = 0 if not lines or subtotal >= FREE_SHIPPING else SHIPPING
    count = sum(line.quantity for line in lines)
    return Summary(lines, count, subtotal, shipping, subtotal + shipping)
