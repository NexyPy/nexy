from src.content import search_entries


async def GET() -> list[dict[str, str | None]]:
    return search_entries()
