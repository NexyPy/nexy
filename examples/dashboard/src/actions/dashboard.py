"""The actions the dashboard calls. The pages keep the period, the channel and the page in the URL,
and send them as text, the way the URL holds them: a value the page does not offer falls back."""

from datetime import date

from nexy.decorators import Action
from pydantic import BaseModel

from src.models.order_model import CHANNELS
from src.services import metrics_service as metrics
from src.services.metrics_service import MetricsService
from src.services.order_service import OrderService
from src.services.window import Window, window_of


class Totals(BaseModel):
    revenue_cents: int
    orders: int
    units: int
    average_cents: int


class Day(BaseModel):
    day: date
    revenue_cents: int
    orders: int


class Share(BaseModel):
    name: str
    revenue_cents: int
    units: int


class Period(BaseModel):
    days: int
    channel: str  # "" for every channel
    first: date
    last: date


class Overview(BaseModel):
    period: Period
    totals: Totals
    before: Totals  # the same number of days just before: what a change is measured against
    daily: list[Day]
    channels: list[Share]
    best: list[Share]


class Products(BaseModel):
    period: Period
    products: list[Share]


class Order(BaseModel):
    id: int
    placed_on: date
    channel: str
    region: str
    product: str
    units: int
    revenue_cents: int


class Orders(BaseModel):
    channel: str
    rows: list[Order]
    number: int
    pages: int
    total: int


def totals_of(found: metrics.Totals) -> Totals:
    return Totals(
        revenue_cents=found.revenue_cents,
        orders=found.orders,
        units=found.units,
        average_cents=found.average_cents,
    )


def share_of(found: metrics.Share) -> Share:
    return Share(name=found.name, revenue_cents=found.revenue_cents, units=found.units)


def period_of(days: str, channel: str) -> Window:
    return window_of(days, channel, MetricsService().as_of())


def described(window: Window) -> Period:
    return Period(days=window.days, channel=window.channel, first=window.first, last=window.last)


def page_number(text: str) -> int:
    """Compared as text: int() would take a digit such as "²" or a number 5000 digits long."""
    return int(text) if text.isascii() and text.isdigit() and len(text) <= 6 else 1


@Action
def overview(days: str = "30", channel: str = "") -> Overview:
    """What the overview shows: totals against the period before, a value per day, the channels."""
    found, window = MetricsService(), period_of(days, channel)
    return Overview(
        period=described(window),
        totals=totals_of(found.totals(window)),
        before=totals_of(found.totals(window.before())),
        daily=[
            Day(day=d.day, revenue_cents=d.revenue_cents, orders=d.orders)
            for d in found.daily(window)
        ],
        channels=[share_of(share) for share in found.channels(window)],
        best=[share_of(share) for share in found.products(window)],
    )


@Action
def products(days: str = "30", channel: str = "") -> Products:
    """Every product sold in the period, the best seller first."""
    window = period_of(days, channel)
    found = MetricsService().products(window, limit=1000)
    return Products(period=described(window), products=[share_of(share) for share in found])


@Action
def orders(channel: str = "", page: str = "1") -> Orders:
    """One page of orders, newest first. A page past the last gives the last."""
    found = OrderService().page(channel, page_number(page))
    rows = [Order.model_validate(row, from_attributes=True) for row in found.rows]
    known = channel if channel in CHANNELS else ""
    return Orders(
        channel=known, rows=rows, number=found.number, pages=found.pages, total=found.total
    )
