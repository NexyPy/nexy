"""Whether this process is the application served by `nexy dev`, and on which Vite port.

Kept apart from the proxy so that a production worker can ask without loading httpx and
websockets, which only the dev proxy uses.
"""

from __future__ import annotations

import os
from pathlib import Path

from nexy.core.config import Config
from nexy.helpers.server.ports import get_client_port

# Set by `nexy dev` for the application process it serves. Nothing else sets
# it, so user test suites and `nexy start` never route through the proxy.
DEV_ENV_VAR = "NEXY_DEV_SERVER"


def vite_proxy_port() -> int | None:
    """Return the loopback Vite port to proxy, or None when not in dev mode.

    Dev mode is opt-in through the environment so that importing the app in a
    user's test suite or under ``nexy start`` never touches a Vite port.
    """
    if os.environ.get(DEV_ENV_VAR) != "1":
        return None
    if not os.path.exists("vite.config.ts"):
        return None
    if Path("__nexy__/nexy.prod").is_file():
        return None
    if not Config().useVite:
        return None
    return get_client_port()
