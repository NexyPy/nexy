from nexy.decorators import Module

from src.apps.stories.stories_controller import (
    DraftsController,
    PublishController,
    StoriesController,
    StoryController,
)


@Module(prefix="/api")
class StoriesModule:
    controllers = (StoriesController, StoryController, DraftsController, PublishController)
