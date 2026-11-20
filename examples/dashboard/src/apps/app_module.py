from nexy.decorators import Module
from .app_controller import (
    AboutController,
    AppController,
    TodosController,
)


@Module()
class AppModule:
    controllers = [
        AppController,
        AboutController,
        TodosController,
    ]
