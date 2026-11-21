"""The departures board: what a slow source would give, and how many times it was asked."""

import itertools
from datetime import UTC, datetime

DEPARTURES = [
    ("08:12", "Halden", "On time"),
    ("08:27", "Moss", "On time"),
    ("08:40", "Fredrikstad", "Delayed 5 min"),
    ("09:05", "Sarpsborg", "On time"),
]

_renders = itertools.count(1)


def render_number() -> int:
    """1 for the first render of the page, 2 for the next: the page calls it once per render."""
    return next(_renders)


def now() -> str:
    return datetime.now(UTC).strftime("%H:%M:%S UTC")
