"""Who waits for Beacon. The form of the page and its fallback without JavaScript both land here."""

import re

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.configs.db import engine
from src.models.subscriber_model import LONGEST_EMAIL, SubscriberModel

# One "@", something on each side, a dot in the domain, no space and no angle bracket. The real
# test of an address is the email that will reach it; this one only stops a typing mistake.
_EMAIL = re.compile(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>.]+")

# What the page says after each outcome. "joined" is also the answer to an address already on the
# list: the form does not tell anyone whether an address signed up before.
MESSAGES = {
    "joined": "You are on the list. We will write once, when Beacon opens.",
    "empty": "Write your email to join the list.",
    "long": "That email is longer than an address can be.",
    "invalid": "That does not look like an email. Check it and try again.",
}


def clean(email: str) -> str:
    return email.strip().lower()


def problem(email: str) -> str:
    """The key of what is wrong with a cleaned email, or "" when it can join."""
    if not email:
        return "empty"
    if len(email) > LONGEST_EMAIL:
        return "long"
    return "" if _EMAIL.fullmatch(email) else "invalid"


def store(email: str) -> None:
    """Add `email` once: an address already on the list stays as it was."""
    with Session(engine) as session:
        session.add(SubscriberModel(email=email))
        try:
            session.commit()
        except IntegrityError:
            session.rollback()


def join(email: str) -> str:
    """Put `email` on the list. Returns the key of the message the page shows."""
    email = clean(email)
    found = problem(email)
    if found:
        return found
    store(email)
    return "joined"
