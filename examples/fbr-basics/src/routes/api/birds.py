"""A Python file in src/routes answers with what its function returns: here, JSON at /api/birds."""

from dataclasses import asdict

from src.birds import BIRDS


def GET() -> list[dict[str, str]]:
    return [asdict(bird) for bird in BIRDS]
