"""Every read and write of the invoices: search, one invoice, totals, revenue by month."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, or_
from sqlmodel import Session, col, select

from src.configs import db
from src.models.customer import Customer
from src.models.invoice import Invoice, status
from src.services import clock

PAGE_SIZE = 10
STATUSES = ("paid", "pending", "overdue")


@dataclass(frozen=True)
class Row:
    id: int
    number: str
    customer: str
    amount_cents: int
    issued: date
    due: date
    paid_on: date | None
    status: str


@dataclass(frozen=True)
class Page:
    rows: list[Row]
    number: int
    pages: int
    total: int


def _row(invoice: Invoice, customer: Customer, today: date) -> Row:
    return Row(
        invoice.id or 0,
        invoice.number,
        customer.name,
        invoice.amount_cents,
        invoice.issued,
        invoice.due,
        invoice.paid_on,
        status(invoice, today),
    )


def _with_status(query, wanted: str, today: date):  # type: ignore[no-untyped-def]
    unpaid = col(Invoice.paid_on).is_(None)
    if wanted == "paid":
        return query.where(col(Invoice.paid_on).is_not(None))
    if wanted == "overdue":
        return query.where(unpaid, col(Invoice.due) < today)
    if wanted == "pending":
        return query.where(unpaid, col(Invoice.due) >= today)
    return query


def _matching(text: str, wanted: str, today: date):  # type: ignore[no-untyped-def]
    query = select(Invoice, Customer).join(Customer)
    if text.strip():
        like = f"%{text.strip()}%"
        query = query.where(or_(col(Invoice.number).ilike(like), col(Customer.name).ilike(like)))
    return _with_status(query, wanted, today)


def search(text: str = "", wanted: str = "", number: int = 1, today: date | None = None) -> Page:
    """One page of the invoices whose number or customer holds `text`, newest first."""
    today = today or clock.today()
    query = _matching(text, wanted, today)
    with Session(db.engine) as session:
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        pages = max(1, -(-total // PAGE_SIZE))
        number = min(max(1, number), pages)
        ordered = query.order_by(col(Invoice.issued).desc(), col(Invoice.id).desc())
        found = session.exec(ordered.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE)).all()
    return Page([_row(i, c, today) for i, c in found], number, pages, total)


def find(invoice_id: int, today: date | None = None) -> tuple[Row, str] | None:
    """One invoice and the email of its customer, or None."""
    with Session(db.engine) as session:
        invoice = session.get(Invoice, invoice_id)
        if invoice is None:
            return None
        customer = session.get(Customer, invoice.customer_id)
    assert customer is not None  # nosec B101 - a foreign key, the database keeps it
    return _row(invoice, customer, today or clock.today()), customer.email


def mark_paid(invoice_id: int, today: date | None = None) -> bool:
    """Record the payment of an unpaid invoice today; False when there is nothing to pay."""
    with Session(db.engine) as session:
        invoice = session.get(Invoice, invoice_id)
        if invoice is None or invoice.paid_on is not None:
            return False
        invoice.paid_on = today or clock.today()
        session.add(invoice)
        session.commit()
    return True
