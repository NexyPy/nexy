from nexy.decorators import Controller
from nexy.hooks import useViews

from src.apps.stories import store

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        page = useViews("src/apps/app_view.nexy", context={"stories": store.published()})
        return useViews(LAYOUT, context={"children": page})
