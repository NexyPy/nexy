"""Sign up, sign in, sign out, change the password. The forms post here without JavaScript, and
every action answers with a redirect: after a POST, the browser lands on a page it can reload."""

from urllib.parse import urlencode

from nexy import useSession
from nexy.decorators import Action
from nexy.http import RedirectResponse

from src.accounts import store, throttle
from src.accounts.session import current, safe_then, sign_in_as

LONGEST_EMAIL = 254


def go(path: str, **query: str) -> RedirectResponse:
    kept = {key: value for key, value in query.items() if value}
    return RedirectResponse(f"{path}?{urlencode(kept)}" if kept else path, status_code=303)


@Action
def sign_up(email: str, password: str, then: str = "") -> RedirectResponse:
    account, problem = store.create(email, password)
    if account is None:
        return go("/signup", error=problem, email=email.strip()[:LONGEST_EMAIL], then=then)
    sign_in_as(account)
    return go(safe_then(then))


@Action
def sign_in(email: str, password: str, then: str = "") -> RedirectResponse:
    key = email.strip().lower()[:LONGEST_EMAIL]
    if throttle.blocked(key):  # the password is not even checked
        return go("/signin", error="slow", email=key, then=then)
    account = store.authenticate(key, password)
    if account is None:
        throttle.failed(key)
        return go("/signin", error="wrong", email=key, then=then)
    throttle.succeeded(key)
    sign_in_as(account)
    return go(safe_then(then))


@Action
def sign_out() -> RedirectResponse:
    useSession().clear()
    return go("/", done="out")


@Action
def change_password(current_password: str, new_password: str) -> RedirectResponse:
    account = current()
    if account is None:
        return go("/signin", error="signin", then="/account")
    problem = store.change_password(account.id, current_password, new_password)
    return go("/account", error=problem) if problem else go("/account", done="password")
