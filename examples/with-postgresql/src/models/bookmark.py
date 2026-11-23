from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Bookmark(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200, index=True)
    url: str = Field(max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
