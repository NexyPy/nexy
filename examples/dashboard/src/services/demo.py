"""Demo data, written once into an empty database so the dashboard has something to show."""

import random
from datetime import date, timedelta

from sqlmodel import Session, select

from src.configs import db
from src.models.customer import Customer
from src.models.invoice import Invoice
from src.models.user import User
from src.services import clock
from src.services.passwords import hash_password

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo-password"
CUSTOMERS = [
    ("Northwind Studio", "billing@northwind.example"),
    ("Blue Harbor Cafe", "accounts@blueharbor.example"),
    ("Kestrel Labs", "finance@kestrel.example"),
    ("Maple and Pine", "hello@mapleandpine.example"),
    ("Orbit Bikes", "billing@orbitbikes.example"),
    ("Quiet Room Books", "orders@quietroom.example"),
    ("Saltwater Yoga", "team@saltwater.example"),
    ("Tandem Architects", "office@tandem.example"),
]


def _invoice(rng: random.Random, customer: Customer, today: date) -> Invoice:
    issued = today - timedelta(days=rng.randrange(0, 365))
    paid = issued + timedelta(days=rng.randint(3, 45))
    is_paid = paid <= today and rng.random() < 0.88
    return Invoice(
        number="",
        customer_id=customer.id or 0,
        amount_cents=rng.randrange(400, 6000) * 100,
        issued=issued,
        due=issued + timedelta(days=30),
        paid_on=paid if is_paid else None,
    )


def seed(session: Session, today: date) -> None:
    """One demo user, eight customers, ninety invoices of the last twelve months."""
    rng = random.Random(7)
    session.add(User(email=DEMO_EMAIL, name="Demo", password_hash=hash_password(DEMO_PASSWORD)))
    customers = [Customer(name=name, email=email) for name, email in CUSTOMERS]
    session.add_all(customers)
    session.flush()
    invoices = sorted(
        (_invoice(rng, rng.choice(customers), today) for _ in range(90)),
        key=lambda invoice: invoice.issued,
    )
    for index, invoice in enumerate(invoices, start=1):
        invoice.number = f"INV-{index:04d}"
    session.add_all(invoices)
    session.commit()


def prepare(today: date | None = None) -> None:
    """Create the tables, and fill them with the demo data the first time."""
    db.create_tables()
    with Session(db.engine) as session:
        if session.exec(select(User)).first() is None:
            seed(session, today or clock.today())
