"""The dev endpoint that renders documents trusts nothing it receives."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
NODE = shutil.which("node")


def _call(fn: str, *args: object) -> dict:
    done = subprocess.run(
        [NODE, str(HERE / "render_request.mjs"), json.dumps([{"fn": fn, "args": list(args)}])],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
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


# The project folder of the platform the test runs on: `C:/...` on Windows, `/...` elsewhere. Vite
# reports module ids with forward slashes whatever the system, so only the spelling is varied.
CWD = HERE.as_posix()
ROOT_LAYOUT = f"{CWD}/src/routes/layout.vue"


@pytest.mark.parametrize(
    "layout",
    [ROOT_LAYOUT, ROOT_LAYOUT.replace("/", "\\"), f"{ROOT_LAYOUT}?vue&type=template"],
    ids=["forward slashes", "backslashes", "query string"],
)
def test_the_root_layout_is_recognised_whatever_the_path_spelling(layout):
    assert _call("isRootLayout", layout, "vue", str(HERE)) == {"ok": True}


def test_a_path_in_another_case_is_the_same_file_on_windows():
    # The platform is an argument, so both behaviours are tested on every system.
    other = f"{CWD.swapcase()}/src/routes/layout.vue"
    assert _call("isRootLayout", other, "vue", str(HERE), "win32") == {"ok": True}


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_a_path_in_another_case_is_another_file_where_paths_are_case_sensitive(platform):
    other = f"{CWD.swapcase()}/src/routes/layout.vue"
    assert _call("isRootLayout", other, "vue", str(HERE), platform) == {"ok": False}


@pytest.mark.parametrize(
    "layout",
    [
        f"{CWD}/src/routes/blog/layout.vue",
        f"{CWD}/src/routes/layout.svelte",
        f"{CWD}/src/layout.vue",
    ],
    ids=["nested", "other framework", "outside routes"],
)
def test_nested_or_foreign_layouts_are_not_the_root_layout(layout):
    assert _call("isRootLayout", layout, "vue", str(HERE)) == {"ok": False}


def test_concurrent_renders_each_see_their_own_request_location():
    done = subprocess.run(
        [NODE, str(HERE / "render_request.mjs"), "[]", "concurrent"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert "@@" in done.stdout, done.stderr[-800:]
    seen = json.loads(done.stdout.split("@@")[1])
    assert [r["seen"] for r in seen["results"]] == ["/a", "/b"]
    assert seen["results"][0]["params"] == {"id": "/a"}
    assert seen["after"] is None  # nothing leaks once the renders are done


def test_a_render_request_may_carry_the_request_location():
    body = {
        "page": "/src/routes/index.tsx",
        "layouts": [],
        "props": {},
        "location": {"pathname": "/users/7", "search": "?tab=x"},
    }
    assert _call("parseRenderRequest", json.dumps(body)) == {"ok": body}


@pytest.mark.parametrize(
    "location",
    [{"pathname": 5, "search": ""}, {"pathname": "/", "search": None}, {"pathname": "/"}, "/x"],
)
def test_a_malformed_location_is_rejected(location):
    body = json.dumps({"page": None, "layouts": [], "props": {}, "location": location})
    assert "error" in _call("parseRenderRequest", body)
