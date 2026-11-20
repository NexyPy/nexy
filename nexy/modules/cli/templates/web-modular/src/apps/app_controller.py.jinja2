from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})


@Controller("/about")
class AboutController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/about_view.nexy")})


@Controller("/todos")
class TodosController:
    async def get(self):
        page = useViews("src/apps/todos/todo_view.nexy")
        return useViews(LAYOUT, context={"children": page})
