"""Three levels of access on one API: anyone reads, a key writes, an editor publishes."""

from dataclasses import asdict
from typing import Any

from fastapi import HTTPException
from nexy.decorators import Controller, UseGuard, UseResponse

from src.apps.guards import require_editor, require_key
from src.apps.stories import store


def _found(slug: str, published: bool) -> store.Story:
    story = store.STORIES.get(slug)
    if story is None or story.published != published:
        raise HTTPException(404, "No such story.")
    return story


@Controller("/stories")
class StoriesController:
    async def get(self) -> list[dict[str, Any]]:
        """Public: the published stories."""
        return [asdict(story) for story in store.published()]


@Controller("/stories/{slug}")
class StoryController:
    async def get(self, slug: str) -> dict[str, Any]:
        """Public: one published story. A draft answers 404, as if it did not exist."""
        return asdict(_found(slug, published=True))

    @UseGuard(require_editor)  # on this method only: reading stays public
    @UseResponse(status_code=204)
    async def delete(self, slug: str) -> None:
        del store.STORIES[_found(slug, published=True).slug]


@Controller("/drafts")
@UseGuard(require_key)  # on the controller: every method needs a key
class DraftsController:
    async def get(self) -> list[dict[str, Any]]:
        return [asdict(story) for story in store.drafts()]

    @UseResponse(status_code=201)
    async def post(self, new: store.NewStory) -> dict[str, Any]:
        story = store.add(new)
        if story is None:
            raise HTTPException(409, "A story already has this title.")
        return asdict(story)


@Controller("/drafts/{slug}/publish")
@UseGuard(require_editor)
class PublishController:
    async def post(self, slug: str) -> dict[str, Any]:
        story = _found(slug, published=False)
        story.published = True
        return asdict(story)
