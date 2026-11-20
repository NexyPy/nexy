
from sqlmodel import Field, SQLModel


class TodoModel(SQLModel, table=True):
    __tablename__ = "todos"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
