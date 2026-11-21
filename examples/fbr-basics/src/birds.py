"""The birds of the guide: the data the pages read."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Bird:
    slug: str
    name: str
    latin: str
    note: str


BIRDS = [
    Bird("robin", "European robin", "Erithacus rubecula", "Sings at night under street lights."),
    Bird("wren", "Wren", "Troglodytes troglodytes", "Tiny, loud, and almost always hidden."),
    Bird("swift", "Common swift", "Apus apus", "Can stay in the air for ten months."),
]


def find(slug: str) -> Bird | None:
    return next((bird for bird in BIRDS if bird.slug == slug), None)
