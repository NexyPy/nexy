"""record four months of orders

Revision ID: bb0f5c59b80e
Revises: a5b8a8e4dbd0
Create Date: 2026-11-20 20:59:49.476910

"""
from typing import Sequence, Union

from datetime import date, timedelta

import sqlalchemy as sa
from alembic import op
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'bb0f5c59b80e'
down_revision: Union[str, Sequence[str], None] = 'a5b8a8e4dbd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Four months of orders, ending on the day below. They are made by a fixed formula and a seeded
# generator written out here, not imported from the application: a migration keeps doing what it
# did on the day it was written, and every copy of the example shows the same numbers.
LAST_DAY = date(2026, 11, 15)
DAYS = 120
PRODUCTS = {  # name: price in cents
    "House blend 250g": 1400,
    "Ethiopia Guji 250g": 1800,
    "Colombia Huila 250g": 1650,
    "Decaf 250g": 1500,
    "Espresso beans 1kg": 4800,
    "Cold brew pack": 2200,
    "Pour-over kit": 3900,
    "Gift box": 5500,
}
# Orders on a Monday for each channel, and how many units one order holds at most.
CHANNELS = {"Online": (9, 3), "Wholesale": (2, 24), "Cafe": (6, 2)}
WEEK = (1.0, 0.9, 0.95, 1.05, 1.25, 1.5, 1.3)  # Monday to Sunday
REGIONS = ("North", "South", "East", "West")

orders = sa.table(
    "orders",
    sa.column("placed_on", sa.Date),
    sa.column("channel", sa.String),
    sa.column("region", sa.String),
    sa.column("product", sa.String),
    sa.column("units", sa.Integer),
    sa.column("revenue_cents", sa.Integer),
)


class Draw:
    """A small linear congruential generator: the same numbers on every machine and Python."""

    def __init__(self, seed: int) -> None:
        self.state = seed

    def __call__(self, below: int) -> int:
        self.state = (self.state * 1103515245 + 12345) % 2**31
        return self.state % below


def day_rows(day: date, draw: Draw) -> list[dict]:
    growth = 1 + 0.35 * (day - LAST_DAY + timedelta(days=DAYS)).days / DAYS
    rows = []
    for channel, (base, most) in CHANNELS.items():
        count = round(base * WEEK[day.weekday()] * growth) + draw(3) - 1
        for _ in range(max(count, 0)):
            product = list(PRODUCTS)[draw(len(PRODUCTS))]
            units = 1 + draw(most)
            rows.append({
                "placed_on": day,
                "channel": channel,
                "region": REGIONS[draw(len(REGIONS))],
                "product": product,
                "units": units,
                "revenue_cents": units * PRODUCTS[product],
            })
    return rows


def upgrade() -> None:
    draw = Draw(2026)
    first = LAST_DAY - timedelta(days=DAYS - 1)
    rows = [row for n in range(DAYS) for row in day_rows(first + timedelta(days=n), draw)]
    op.bulk_insert(orders, rows)


def downgrade() -> None:
    first = LAST_DAY - timedelta(days=DAYS - 1)
    op.execute(orders.delete().where(orders.c.placed_on.between(first, LAST_DAY)))
