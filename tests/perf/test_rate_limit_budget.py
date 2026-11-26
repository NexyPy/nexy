"""`useRateLimit` adds at most a few percent to the cost of a request through Nexy.

Two Nexy applications, one with the limit and one without, differ by less than the noise of the
machine, so their ratio cannot hold a budget of a few percent. This test measures what the limit
adds instead: the same bare ASGI application timed with and without `RateLimitMiddleware` around
it, and that difference divided by the cost of one request through a Nexy application. Everything
runs in this process, so the share does not depend on how fast the machine is.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from nexy.helpers.server.rate_limit import RateLimitMiddleware
from tests.perf.asgi_timer import seconds_per_request

ROUTE = 'async def GET():\n    return {"message": "Hello"}\n'
CONFIG = (
    "from nexy.core.models import NexyConfigModel\n\n\n"
    "class NexyConfig(NexyConfigModel):\n    useVite: bool = False\n"
)

# The share of a Nexy request the limit adds. Measured on 2026-11-26, six runs: 2.05% to 2.83%,
# times about 1.5 for the noise of a shared CI runner.
BUDGET = 0.043
TRIES = 3


async def _bare(_scope: Any, _receive: Any, send: Any) -> None:
    """The cheapest application that answers 200: what is left is the cost of the middleware."""
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"{}"})


@pytest.fixture(scope="module")
def nexy_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Any]:
    from nexy.core.config import Config
    from nexy.modules.routers.app import AppServer

    root = tmp_path_factory.mktemp("rate_limit")
    (root / "src/routes/fast").mkdir(parents=True)
    (root / "src/routes/fast/index.py").write_text(ROUTE, encoding="utf-8")
    (root / "nexyconfig.py").write_text(CONFIG, encoding="utf-8")
    before, path, previous = set(sys.modules), list(sys.path), Path.cwd()
    os.chdir(root)
    Config.reset()
    try:
        yield AppServer().run()
    finally:
        os.chdir(previous)
        Config.reset()
        # The project's folder and src package must not answer the imports of the tests after.
        sys.path[:] = path
        for name in set(sys.modules) - before:
            if name in ("src", "nexyconfig") or name.startswith("src."):
                del sys.modules[name]


def _best(app: Any, path: str) -> float:
    """The fastest of several timings of many requests: a few microseconds need both."""
    return min(seconds_per_request(app, path, count=20_000) for _ in range(TRIES))


def test_budget_of_the_rate_limit(nexy_app):
    # Far above what the timer sends from its one client: no request is refused.
    limited = RateLimitMiddleware(_bare, requests=10**9, per=60)
    added = _best(limited, "/") - _best(_bare, "/")
    request = seconds_per_request(nexy_app, "/fast")
    share = added / request
    print(f"\nrate limit: {added * 1e6:.2f} us on a {request * 1e6:.1f} us request, {share:.2%}")
    assert share < BUDGET
