"""The dev endpoint that renders documents trusts nothing it receives."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is not installed")


def _call(fn: str, *args: object) -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "render_request.mjs"), json.dumps([{"fn": fn, "args": list(args)}])],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    if "ERR_UNKNOWN_FILE_EXTENSION" in done.stderr:
        pytest.skip("this Node.js cannot run TypeScript")
    assert "@@" in done.stdout, done.stderr[-800:]
    return json.loads(done.stdout.split("@@")[1])[0]


@pytest.mark.parametrize("address", ["127.0.0.1", "::1", "::ffff:127.0.0.1"])
def test_loopback_addresses_are_accepted(address):
    assert _call("isLoopback", address) == {"ok": True}


@pytest.mark.parametrize("address", ["192.168.1.20", "10.0.0.5", "::ffff:192.168.1.20", None, ""])
def test_other_addresses_are_refused(address):
    assert _call("isLoopback", address) == {"ok": False}


def test_a_valid_request_is_parsed():
    body = {
        "page": "/src/routes/index.tsx",
        "layouts": ["/src/routes/layout.tsx"],
        "props": {"a": 1},
    }
    assert _call("parseRenderRequest", json.dumps(body)) == {"ok": body}


def test_a_null_page_is_the_shell():
    body = {"page": None, "layouts": [], "props": {}}
    assert _call("parseRenderRequest", json.dumps(body)) == {"ok": body}


@pytest.mark.parametrize(
    "body",
    [
        "not json",
        "[]",
        json.dumps({"page": 5, "layouts": [], "props": {}}),
        json.dumps({"page": None, "layouts": "x", "props": {}}),
        json.dumps({"page": None, "layouts": [1], "props": {}}),
        json.dumps({"page": None, "layouts": [], "props": []}),
        json.dumps({"page": None, "layouts": [], "props": None}),
    ],
)
def test_malformed_requests_are_rejected(body):
    assert "error" in _call("parseRenderRequest", body)


@pytest.mark.parametrize("page", ["/etc/passwd", "/src/routes/../../x.tsx", "/src/main.ts"])
def test_only_route_files_can_be_rendered(page):
    body = json.dumps({"page": page, "layouts": [], "props": {}})
    assert "error" in _call("parseRenderRequest", body)


CWD = "C:/work/app"


@pytest.mark.parametrize(
    "layout",
    [
        "C:/work/app/src/routes/layout.vue",
        "C:\work\app\src\routes\layout.vue",
        "C:/work/app/src/routes/layout.vue?vue&type=template",
    ],
)
def test_the_root_layout_is_recognised_whatever_the_path_spelling(layout):
    assert _call("isRootLayout", layout, "vue", CWD) == {"ok": True}


def test_a_drive_letter_in_another_case_is_the_same_file_on_windows():
    import sys

    if sys.platform != "win32":
        pytest.skip("paths are case-sensitive here")
    assert _call("isRootLayout", "c:/work/app/src/routes/layout.vue", "vue", CWD) == {"ok": True}


@pytest.mark.parametrize(
    "layout",
    [
        "C:/work/app/src/routes/blog/layout.vue",
        "C:/work/app/src/routes/layout.svelte",
        "C:/work/app/src/layout.vue",
    ],
)
def test_nested_or_foreign_layouts_are_not_the_root_layout(layout):
    assert _call("isRootLayout", layout, "vue", CWD) == {"ok": False}
