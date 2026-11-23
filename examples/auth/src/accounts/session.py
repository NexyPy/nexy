"""Who is signed in: the id of the account, in the signed session cookie."""

from nexy import useSession

from src.accounts.store import Account, find

KEY = "account_id"


def current() -> Account | None:
    """The signed-in account, or None. An id whose account was deleted counts as signed out."""
    account_id = useSession().get(KEY)
    return find(account_id) if isinstance(account_id, int) else None


def sign_in_as(account: Account) -> None:
    """Start a new session for `account`: nothing of the previous one is kept."""
    session = useSession()
    session.clear()
    session[KEY] = account.id


def safe_then(path: str, default: str = "/account") -> str:
    """Where to go after signing in. Only a path of this site: `//evil.example` or
    `https://evil.example` would send the visitor to another one (an open redirect)."""
    if not path.startswith("/") or path.startswith(("//", "/\\")) or len(path) > 200:
        return default
    return path
