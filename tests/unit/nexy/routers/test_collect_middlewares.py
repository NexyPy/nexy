"""`useMiddlewares` takes a middleware class, or a (class, options) pair."""

from types import SimpleNamespace

from nexy.modules.routers.middlewares import collect_middlewares


class AppHeader:
    def __init__(self, app):
        self.app = app


def _config(use_middlewares):
    return SimpleNamespace(
        useCORS=None,
        useGZip=None,
        useTrustedHost=None,
        useSession=None,
        useAuth=None,
        useMiddlewares=use_middlewares,
    )


def test_collect_middlewares_takes_a_bare_class():
    assert collect_middlewares(_config([AppHeader])) == [(AppHeader, {})]


def test_collect_middlewares_takes_a_class_with_options():
    assert collect_middlewares(_config([(AppHeader, {"a": 1})])) == [(AppHeader, {"a": 1})]


def test_collect_middlewares_keeps_the_order_of_the_list():
    pairs = collect_middlewares(_config([AppHeader, (AppHeader, {"a": 1})]))
    assert pairs == [(AppHeader, {}), (AppHeader, {"a": 1})]
