from datetime import date

from sqlmodel import Field, SQLModel


class Invoice(SQLModel, table=True):
    """One invoice. Its status is worked out from the dates: see `status()`."""

    id: int | None = Field(default=None, primary_key=True)
    number: str = Field(unique=True, index=True)
    customer_id: int = Field(foreign_key="customer.id", index=True)
    amount_cents: int
    issued: date
    due: date
    paid_on: date | None = None


def status(invoice: Invoice, today: date) -> str:
    """`paid` once paid, `overdue` when unpaid past its due date, `pending` before."""
    if invoice.paid_on is not None:
        return "paid"
    return "overdue" if invoice.due < today else "pending"
