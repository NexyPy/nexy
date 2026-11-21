import os
import secrets
from pathlib import Path

from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


def session_secret() -> str:
    """The key that signs the session cookie. Anyone who knows it can sign in as anyone.

    In production, set SESSION_SECRET. Without it, a random key is made once and kept in
    `session.key` (ignored by git), so the example runs with no setup and sessions survive a restart.
    """
    if secret := os.environ.get("SESSION_SECRET"):
        return secret
    kept = Path("session.key")
    if not kept.exists():
        kept.write_text(secrets.token_urlsafe(32), encoding="utf-8")
    return kept.read_text(encoding="utf-8").strip()


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useTitle = "Kestrel"
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True  # the toolbar of `nexy dev` on every page; False removes it
    # A signed cookie the browser never sends with a POST from another site ("lax"). Behind HTTPS,
    # set SECURE_COOKIES=1: the cookie is then never sent over plain HTTP.
    useSession = {
        "secret_key": session_secret(),
        "same_site": "lax",
        "https_only": os.environ.get("SECURE_COOKIES") == "1",
    }
