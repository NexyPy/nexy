"""Running the application under uvicorn in the foreground."""

from __future__ import annotations

import os
import sys
import traceback
from typing import Any

import uvicorn

from nexy.core.config import Config
from nexy.helpers.common.console import console
from nexy.helpers.server.markers import write_port_file
from nexy.helpers.server.uvicorn_config import NEXY_LOG_CONFIG, SERVE_LIMITS
from nexy.modules.i18n import t

APP = "nexy.modules.routers.app:_server"


def worker_count(config: Config, requested: int | None) -> int:
    """The workers to start: what was asked, else the config, else one (Windows) or one per CPU."""
    if requested is not None:
        return requested
    if config.useWorkers:
        return config.useWorkers
    return 1 if sys.platform == "win32" else os.cpu_count() or 1


def _options(
    host: str, port: int, keyfile: str | None, certfile: str | None, workers: int
) -> dict[str, Any]:
    options: dict[str, Any] = {
        "host": host,
        "port": port,
        "log_config": NEXY_LOG_CONFIG,
        "access_log": False,
        "log_level": "info",
        **SERVE_LIMITS,
    }
    if keyfile and certfile:
        options.update(ssl_keyfile=keyfile, ssl_certfile=certfile)
    if workers > 1:
        options["workers"] = workers
    return options


def run_uvicorn(
    host: str | None = None,
    port: int = 3000,
    ssl_keyfile: str | None = None,
    ssl_certfile: str | None = None,
    workers: int | None = None,
) -> bool | None:
    """Serve until the server stops; True when it stopped normally, None when it could not start."""
    write_port_file("server", port)
    count = worker_count(Config(), workers)
    try:
        uvicorn.run(APP, **_options(host or "127.0.0.1", port, ssl_keyfile, ssl_certfile, count))
    except Exception as error:
        traceback.print_exc()
        failure = t("server.launch_failed", "Server launch failed:")
        console.print(f"[red]✘ {failure}[/red] {error}")
        return None
    return True
