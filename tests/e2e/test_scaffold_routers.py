"""Every scaffold template must build and answer requests, for both routers.

Each project runs in its own interpreter: Nexy resolves imports relative to the
working directory, so an in-process run would leak state between templates.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from nexy.modules.cli.init.template_setup import _render_local_template

REPO = Path(__file__).resolve().parents[2]

_RUNNER = """
import json, sys
sys.path.insert(0, ".")
from nexy.core.config import Config
Config()
from nexy.modules.builder import Builder
build = Builder().build()
# Like `nx dev`: the app module scans routes on import, so it loads after the build.
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer
out = {"failed": list(build.failed), "load_error": Config.get_load_error(), "pages": {}}
with TestClient(AppServer().run()) as client:
    for path in ("/", "/about", "/definitely-not-a-route"):
        r = client.get(path)
        out["pages"][path] = [r.status_code, r.headers.get("content-type", ""), r.text]
sys.stdout.write("@@" + json.dumps(out) + "@@")
"""

WEB = [
    ("web-fbr", "none", False),
    ("web-fbr", "react", False),
    ("web-fbr", "vue", False),
    ("web-fbr", "react", True),
    ("web-fbr", "svelte", True),
    ("web-fbr", "vue", True),
    ("web-fbr", "preact", True),
    ("web-fbr", "solid", True),
    ("web-modular", "none", False),
    ("web-modular", "react", False),
    ("web-modular", "vue", False),
]
API = [("api-fbr", "none", False), ("api-modular", "none", False)]


def _run(tmp_path: Path, template: str, framework: str, use_csr: bool) -> dict:
    config = {
        "client_framework": framework,
        "FBRouter": template.endswith("fbr"),
        "project_type": template.split("-")[0],
        "orm": "None",
        "useCSR": use_csr,
    }
    _render_local_template(template, tmp_path, config, "demo")
    env = {**os.environ, "PYTHONPATH": str(REPO), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, "-c", _RUNNER],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    assert "@@" in proc.stdout, proc.stderr[-2000:]
    return json.loads(proc.stdout.split("@@")[1])


@pytest.mark.parametrize(("template", "framework", "use_csr"), WEB)
def test_web_template_serves_a_valid_document(tmp_path, template, framework, use_csr):
    result = _run(tmp_path, template, framework, use_csr)
    assert result["load_error"] is None
    assert result["failed"] == []

    status, content_type, html = result["pages"]["/"]
    assert status == 200
    assert content_type.startswith("text/html")
    assert html.lstrip().lower().startswith("<!doctype html>"), html[:120]
    assert html.lower().count("<!doctype") == 1
    assert "</html>" in html
    if use_csr:
        # No layout.nexy in client mode: the root layout of the framework owns the document. Node
        # renders it, which needs a Vite server, so here the page describes itself to the browser.
        assert "__nexy_page" in html
    else:
        assert "<main" in html
    assert "object at 0x" not in html
    assert html.count("/_nexy/hmr") <= 1

    assert result["pages"]["/definitely-not-a-route"][0] == 404


@pytest.mark.parametrize(("template", "framework", "use_csr"), WEB)
@pytest.mark.parametrize(("path", "marker"), [("/about", "open source"), ("/", "Full-stack")])
def test_web_template_has_the_starter_pages(tmp_path, template, framework, use_csr, path, marker):
    """Every starter links Home and About, so both must exist, in every mode."""
    result = _run(tmp_path, template, framework, use_csr)
    status, content_type, html = result["pages"][path]
    assert status == 200, path
    assert content_type.startswith("text/html")
    if use_csr:
        assert "__nexy_page" in html  # the page describes itself to the browser
    else:
        assert marker.lower() in html.lower()


@pytest.mark.parametrize(("template", "framework", "use_csr"), API)
def test_api_template_serves_json(tmp_path, template, framework, use_csr):
    result = _run(tmp_path, template, framework, use_csr)
    assert result["load_error"] is None
    assert result["failed"] == []

    status, content_type, body = result["pages"]["/"]
    assert status == 200
    assert "json" in content_type
    json.loads(body)
    assert result["pages"]["/definitely-not-a-route"][0] == 404
