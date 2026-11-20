from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """A person who can sign in. The table keeps a hash of the password, never the password."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
