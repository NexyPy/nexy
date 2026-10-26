"""Nested framework layouts and client navigation, with the real libraries in jsdom.

Each generated framework runtime (``nexy.modules.frontend.<fw>``) is mounted on an island that lists
two layouts. The scenario checks the composed DOM, that layouts survive a navigation, and that a
different layout chain remounts them.

Needs Node.js 22.13+ and ``npm install`` in this directory; skipped otherwise.
"""

import importlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
GENERATED = HERE / ".generated"
FRAMEWORKS = ("react", "preact", "vue", "solid", "svelte")

_STRIP = """
const { stripTypeScriptTypes } = require('node:module');
const fs = require('node:fs');
const [src, dst] = process.argv.slice(1);
fs.writeFileSync(dst, stripTypeScriptTypes(fs.readFileSync(src, 'utf8')));
"""

NODE = shutil.which("node")
pytestmark = [
    pytest.mark.skipif(NODE is None, reason="Node.js is not installed"),
    pytest.mark.skipif(
        not (HERE / "node_modules" / "jsdom").is_dir(),
        reason="run `npm install` in tests/client first",
    ),
]


def _runtime(framework: str) -> Path:
    render = getattr(importlib.import_module("nexy.modules.frontend.frameworks"), framework)()
    GENERATED.mkdir(exist_ok=True)
    source = GENERATED / f"{framework}.runtime.ts"
    source.write_text(render.render, encoding="utf-8")
    target = GENERATED / f"{framework}.runtime.mjs"
    done = subprocess.run(
        [NODE, "-e", _STRIP, str(source), str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode != 0:
        pytest.skip(f"this Node.js cannot strip TypeScript types: {done.stderr[-200:]}")
    return target


def _run(framework: str) -> dict:
    done = subprocess.run(
        [
            NODE,
            "--conditions=browser",
            str(HERE / "scenario.mjs"),
            framework,
            str(_runtime(framework)),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


@pytest.fixture(scope="module", params=FRAMEWORKS)
def report(request: pytest.FixtureRequest) -> dict:
    return _run(request.param)


def test_layouts_wrap_the_page_in_order(report):
    assert report["initial"]["nested"]


def test_navigation_replaces_only_the_page(report):
    assert report["sameChain"]["nested"]
    assert report["sameChain"]["oldPageGone"]


def test_layouts_keep_their_dom_across_navigation(report):
    assert report["sameChain"]["l1Preserved"]
    assert report["sameChain"]["l2Preserved"]


def test_a_different_chain_remounts_cleanly(report):
    assert report["otherChain"] == {"inL1": True, "l2Gone": True, "noStalePage": True}


def test_generated_router_runtime_is_valid_and_defines_prefetch():
    from nexy.modules.frontend.vite_entry import runtime_source

    GENERATED.mkdir(exist_ok=True)
    source = GENERATED / "router.runtime.ts"
    source.write_text(runtime_source(), encoding="utf-8")
    target = GENERATED / "router.runtime.mjs"
    done = subprocess.run(
        [NODE, "-e", _STRIP, str(source), str(target)], capture_output=True, text=True, check=False
    )
    if done.returncode != 0:
        pytest.skip("this Node.js cannot strip TypeScript types")
    checked = subprocess.run(
        [NODE, "--check", str(target)], capture_output=True, text=True, check=False
    )
    assert checked.returncode == 0, checked.stderr[-600:]
    assert "w.__nexy_prefetch = " in source.read_text(encoding="utf-8")
    assert "pickRenderer" in source.read_text(encoding="utf-8")


def _run_document(framework: str, mode: str) -> subprocess.CompletedProcess[str]:
    runtime = _runtime(framework)
    if framework == "solid":
        # Solid's server and browser builds differ, so the page is rendered by one Node process and
        # hydrated by another.
        served = GENERATED / f"solid_{mode}.html"
        script = str(HERE / "solid_document.mjs")
        rendered = subprocess.run(
            [NODE, script, "server", mode, str(served)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=120,
            check=False,
            cwd=HERE,
        )
        assert rendered.returncode == 0, rendered.stderr[-1500:]
        args = ["client", mode, str(runtime), str(served)]
    else:
        script = str(HERE / "document.mjs")
        args = [framework, mode, str(runtime)]
    return subprocess.run(
        [NODE, "--conditions=browser", script, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        cwd=HERE,
    )


@pytest.fixture(
    scope="module",
    params=[
        *[("react", mode) for mode in ("document", "shell", "client")],
        *[("solid", mode) for mode in ("document", "shell")],
    ],
    ids=lambda pair: "-".join(pair),
)
def document_report(request: pytest.FixtureRequest) -> dict:
    done = _run_document(*request.param)
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_document_hydrates_without_mismatch(document_report):
    assert document_report["hydrationErrors"] == []


def test_document_is_interactive_after_hydration(document_report):
    assert document_report["layoutRendered"] and document_report["interactive"]


def test_root_layout_owns_the_html_element(document_report):
    assert document_report["title"] == "Layout title"
    # In client mode the layout replaces the placeholder document, so its lang wins.
    assert document_report["attributesKept"] is (document_report["mode"] != "client")


def test_navigation_keeps_html_and_layouts(document_report):
    assert document_report["navigation"] == {
        "pageSwapped": True,
        "htmlPreserved": True,
        "headerPreserved": True,
        "nestedKept": True,
    }


@pytest.fixture(scope="module", params=("preact", "vue", "svelte"))
def takeover_report(request: pytest.FixtureRequest) -> dict:
    done = subprocess.run(
        [
            NODE,
            "--conditions=browser",
            str(HERE / "takeover.mjs"),
            request.param,
            str(_runtime(request.param)),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
        cwd=HERE,
    )
    assert "@@" in done.stdout, (done.stdout + done.stderr)[-1500:]
    return json.loads(done.stdout.split("@@")[1])


def test_takeover_keeps_html_head_and_doctype_from_the_server(takeover_report):
    assert takeover_report["htmlKept"] and takeover_report["headKept"]
    assert takeover_report["doctypeKept"] and takeover_report["bodyAttributes"]
    assert takeover_report["singleBody"]


def test_takeover_renders_the_layouts_and_is_interactive(takeover_report):
    assert takeover_report["layoutRendered"] and takeover_report["interactive"]
    assert takeover_report["errors"] == []


def test_takeover_navigation_keeps_the_body_and_layouts(takeover_report):
    assert takeover_report["navigation"] == {
        "pageSwapped": True,
        "htmlPreserved": True,
        "bodyPreserved": True,
        "headerPreserved": True,
        "nestedKept": True,
    }
