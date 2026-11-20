from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
