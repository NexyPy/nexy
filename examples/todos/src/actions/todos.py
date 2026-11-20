"""The actions the page calls. Each one answers with the whole list, so the page never guesses.

Every action is a POST endpoint, typed in `@nexy/actions`: the page calls them like functions.
They are plain functions, so Nexy runs them in a thread and a query never holds up other requests.
"""

from pydantic import BaseModel

from nexy.decorators import Action
from src.services import todos


class Item(BaseModel):
    id: int
    title: str
    done: bool


class Board(BaseModel):
    items: list[Item]
    note: str = ""  # why the last change was refused; empty when it was saved


def _board(note: str = "") -> Board:
    items = [Item(id=t.id or 0, title=t.title, done=t.done) for t in todos.all_todos()]
    return Board(items=items, note=note)


@Action
def list_todos() -> Board:
    """The list as it is in the database."""
    return _board()


@Action
def add_todo(title: str) -> Board:
    title = title.strip()
    note = todos.problem(title)
    if not note:
        todos.add(title)
    return _board(note)


@Action
def toggle_todo(todo_id: int) -> Board:
    todos.toggle(todo_id)
    return _board()


@Action
def rename_todo(todo_id: int, title: str) -> Board:
    title = title.strip()
    note = todos.problem(title)
    if not note:
        todos.rename(todo_id, title)
    return _board(note)


@Action
def delete_todo(todo_id: int) -> Board:
    todos.remove(todo_id)
    return _board()


@Action
def clear_completed() -> Board:
    todos.clear_done()
    return _board()
