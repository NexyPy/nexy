"""Every read and write of the tasks. The actions of `src/actions/todos.py` call
nothing else."""


from src.models.todo_model import TodoModel


class TodoService:
    @staticmethod
    async def all() -> list[TodoModel]:
        return await TodoModel.all().order_by("id")

    @staticmethod
    async def add(title: str) -> None:
        await TodoModel.create(title=title)

    @staticmethod
    async def toggle(todo_id: int) -> None:
        todo = await TodoModel.get_or_none(id=todo_id)
        if todo:
            todo.done = not todo.done
            await todo.save()

    @staticmethod
    async def rename(todo_id: int, title: str) -> None:
        await TodoModel.filter(id=todo_id).update(title=title)

    @staticmethod
    async def remove(todo_id: int) -> None:
        await TodoModel.filter(id=todo_id).delete()

    @staticmethod
    async def clear_done() -> None:
        await TodoModel.filter(done=True).delete()
