"""Importing the application modules does not assemble the application."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROBE = """
import sys
import nexy.app, nexy.modules.routers.app as assembly
print('_server' in vars(assembly))
print(callable(nexy.app.app))
print('_server' in vars(assembly))
"""


def _run(tmp_path: Path) -> list[str]:
    done = subprocess.run(
        [sys.executable, "-c", PROBE], cwd=tmp_path, capture_output=True, text=True, check=True
    )
    return done.stdout.split()


def test_importing_does_not_build_the_app(tmp_path):
    assert _run(tmp_path)[0] == "False"


def test_reading_app_builds_a_callable_application(tmp_path):
    assert _run(tmp_path)[1] == "True"


def test_the_built_application_is_kept(tmp_path):
    assert _run(tmp_path)[2] == "True"


def test_an_unknown_attribute_is_an_error():
    import nexy.app

    try:
        nexy.app.nothing  # noqa: B018
    except AttributeError:
        return
    raise AssertionError("expected AttributeError")
