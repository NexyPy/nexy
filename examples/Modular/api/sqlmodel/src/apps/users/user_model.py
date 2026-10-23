
from sqlmodel import SQLModel, Field

class UserModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
