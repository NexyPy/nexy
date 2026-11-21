"""Every read and write of the tasks. The actions of `src/actions/todos.py` call
nothing else."""


from dataclasses import dataclass


@dataclass
class TodoModel:
    id: int
    title: str
    done: bool = False


# No database in this project: the tasks are a list the server keeps while it runs.
TODOS = [
    TodoModel(1, "Read src/actions/todos.py: the page calls them"),
    TodoModel(2, "Add a task with the field above"),
    TodoModel(3, "Tick a task to mark it done", done=True),
]


def _find(todo_id: int) -> TodoModel | None:
    return next((todo for todo in TODOS if todo.id == todo_id), None)


class TodoService:
    @staticmethod
    def all() -> list[TodoModel]:
        return list(TODOS)

    @staticmethod
    def add(title: str) -> None:
        TODOS.append(TodoModel(max((todo.id for todo in TODOS), default=0) + 1, title))

    @staticmethod
    def toggle(todo_id: int) -> None:
        if todo := _find(todo_id):
            todo.done = not todo.done

    @staticmethod
    def rename(todo_id: int, title: str) -> None:
        if todo := _find(todo_id):
            todo.title = title

    @staticmethod
    def remove(todo_id: int) -> None:
        TODOS[:] = [todo for todo in TODOS if todo.id != todo_id]

    @staticmethod
    def clear_done() -> None:
        TODOS[:] = [todo for todo in TODOS if not todo.done]
