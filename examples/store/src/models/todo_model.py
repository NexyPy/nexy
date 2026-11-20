from sqlalchemy import Boolean, Column, Integer, String

from src.models import Base


class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    done = Column(Boolean, nullable=False, default=False)
