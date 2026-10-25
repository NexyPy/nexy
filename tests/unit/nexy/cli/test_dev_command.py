"""`nx dev` end to end with every collaborator replaced: order of events, restarts, clean-up."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

import pytest

dev_module = importlib.import_module("nexy.modules.cli.commands.dev")


class Recorder:
    """Shared event log: what happened, in order."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self.reload_callback: Any = None

    def __call__(self, event: str) -> None:
        self.events.append(event)

    def count(self, event: str) -> int:
        return self.events.count(event)


class FakeBuildResult:
    def __init__(self, failed: dict[str, Any] | None = None) -> None:
        self.failed = list(failed or {})
        self.errors = failed or {}


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    rec = Recorder()
    state = SimpleNamespace(
        rec=rec,
        use_vite=True,
        build_result=FakeBuildResult(),
        vite_ready=True,
        generate_error=None,
        serve_plan=[],  # one entry per uvicorn run: "exit" | "restart" | "interrupt"
        vite_proc=object(),
    )
    config = SimpleNamespace(
        useVite=True,
        useHost="127.0.0.1",
        usePort=3000,
        WATCH_EXTENSIONS_GLOB=["*.py"],
        WATCH_EXCLUDE_PATTERNS=[],
    )

    class FakeServer:
        @staticmethod
        def resolve_ports(host: str, port: int) -> tuple[int, int]:
            return port, 5173

        @staticmethod
        def check_nexy_prod(delete: bool = False) -> None:
            rec("check_prod")

        @staticmethod
        def get_ssl_config(_config: Any) -> tuple[None, None]:
            return None, None

        @staticmethod
        def vite(port: int, ssl: bool) -> object:
            rec(f"vite_start:{port}")
            return state.vite_proc

        @staticmethod
        def wait_for_vite_ready(port: int, process: Any = None) -> bool:
            rec("vite_wait")
            return state.vite_ready

        @staticmethod
        def stop_process(process: Any) -> None:
            rec("stop_process" if process is not None else "stop_process:none")

        @staticmethod
        def get_network_ip() -> str:
            return "192.168.1.2"

    class FakeFrontend:
        def generate(self) -> None:
            rec("frontend")
            if state.generate_error:
                raise state.generate_error

    class FakeBuilder:
        def build(self, showlog: bool = False) -> FakeBuildResult:
            rec("build")
            return state.build_result

    class FakeUvicornServer:
        def __init__(self, uvicorn_config: Any) -> None:
            self.config = uvicorn_config
            self.should_exit = False
            rec("uvicorn_new")

        def run(self) -> None:
            rec("uvicorn_run")
            step = state.serve_plan.pop(0) if state.serve_plan else "exit"
            if step == "restart":
                rec.reload_callback()
            if step == "interrupt":
                raise KeyboardInterrupt

    monkeypatch.setattr(dev_module, "pycache", lambda: rec("pycache"))
    monkeypatch.setattr(dev_module, "abort_on_invalid_config", lambda: rec("validate"))
    monkeypatch.setattr(dev_module, "Config", lambda: config)
    monkeypatch.setattr(dev_module, "Server", FakeServer)
    monkeypatch.setattr(dev_module, "FrontendGenerator", FakeFrontend)
    monkeypatch.setattr(dev_module, "Builder", FakeBuilder)
    monkeypatch.setattr(dev_module.VFS, "set_dev_mode", lambda *_: rec("dev_mode"))
    monkeypatch.setattr(dev_module, "_require_vite_install", lambda: rec("require_vite"))
    monkeypatch.setattr(dev_module, "purge_project_modules", lambda: rec("purge"))
    monkeypatch.setattr(dev_module, "stop_observer", lambda _o: rec("stop_observer"))

    def create_observer(**kwargs: Any) -> object:
        rec.reload_callback = kwargs["on_reload_api"]
        rec("observer")
        return object()

    monkeypatch.setattr(dev_module, "create_observer", create_observer)
    for name in ("banner", "success", "entry"):
        monkeypatch.setattr(dev_module.launcher, name, lambda *a, **k: None)
    monkeypatch.setattr("uvicorn.Config", lambda *a, **k: SimpleNamespace(args=a, kwargs=k))
    monkeypatch.setattr("uvicorn.Server", FakeUvicornServer)
    monkeypatch.delenv(dev_module.DEV_ENV_VAR, raising=False)
    state.config = config
    return state


def test_happy_path_runs_in_order_and_cleans_up(world):
    dev_module.dev()

    events = world.rec.events
    assert events[:2] == ["pycache", "validate"]
    assert events.index("require_vite") < events.index("check_prod") < events.index("build")
    assert events.index("vite_start:5173") < events.index("vite_wait") < events.index("uvicorn_run")
    assert events[-2:] == ["stop_observer", "stop_process"]


def test_marks_the_process_as_the_dev_server(world):
    import os

    dev_module.dev()
    assert os.environ[dev_module.DEV_ENV_VAR] == "1"


def test_explicit_host_and_port_win_over_the_config(world, monkeypatch):
    seen = {}
    monkeypatch.setattr(
        dev_module.Server,
        "resolve_ports",
        staticmethod(lambda h, p: seen.update(h=h, p=p) or (p, 1)),
    )
    dev_module.dev(port=4100, host="0.0.0.0")  # noqa: S104 - test value
    assert seen == {"h": "0.0.0.0", "p": 4100}  # noqa: S104


def test_without_vite_nothing_is_started_or_waited_for(world):
    world.config.useVite = False
    dev_module.dev()
    assert "require_vite" not in world.rec.events
    assert not any(e.startswith("vite") for e in world.rec.events)
    assert "uvicorn_run" in world.rec.events


def test_build_failures_stop_vite_but_the_server_still_starts(world):
    world.build_result = FakeBuildResult({"src/routes/a.nexy": None})
    dev_module.dev()
    events = world.rec.events
    assert "vite_wait" not in events
    assert events.index("stop_process") < events.index("uvicorn_run")
    assert events[-1] == "stop_process:none"


def test_vite_that_never_answers_aborts_with_exit_code_1(world):
    world.vite_ready = False
    with pytest.raises(SystemExit) as error:
        dev_module.dev()
    assert error.value.code == 1
    assert "uvicorn_run" not in world.rec.events
    assert world.rec.count("stop_process") == 1


def test_an_initialisation_error_stops_vite_and_exits(world):
    world.generate_error = RuntimeError("boom")
    with pytest.raises(SystemExit) as error:
        dev_module.dev()
    assert error.value.code == 1
    assert "uvicorn_run" not in world.rec.events


def test_a_file_change_restarts_uvicorn_with_fresh_modules(world):
    world.serve_plan = ["restart", "exit"]
    dev_module.dev()
    assert world.rec.count("uvicorn_run") == 2
    assert world.rec.count("uvicorn_new") == 2
    assert world.rec.count("purge") == 2


def test_ctrl_c_still_cleans_up(world):
    world.serve_plan = ["interrupt"]
    dev_module.dev()
    assert world.rec.events[-2:] == ["stop_observer", "stop_process"]


def test_the_observer_watches_what_the_config_says(world, monkeypatch):
    captured = {}
    original = dev_module.create_observer

    def spy(**kwargs):
        captured.update(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(dev_module, "create_observer", spy)
    dev_module.dev()
    assert captured["patterns"] == ["*.py"] and captured["path"] == "."


class TestEndpoint:
    def test_protocol_follows_the_certificates(self):
        plain = dev_module._Endpoint("127.0.0.1", 3000)
        secure = dev_module._Endpoint("127.0.0.1", 3000, "key.pem", "cert.pem")
        assert (plain.protocol, secure.protocol) == ("http", "https")

    def test_a_key_without_a_certificate_stays_http(self):
        assert dev_module._Endpoint("h", 1, ssl_keyfile="key.pem").protocol == "http"


class TestReloader:
    def test_a_request_stops_the_running_server(self):
        reloader = dev_module._Reloader()
        reloader._server = SimpleNamespace(should_exit=False)
        reloader.request_restart()
        assert reloader.restart_requested and reloader._server.should_exit

    def test_a_request_before_the_server_exists_is_remembered(self):
        reloader = dev_module._Reloader()
        reloader.request_restart()
        assert reloader.restart_requested

    def test_serve_returns_when_no_restart_was_requested(self, world):
        dev_module._Reloader().serve(dev_module._Endpoint("127.0.0.1", 3000))
        assert world.rec.count("uvicorn_run") == 1


class TestSettleVite:
    def test_failed_routes_drop_vite_without_waiting(self, world):
        session = dev_module._Session(vite=object())
        dev_module._settle_vite(session, FakeBuildResult({"a": None}), 5173)
        assert session.vite is None and "vite_wait" not in world.rec.events

    def test_a_ready_vite_is_kept(self, world):
        session = dev_module._Session(vite=world.vite_proc)
        dev_module._settle_vite(session, FakeBuildResult(), 5173)
        assert session.vite is world.vite_proc

    def test_an_unready_vite_is_dropped_and_exits_1(self, world):
        world.vite_ready = False
        session = dev_module._Session(vite=world.vite_proc)
        with pytest.raises(SystemExit) as error:
            dev_module._settle_vite(session, FakeBuildResult(), 5173)
        assert error.value.code == 1 and session.vite is None


class TestBanner:
    def test_the_network_address_is_shown_when_listening_on_all_interfaces(
        self, world, monkeypatch
    ):
        entries: list[str] = []
        monkeypatch.setattr(
            dev_module.launcher, "entry", lambda label, value: entries.append(value)
        )
        dev_module._print_banner(dev_module._Endpoint("0.0.0.0", 3000), 1.5)  # noqa: S104
        assert "http://localhost:3000" in entries and "http://192.168.1.2:3000" in entries

    def test_loopback_shows_no_network_line(self, world, monkeypatch):
        entries: list[str] = []
        monkeypatch.setattr(
            dev_module.launcher, "entry", lambda label, value: entries.append(value)
        )
        dev_module._print_banner(dev_module._Endpoint("127.0.0.1", 3000), 0.2)
        assert entries == ["http://localhost:3000", "0.20s"]


def test_purging_removes_the_application_modules(monkeypatch, world):
    import sys

    monkeypatch.setitem(sys.modules, "__nexy__.src.routes.index", object())
    monkeypatch.setitem(sys.modules, "nexy.modules.routers.app", object())
    dev_module._purge_app_modules()
    assert "__nexy__.src.routes.index" not in sys.modules
    assert "nexy.modules.routers.app" not in sys.modules
    assert world.rec.count("purge") == 1
