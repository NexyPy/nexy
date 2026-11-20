"""The figures of the overview: totals, revenue by month, the latest invoices, each customer."""

from dataclasses import dataclass
from datetime import date

from sqlmodel import Session, select

from src.configs import db
from src.models.customer import Customer
from src.models.invoice import Invoice, status
from src.services import clock


@dataclass(frozen=True)
class Totals:
    collected_this_month: int
    outstanding: int
    overdue: int
    overdue_count: int
    customers: int


@dataclass(frozen=True)
class CustomerLine:
    name: str
    email: str
    invoices: int
    paid: int
    outstanding: int


def _all() -> tuple[list[Invoice], list[Customer]]:
    with Session(db.engine) as session:
        return list(session.exec(select(Invoice)).all()), list(session.exec(select(Customer)).all())


def totals(today: date | None = None) -> Totals:
    today = today or clock.today()
    invoices, customers = _all()
    month = (today.year, today.month)
    collected = [i for i in invoices if i.paid_on and (i.paid_on.year, i.paid_on.month) == month]
    unpaid = [i for i in invoices if i.paid_on is None]
    late = [i for i in unpaid if status(i, today) == "overdue"]
    return Totals(
        sum(i.amount_cents for i in collected),
        sum(i.amount_cents for i in unpaid),
        sum(i.amount_cents for i in late),
        len(late),
        len(customers),
    )


def _months(today: date, count: int) -> list[tuple[int, int]]:
    index = today.year * 12 + today.month - 1
    return [divmod(index - back, 12) for back in range(count - 1, -1, -1)]


def revenue(today: date | None = None, count: int = 12) -> list[dict[str, object]]:
    """The money collected in each of the last `count` months, oldest first."""
    today = today or clock.today()
    invoices, _ = _all()
    paid: dict[tuple[int, int], int] = {}
    for invoice in invoices:
        if invoice.paid_on:
            key = (invoice.paid_on.year, invoice.paid_on.month - 1)
            paid[key] = paid.get(key, 0) + invoice.amount_cents
    return [
        {"label": date(year, month + 1, 1).strftime("%b %Y"), "cents": paid.get((year, month), 0)}
        for year, month in _months(today, count)
    ]


def customers() -> list[CustomerLine]:
    """Each customer with its invoices, what it paid and what it still owes; who owes most first."""
    invoices, people = _all()
    lines = []
    for person in people:
        own = [i for i in invoices if i.customer_id == person.id]
        paid = sum(i.amount_cents for i in own if i.paid_on)
        owed = sum(i.amount_cents for i in own if not i.paid_on)
        lines.append(CustomerLine(person.name, person.email, len(own), paid, owed))
    return sorted(lines, key=lambda line: (-line.outstanding, line.name))
