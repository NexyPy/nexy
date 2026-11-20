"""The actions of the cart. It lives in the `cart_lines` table, behind a token the cookie of the
browser holds: no account, and the server always knows what the cart contains."""

import secrets

from pydantic import BaseModel

from nexy.decorators import Action
from nexy.http import Request, Response
from src.models.cart_model import CartLineModel
from src.services.cart_service import CartService, shipping_for

COOKIE = "cart"
MONTH = 60 * 60 * 24 * 30


class Line(BaseModel):
    slug: str
    name: str
    image: str
    price_cents: int
    quantity: int
    stock: int
    total_cents: int


class Cart(BaseModel):
    lines: list[Line]
    count: int
    subtotal_cents: int
    shipping_cents: int
    total_cents: int
    note: str = ""  # why the last change kept fewer than asked; empty when it kept them all


def token(request: Request, response: Response) -> str:
    """The cart of this browser: the one its cookie names, or a new one the cookie will keep."""
    existing = request.cookies.get(COOKIE)
    if existing:
        return existing
    created = secrets.token_urlsafe(24)
    secure = request.url.scheme == "https"
    response.set_cookie(
        COOKIE, created, max_age=MONTH, httponly=True, samesite="lax", secure=secure
    )
    return created


def line_of(line: CartLineModel) -> Line:
    product = line.product
    return Line(
        slug=product.slug,
        name=product.name,
        image=product.image,
        price_cents=product.price_cents,
        quantity=line.quantity,
        stock=product.stock,
        total_cents=line.total_cents,
    )


def cart_of(cart: str, note: str = "") -> Cart:
    """What `cart` holds and what it costs; the server counts, the page only shows."""
    lines = [line_of(line) for line in CartService.lines(cart)]
    subtotal = sum(line.total_cents for line in lines)
    shipping = shipping_for(subtotal)
    count = sum(line.quantity for line in lines)
    return Cart(
        lines=lines,
        count=count,
        subtotal_cents=subtotal,
        shipping_cents=shipping,
        total_cents=subtotal + shipping,
        note=note,
    )


@Action
def cart(*, request: Request) -> Cart:
    """What the cart of this browser holds; an empty one, and no cookie, until it adds something."""
    return cart_of(request.cookies.get(COOKIE, ""))


@Action
def add_to_cart(slug: str, quantity: int = 1, *, request: Request, response: Response) -> Cart:
    owner = token(request, response)
    return cart_of(owner, CartService.add(owner, slug, quantity))


@Action
def set_quantity(slug: str, quantity: int, *, request: Request, response: Response) -> Cart:
    owner = token(request, response)
    return cart_of(owner, CartService.put(owner, slug, quantity))


@Action
def remove_from_cart(slug: str, *, request: Request, response: Response) -> Cart:
    owner = token(request, response)
    return cart_of(owner, CartService.put(owner, slug, 0))
