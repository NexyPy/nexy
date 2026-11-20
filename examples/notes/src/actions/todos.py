"""The actions the /todos page calls. The tasks live on the Python server, in the `todos` table.

Each action is a POST endpoint, typed in `@nexy/actions`, so the page calls them like functions.
Every one answers with the whole list: the page shows what the server holds, never a guess.
"""

from pydantic import BaseModel

from nexy.decorators import Action
from src.configs.db import arun
from src.services.todo_service import TodoService

MAX_TITLE = 200


class Todo(BaseModel):
    id: int
    title: str
    done: bool


class Board(BaseModel):
    items: list[Todo]
    note: str = ""  # why the last change was refused; empty when it was made


def problem(title: str) -> str:
    """What is wrong with a title, or an empty string."""
    if not title:
        return "Write what there is to do."
    if len(title) > MAX_TITLE:
        return f"Keep it under {MAX_TITLE} characters."
    return ""


# Tortoise runs on a loop of its own (src/configs/db.py): `arun` waits for it without blocking.


async def board(note: str = "") -> Board:
    items = [Todo(id=t.id, title=t.title, done=t.done) for t in await arun(TodoService.all())]
    return Board(items=items, note=note)


@Action
async def todos() -> Board:
    """Every task, oldest first."""
    return await board()


@Action
async def add_todo(title: str) -> Board:
    title = title.strip()
    note = problem(title)
    if not note:
        await arun(TodoService.add(title))
    return await board(note)


@Action
async def toggle_todo(todo_id: int) -> Board:
    await arun(TodoService.toggle(todo_id))
    return await board()


@Action
async def rename_todo(todo_id: int, title: str) -> Board:
    title = title.strip()
    note = problem(title)
    if not note:
        await arun(TodoService.rename(todo_id, title))
    return await board(note)


@Action
async def delete_todo(todo_id: int) -> Board:
    await arun(TodoService.remove(todo_id))
    return await board()


@Action
async def clear_done() -> Board:
    """Delete every task that is done."""
    await arun(TodoService.clear_done())
    return await board()
