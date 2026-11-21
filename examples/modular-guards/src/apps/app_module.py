from nexy.decorators import Module

from src.apps.app_controller import AppController
from src.apps.stories.stories_module import StoriesModule


@Module()
class AppModule:
    controllers = (AppController,)
    imports = (StoriesModule,)  # mounted as a sub-router, with its own /api prefix
