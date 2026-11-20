"""stock the shop: the products and how many of each are on the shelves

Revision ID: 0e7f77b297b2
Revises: 30ce1b187ead
Create Date: 2026-11-20 15:44:46.614411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e7f77b297b2'
down_revision: Union[str, Sequence[str], None] = '30ce1b187ead'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PRODUCTS = sa.table(
    "products",
    sa.column("slug", sa.String),
    sa.column("name", sa.String),
    sa.column("category", sa.String),
    sa.column("price_cents", sa.Integer),
    sa.column("summary", sa.String),
    sa.column("details", sa.JSON),
    sa.column("stock", sa.Integer),
)

# The rows are written out here, not imported from the application: a migration keeps doing what it
# did on the day it was written, whatever the code becomes.
SHELVES = [
    {
        "slug": "ceramic-mug",
        "name": "Ceramic mug",
        "category": "Kitchen",
        "price_cents": 1800,
        "summary": "A wide stoneware mug that keeps coffee warm.",
        "details": ["350 ml", "Glazed stoneware, dishwasher safe", "Made in Portugal"],
        "stock": 24,
    },
    {
        "slug": "pour-over",
        "name": "Pour-over dripper",
        "category": "Kitchen",
        "price_cents": 3200,
        "summary": "Brews one or two cups through a paper filter.",
        "details": ["Fits size 02 filters", "Porcelain", "Comes with 40 filters"],
        "stock": 12,
    },
    {
        "slug": "linen-apron",
        "name": "Linen apron",
        "category": "Kitchen",
        "price_cents": 3800,
        "summary": "A heavy linen apron with two deep pockets.",
        "details": ["Washed linen", "Adjustable neck strap", "One size"],
        "stock": 9,
    },
    {
        "slug": "dot-notebook",
        "name": "Dot grid notebook",
        "category": "Paper",
        "price_cents": 1400,
        "summary": "192 pages of dot grid on paper that takes ink.",
        "details": ["A5, lay-flat binding", "100 g/m2 paper", "Numbered pages"],
        "stock": 40,
    },
    {
        "slug": "pencil-set",
        "name": "Pencil set of six",
        "category": "Paper",
        "price_cents": 900,
        "summary": "Six cedar pencils, from hard to soft.",
        "details": ["2H, H, HB, B, 2B, 4B", "Cedar wood", "Sharpened"],
        "stock": 60,
    },
    {
        "slug": "canvas-tote",
        "name": "Canvas tote",
        "category": "Bags",
        "price_cents": 2400,
        "summary": "A tote that carries a laptop and the groceries.",
        "details": ["Heavy cotton canvas", "Inner pocket", "40 x 38 cm"],
        "stock": 18,
    },
    {
        "slug": "field-bag",
        "name": "Field bag",
        "category": "Bags",
        "price_cents": 6400,
        "summary": "A waxed shoulder bag for a day out.",
        "details": ["Waxed cotton", "Brass buckles", "Fits a 13 inch laptop"],
        "stock": 3,
    },
    {
        "slug": "wool-beanie",
        "name": "Wool beanie",
        "category": "Wear",
        "price_cents": 2800,
        "summary": "A ribbed beanie knitted from soft merino.",
        "details": ["100% merino wool", "One size", "Hand wash"],
        "stock": 0,
    },
]


def upgrade() -> None:
    """Put the products on the shelves."""
    op.bulk_insert(PRODUCTS, SHELVES)


def downgrade() -> None:
    """Take them off again."""
    slugs = [product["slug"] for product in SHELVES]
    op.execute(PRODUCTS.delete().where(PRODUCTS.c.slug.in_(slugs)))
