"""Sign in and sign out: the session cookie holds the id of the signed-in user."""

from urllib.parse import urlencode

from nexy import useSession
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.services.accounts import authenticate


def go(path: str, error: str = "") -> RedirectResponse:
    """A redirect after a POST (303), with an error for the page to show."""
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"{path}{query}", status_code=303)


@Action
async def sign_in(email: str, password: str) -> RedirectResponse:
    user = authenticate(email, password)
    if user is None:
        # Never which of the two is wrong: that would tell anyone which emails have an account.
        return go("/signin", "Wrong email or password.")
    session = useSession()
    session.clear()
    session["user_id"] = user.id
    return go("/")


@Action
async def sign_out() -> RedirectResponse:
    useSession().clear()
    return go("/signin")
