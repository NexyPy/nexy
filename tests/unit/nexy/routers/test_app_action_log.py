"""The access log of the assembled application names an action instead of its hashed URL."""

from __future__ import annotations

from nexy.helpers.server.access_log import AccessLogMiddleware
from nexy.modules.routers.actions.store import ACTIONS_STORE


def test_the_access_log_reads_action_names_from_the_store(nexy_project):
    from nexy.modules.routers.app import AppServer

    nexy_project("")
    server = AppServer()
    server.run()
    log = next(m for m in server.server.user_middleware if m.cls is AccessLogMiddleware)
    assert log.kwargs["names"] == ACTIONS_STORE.name_of
