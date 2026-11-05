from src.content import search_entries


async def GET(lang: str = "en") -> list[dict[str, str | None]]:
    """The search index of one language: the pages a reader of it can open."""
    return search_entries(lang)
