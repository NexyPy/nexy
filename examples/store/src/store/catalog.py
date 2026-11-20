"""The products of the shop. A small catalog lives in code; a large one would live in a database."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    slug: str
    name: str
    category: str
    price_cents: int
    summary: str
    details: tuple[str, ...]


PRODUCTS = (
    Product(
        "ceramic-mug",
        "Ceramic mug",
        "Kitchen",
        1800,
        "A wide stoneware mug that keeps coffee warm.",
        ("350 ml", "Glazed stoneware, dishwasher safe", "Made in Portugal"),
    ),
    Product(
        "pour-over",
        "Pour-over dripper",
        "Kitchen",
        3200,
        "Brews one or two cups through a paper filter.",
        ("Fits size 02 filters", "Porcelain", "Comes with 40 filters"),
    ),
    Product(
        "linen-apron",
        "Linen apron",
        "Kitchen",
        3800,
        "A heavy linen apron with two deep pockets.",
        ("Washed linen", "Adjustable neck strap", "One size"),
    ),
    Product(
        "dot-notebook",
        "Dot grid notebook",
        "Paper",
        1400,
        "192 pages of dot grid on paper that takes ink.",
        ("A5, lay-flat binding", "100 g/m2 paper", "Numbered pages"),
    ),
    Product(
        "pencil-set",
        "Pencil set of six",
        "Paper",
        900,
        "Six cedar pencils, from hard to soft.",
        ("2H, H, HB, B, 2B, 4B", "Cedar wood", "Sharpened"),
    ),
    Product(
        "canvas-tote",
        "Canvas tote",
        "Bags",
        2400,
        "A tote that carries a laptop and the groceries.",
        ("Heavy cotton canvas", "Inner pocket", "40 x 38 cm"),
    ),
    Product(
        "field-bag",
        "Field bag",
        "Bags",
        6400,
        "A waxed shoulder bag for a day out.",
        ("Waxed cotton", "Brass buckles", "Fits a 13 inch laptop"),
    ),
    Product(
        "wool-beanie",
        "Wool beanie",
        "Wear",
        2800,
        "A ribbed beanie knitted from soft merino.",
        ("100% merino wool", "One size", "Hand wash"),
    ),
)
CATEGORIES = tuple(dict.fromkeys(product.category for product in PRODUCTS))


def find(slug: str) -> Product | None:
    return next((product for product in PRODUCTS if product.slug == slug), None)


def browse(text: str = "", category: str = "") -> list[Product]:
    """The products whose name or summary holds `text`, in `category` when one is given."""
    words = text.strip().lower()
    return [
        product
        for product in PRODUCTS
        if (not category or product.category == category)
        and (words in product.name.lower() or words in product.summary.lower())
    ]


def money(cents: int) -> str:
    """`1800` cents as `$18.00`."""
    return f"${cents / 100:,.2f}"
