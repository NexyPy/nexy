"""The results the search box shows as you type: the same search as the /search page, as JSON."""

from nexy.http import JSONResponse, Request

from src.docs.search import search

LONGEST_QUERY = 100  # longer than any question typed in a search box


def GET(request: Request) -> JSONResponse:
    query = request.query_params.get("q", "")[:LONGEST_QUERY]
    hits = [
        {"title": hit.title, "heading": hit.heading, "url": hit.url, "snippet": hit.snippet}
        for hit in search(query)
    ]
    return JSONResponse(hits)
