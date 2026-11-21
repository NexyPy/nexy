from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse

from src.services import bookmarks


@Action
def add_bookmark(title: str, url: str) -> RedirectResponse:
    """The form posts here without JavaScript; the answer is a redirect to a page that reloads."""
    problem = bookmarks.problem(title, url)
    if problem:
        kept = urlencode({"error": problem, "title": title[:200], "url": url[:2000]})
        return RedirectResponse(f"/?{kept}", status_code=303)
    bookmarks.add(title, url)
    return RedirectResponse("/?added=1", status_code=303)
