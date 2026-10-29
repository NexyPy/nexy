from nexy.http import Response
from src.content import markdown_source


async def GET(slug: str = "") -> Response:
    """The Markdown of one page, as it is written in docs/: what the copy button copies."""
    return Response(markdown_source(slug), media_type="text/markdown; charset=utf-8")
