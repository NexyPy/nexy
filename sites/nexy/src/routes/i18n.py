from src.content import i18n_payload


async def GET() -> dict[str, object]:
    return i18n_payload()
