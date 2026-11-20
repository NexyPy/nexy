
from sqlalchemy import Boolean, Column, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    # Migrations can only drop or rebuild a constraint that has a name: SQLite batch mode refuses
    # an unnamed one. The convention names the ones the models leave unnamed, such as a foreign key.
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    done = Column(Boolean, nullable=False, default=False)
