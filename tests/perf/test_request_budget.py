"""A request through Nexy costs at most a few times the same request through bare Starlette.

Both run in this process, on the same machine, so the ratio does not depend on how fast the
machine is. A change that makes a request slower than its budget fails here, before review.
"""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from tests.perf.asgi_timer import seconds_per_request

ROUTES = {
    "src/routes/fast/index.py": 'async def GET():\n    return {"message": "Hello"}\n',
    "src/routes/typed/index.py": (
        'def GET() -> dict[str, str]:\n    return {"message": "Hello"}\n'
    ),
    "src/actions/__init__.py": (
        "from nexy.decorators import Action\n\n\n"
        "@Action\nasync def add(a: int, b: int) -> dict[str, int]:\n"
        '    return {"sum": a + b}\n'
    ),
}
BODY = json.dumps({"a": 1, "b": 2}).encode()

# Measured ratios on 2026-11-17, times about 1.5 for the noise of a shared CI runner.
BUDGETS = {"fast": 4.3, "typed": 16.0, "action": 4.3}


async def _json(_request: Request) -> Response:
    return JSONResponse({"message": "Hello"})


async def _add(request: Request) -> Response:
    body = await request.json()
    return JSONResponse({"sum": int(body["a"]) + int(body["b"])})


def _baseline() -> Starlette:
    routes = [Route("/json", _json), Route("/add", _add, methods=["POST"])]
    return Starlette(routes=routes)


@pytest.fixture(scope="module")
def nexy_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Any]:
    root = tmp_path_factory.mktemp("budget")
    for name, source in ROUTES.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(source, encoding="utf-8")
    (root / "nexyconfig.py").write_text(
        "from nexy.core.models import NexyConfigModel\n\n\n"
        "class NexyConfig(NexyConfigModel):\n    useVite: bool = False\n",
        encoding="utf-8",
    )
    before, path = set(sys.modules), list(sys.path)
    yield _build(root)
    # The project's folder and src package must not answer the imports of the tests that follow.
    sys.path[:] = path
    for name in set(sys.modules) - before:
        if name == "src" or name.startswith("src."):
            del sys.modules[name]


def _build(root: Path) -> Any:
    from nexy.core.config import Config
    from nexy.modules.routers.actions.store import ACTIONS_STORE
    from nexy.modules.routers.app import AppServer

    previous = Path.cwd()
    os.chdir(root)
    Config.reset()
    try:
        app = AppServer().run()
        action = ACTIONS_STORE.path_map["src.actions.add"]
    finally:
        os.chdir(previous)
        Config.reset()
    return app, action


def _ratio(nexy: float, starlette: float, name: str) -> float:
    ratio = nexy / starlette
    print(f"\n{name}: Nexy {nexy * 1e6:.1f} us, Starlette {starlette * 1e6:.1f} us, x{ratio:.2f}")
    return ratio


def test_budget_of_an_async_file_route(nexy_app):
    app, _action = nexy_app
    nexy = seconds_per_request(app, "/fast")
    ratio = _ratio(nexy, seconds_per_request(_baseline(), "/json"), "fast")
    assert ratio < BUDGETS["fast"]


def test_budget_of_a_sync_typed_file_route(nexy_app):
    app, _action = nexy_app
    nexy = seconds_per_request(app, "/typed")
    ratio = _ratio(nexy, seconds_per_request(_baseline(), "/json"), "typed")
    assert ratio < BUDGETS["typed"]


def test_budget_of_a_server_action(nexy_app):
    app, action = nexy_app
    nexy = seconds_per_request(app, action, "POST", BODY)
    baseline = seconds_per_request(_baseline(), "/add", "POST", BODY)
    assert _ratio(nexy, baseline, "action") < BUDGETS["action"]
