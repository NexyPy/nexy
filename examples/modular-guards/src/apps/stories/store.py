"""The stories of the newsroom, kept in memory: a sample needs no database."""

import re
from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass
class Story:
    slug: str
    title: str
    body: str
    published: bool = False


class NewStory(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=5000)


STORIES: dict[str, Story] = {}


def reset() -> None:
    STORIES.clear()
    STORIES["harbour-reopens"] = Story(
        "harbour-reopens", "The harbour reopens", "Boats are back from Monday.", published=True
    )
    STORIES["bridge-vote"] = Story("bridge-vote", "Bridge vote next week", "The council meets.")


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "story"


def add(new: NewStory) -> Story | None:
    """A new draft, or None when a story already has its address."""
    slug = slugify(new.title)
    if slug in STORIES:
        return None
    STORIES[slug] = Story(slug, new.title, new.body)
    return STORIES[slug]


def published() -> list[Story]:
    return [story for story in STORIES.values() if story.published]


def drafts() -> list[Story]:
    return [story for story in STORIES.values() if not story.published]


reset()
