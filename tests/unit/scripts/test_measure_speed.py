"""scripts/measure_speed.py measures the startup, first page and recompile times (#297)."""

from __future__ import annotations

import importlib.util
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "measure_speed.py"


@pytest.fixture(name="speed", scope="module")
def _speed() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("measure_speed", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(name="measured", scope="module")
def _measured(speed, tmp_path_factory) -> dict[str, float]:
    return speed.measure(speed.project(tmp_path_factory.mktemp("speed")), runs=1)


def test_project_has_a_page(speed, tmp_path):
    assert (speed.project(tmp_path) / "src/routes/index.nexy").is_file()


@pytest.mark.parametrize("name", ["startup", "first_page", "recompile"])
def test_measure_gives_a_positive_time(measured, name):
    assert measured[name] > 0


def test_table_names_the_machine(speed):
    assert "| Machine | Linux x86_64, 8 CPUs, Python 3.13.1 |" in speed.table(
        {"startup": 0.5, "first_page": 0.7, "recompile": 0.0016},
        "Linux x86_64, 8 CPUs, Python 3.13.1",
    )


def test_table_gives_the_startup_in_milliseconds(speed):
    assert "| Startup | 500 ms |" in speed.table(
        {"startup": 0.5, "first_page": 0.7, "recompile": 0.0016}, "m"
    )


def test_table_keeps_a_decimal_under_ten_milliseconds(speed):
    assert "| Recompile a page | 1.6 ms |" in speed.table(
        {"startup": 0.5, "first_page": 0.7, "recompile": 0.0016}, "m"
    )


def test_machine_names_the_python_version(speed):
    import platform

    assert f"Python {platform.python_version()}" in speed.machine()
