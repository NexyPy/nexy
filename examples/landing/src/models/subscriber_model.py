"""The people waiting for Beacon: one row per email, the first time it was given."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

LONGEST_EMAIL = 254  # the longest address SMTP carries


def now() -> datetime:
    return datetime.now(UTC)


class SubscriberModel(SQLModel, table=True):
    __tablename__ = "subscribers"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=LONGEST_EMAIL)
    joined_at: datetime = Field(default_factory=now)
