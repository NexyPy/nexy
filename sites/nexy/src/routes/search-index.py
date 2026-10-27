from src.content import search_entries


async def GET() -> list[dict[str, str]]:
    return search_entries()
