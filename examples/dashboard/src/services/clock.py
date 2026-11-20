from datetime import UTC, date, datetime


def today() -> date:
    """The date of today, in UTC: the one every status and total is worked out on."""
    return datetime.now(UTC).date()
