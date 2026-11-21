"""The guards of the newsroom API. A guard is a FastAPI dependency: it reads what it needs from
the request and raises to refuse the call. `@UseGuard(...)` puts one on a controller or a method."""

import hmac
import os

from fastapi import Depends, Header, HTTPException


def _keys() -> dict[str, str]:
    """API key to role, from NEWSROOM_KEYS="key:role,key:role". The two demo keys are for a first
    run only: set NEWSROOM_KEYS to your own before the API leaves your machine."""
    raw = os.environ.get("NEWSROOM_KEYS", "demo-writer-key:writer,demo-editor-key:editor")
    pairs = (item.strip().rpartition(":") for item in raw.split(",") if item.strip())
    return {key: role for key, _, role in pairs if key}


def require_key(x_api_key: str = Header("")) -> str:
    """Any known key: 401 without one. Each key is compared in constant time, so the time of the
    answer does not tell how much of a guess was right."""
    role = next(
        (role for key, role in _keys().items() if hmac.compare_digest(key, x_api_key)), None
    )
    if role is None:
        raise HTTPException(401, "Send a valid X-Api-Key header.")
    return role


def require_editor(role: str = Depends(require_key)) -> str:
    """An editor's key: 401 without a key, 403 with a writer's. Built on `require_key`."""
    if role != "editor":
        raise HTTPException(403, "Only an editor can do this.")
    return role
