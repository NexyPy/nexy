"""Every read and write of the todo list goes through here."""

from sqlmodel import Session, col, delete, select

from src.configs.db import create_tables, engine
from src.models.todo import Todo

LONGEST = 200

create_tables()


def problem(title: str) -> str:
    """Why a title cannot be saved, or an empty string."""
    if not title:
        return "Write what there is to do."
    if len(title) > LONGEST:
        return f"Keep it under {LONGEST} characters."
    return ""


def all_todos() -> list[Todo]:
    """The whole list, oldest first."""
    with Session(engine) as session:
        return list(session.exec(select(Todo).order_by(col(Todo.created_at))))


def add(title: str) -> None:
    with Session(engine) as session:
        session.add(Todo(title=title))
        session.commit()


def toggle(todo_id: int) -> None:
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if todo is not None:
            todo.done = not todo.done
            session.commit()


def rename(todo_id: int, title: str) -> None:
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if todo is not None:
            todo.title = title
            session.commit()


def remove(todo_id: int) -> None:
    with Session(engine) as session:
        session.exec(delete(Todo).where(col(Todo.id) == todo_id))
        session.commit()


def clear_done() -> None:
    with Session(engine) as session:
        session.exec(delete(Todo).where(col(Todo.done)))
        session.commit()
