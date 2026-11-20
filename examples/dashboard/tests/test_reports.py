from conftest import TODAY
from sqlmodel import Session, col, select
from src.configs import db
from src.models.invoice import Invoice
from src.services.invoices import search
from src.services.reports import customers, revenue, totals


def test_revenue_covers_twelve_months():
    assert len(revenue(TODAY)) == 12


def test_revenue_ends_with_this_month():
    assert revenue(TODAY)[-1]["label"] == "Nov 2026"


def test_revenue_starts_eleven_months_before():
    assert revenue(TODAY)[0]["label"] == "Dec 2025"


def test_outstanding_is_every_unpaid_invoice():
    with Session(db.engine) as session:
        unpaid = session.exec(select(Invoice).where(col(Invoice.paid_on).is_(None))).all()
    assert totals(TODAY).outstanding == sum(invoice.amount_cents for invoice in unpaid)


def test_overdue_counts_the_overdue_invoices():
    assert totals(TODAY).overdue_count == search(wanted="overdue", today=TODAY).total


def test_this_month_matches_the_last_bar_of_the_chart():
    assert totals(TODAY).collected_this_month == revenue(TODAY)[-1]["cents"]


def test_every_customer_is_listed():
    assert len(customers()) == totals(TODAY).customers


def test_who_owes_most_comes_first():
    owed = [line.outstanding for line in customers()]
    assert owed == sorted(owed, reverse=True)
