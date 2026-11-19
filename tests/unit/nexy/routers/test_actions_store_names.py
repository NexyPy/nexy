"""ActionsStore.name_of turns the hashed path of an action back into its function name."""

from __future__ import annotations

from nexy.modules.routers.actions.store import ActionsStore


def _store() -> ActionsStore:
    store = ActionsStore()
    store.path_map["src.actions.ping.ping"] = "/_nx_6a20e9479679"
    return store


def test_name_of_an_action_path_is_its_function_name():
    assert _store().name_of("/_nx_6a20e9479679") == "ping"


def test_name_of_another_path_is_none():
    assert _store().name_of("/users") is None
