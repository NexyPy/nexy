from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    """Someone the studio sends invoices to."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str
