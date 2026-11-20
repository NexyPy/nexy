"""Numbers as the pages show them: money in dollars, changes in percent, days in words."""

from datetime import date


def money(cents: int) -> str:
    """Whole dollars, for a total: its cents are noise."""
    return f"${cents // 100:,}"


def exact(cents: int) -> str:
    """Dollars and cents, for one order or an average."""
    return f"${cents // 100:,}.{cents % 100:02d}"


def change(now: int, before: int) -> tuple[str, str]:
    """The change from `before` to `now`, and its direction: "up", "down" or "flat"."""
    if before == 0:
        return ("new", "up") if now else ("no change", "flat")
    percent = (now - before) / before * 100
    if abs(percent) < 0.05:
        return "no change", "flat"
    return f"{percent:+.1f}%", "up" if percent > 0 else "down"


def day(value: date) -> str:
    return f"{value:%b} {value.day}, {value.year}"


def span(first: date, last: date) -> str:
    """Two days as a range, the year written once when they share it."""
    if first.year == last.year:
        return f"{first:%b} {first.day} to {last:%b} {last.day}, {last.year}"
    return f"{day(first)} to {day(last)}"
