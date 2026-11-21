"""A Python route answers JSON, not a page: it is not in the sitemap either."""


def GET() -> dict[str, str]:
    return {"opens": "07:00", "closes": "14:00"}
