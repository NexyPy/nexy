"""Every read and write of the tasks. The actions of `src/actions/todos.py` call
nothing else."""


from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.configs.db import engine
from src.models.todo_model import TodoModel


class TodoService:
    @staticmethod
    def all() -> list[TodoModel]:
        with Session(engine) as session:
            return list(session.scalars(select(TodoModel).order_by(TodoModel.id)).all())

    @staticmethod
    def add(title: str) -> None:
        with Session(engine) as session:
            session.add(TodoModel(title=title, done=False))
            session.commit()

    @staticmethod
    def toggle(todo_id: int) -> None:
        with Session(engine) as session:
            todo = session.get(TodoModel, todo_id)
            if todo:
                todo.done = not todo.done
                session.commit()

    @staticmethod
    def rename(todo_id: int, title: str) -> None:
        with Session(engine) as session:
            todo = session.get(TodoModel, todo_id)
            if todo:
                todo.title = title
                session.commit()

    @staticmethod
    def remove(todo_id: int) -> None:
        with Session(engine) as session:
            session.execute(delete(TodoModel).where(TodoModel.id == todo_id))
            session.commit()

    @staticmethod
    def clear_done() -> None:
        with Session(engine) as session:
            session.execute(delete(TodoModel).where(TodoModel.done))
            session.commit()
