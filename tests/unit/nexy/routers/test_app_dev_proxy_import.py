"""A production app does not load the Vite dev proxy, nor httpx and websockets with it."""

from __future__ import annotations

import os
import subprocess  # nosec B404
import sys
from pathlib import Path

_ASSEMBLE = (
    "import sys, nexy.app; nexy.app.app; "
    "print(','.join(m for m in ('httpx', 'websockets') if m in sys.modules))"
)


def _loaded_after_assembly(project: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(  # nosec B603 - sys.executable with a fixed script
        [sys.executable, "-c", _ASSEMBLE],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def test_a_production_app_does_not_load_the_dev_proxy(tmp_path, monkeypatch):
    monkeypatch.delenv("NEXY_DEV_SERVER", raising=False)
    assert _loaded_after_assembly(tmp_path, dict(os.environ)) == ""


def test_a_dev_app_is_still_wrapped_by_the_vite_proxy(monkeypatch):
    from fastapi import FastAPI

    from nexy.helpers.server.proxy import ViteProxyMiddleware
    from nexy.modules.routers import app as assembly

    monkeypatch.setattr(assembly, "vite_proxy_port", lambda: 5199)
    assert isinstance(assembly.AppServer._with_vite_proxy(FastAPI()), ViteProxyMiddleware)
