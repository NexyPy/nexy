"""The first route moved from the service to a file of src/routes: GET /api/v2/books.

Same data, a new shape: only the books on the shelf. The old /api/v1/books keeps answering
until every client has moved.
"""

from src.library.catalogue import BOOKS


async def GET() -> list[dict[str, object]]:
    return [book.model_dump() for book in BOOKS if not book.on_loan]
