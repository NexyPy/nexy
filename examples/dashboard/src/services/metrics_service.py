"""What the overview adds up: totals, a value per day, the share of each channel, the best sellers."""

from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import func
from sqlmodel import Session, col, select

from src.configs.db import engine
from src.models.order_model import CHANNELS, OrderModel
from src.services.window import Window


@dataclass(frozen=True)
class Totals:
    revenue_cents: int
    orders: int
    units: int

    @property
    def average_cents(self) -> int:
        return self.revenue_cents // self.orders if self.orders else 0


@dataclass(frozen=True)
class Day:
    day: date
    revenue_cents: int
    orders: int


@dataclass(frozen=True)
class Share:
    name: str
    revenue_cents: int
    units: int


def within(window: Window, query, by_channel: bool = True):
    query = query.where(col(OrderModel.placed_on).between(window.first, window.last))
    if by_channel and window.channel:
        query = query.where(OrderModel.channel == window.channel)
    return query


REVENUE = func.coalesce(func.sum(OrderModel.revenue_cents), 0)
UNITS = func.coalesce(func.sum(OrderModel.units), 0)


class MetricsService:
    def as_of(self) -> date:
        """The last day with an order: the windows end there, so old data still fills them."""
        with Session(engine) as session:
            return session.exec(select(func.max(OrderModel.placed_on))).one() or date.today()

    def totals(self, window: Window) -> Totals:
        query = within(window, select(REVENUE, func.count(), UNITS))
        with Session(engine) as session:
            revenue, orders, units = session.exec(query).one()
        return Totals(revenue, orders, units)

    def daily(self, window: Window) -> list[Day]:
        """One value per day of the window, a day with no order included."""
        query = within(window, select(OrderModel.placed_on, REVENUE, func.count()))
        with Session(engine) as session:
            found = {
                day: (revenue, orders)
                for day, revenue, orders in session.exec(query.group_by(OrderModel.placed_on))
            }
        days = (window.first + timedelta(days=n) for n in range(window.days))
        return [Day(day, *found.get(day, (0, 0))) for day in days]

    def channels(self, window: Window) -> list[Share]:
        """Every channel, the chosen one or not, so the page can compare them."""
        query = within(window, select(OrderModel.channel, REVENUE, UNITS), by_channel=False)
        with Session(engine) as session:
            found = {
                name: (revenue, units)
                for name, revenue, units in session.exec(query.group_by(OrderModel.channel))
            }
        return [Share(name, *found.get(name, (0, 0))) for name in CHANNELS]

    def products(self, window: Window, limit: int = 5) -> list[Share]:
        query = within(window, select(OrderModel.product, REVENUE, UNITS))
        query = query.group_by(OrderModel.product).order_by(REVENUE.desc(), OrderModel.product)
        with Session(engine) as session:
            return [Share(*row) for row in session.exec(query.limit(limit))]
