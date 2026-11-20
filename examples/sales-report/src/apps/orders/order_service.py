"""The list of orders, newest first, one page at a time."""

from dataclasses import dataclass

from nexy.decorators import Injectable
from sqlalchemy import func
from sqlmodel import Session, select

from src.apps.orders.order_model import CHANNELS, OrderModel
from src.configs.db import engine

PAGE_SIZE = 20


@dataclass(frozen=True)
class Page:
    rows: list[OrderModel]
    number: int  # from 1
    pages: int
    total: int


def filtered(query, channel: str):
    return query.where(OrderModel.channel == channel) if channel in CHANNELS else query


@Injectable()
class OrderService:
    def page(self, channel: str = "", number: int = 1) -> Page:
        """A page past the last one gives the last one; a page before the first gives the first."""
        with Session(engine) as session:
            total = session.exec(
                filtered(select(func.count()).select_from(OrderModel), channel)
            ).one()
            pages = max(1, -(-total // PAGE_SIZE))
            number = min(max(number, 1), pages)
            query = filtered(select(OrderModel), channel)
            query = query.order_by(OrderModel.placed_on.desc(), OrderModel.id.desc())
            rows = list(session.exec(query.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
        return Page(rows, number, pages, total)
