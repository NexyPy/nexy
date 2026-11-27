"""A `.tsx` edit still reaches the tab after the tab reloads (#690).

The first load installs React Fast Refresh through the synchronous Vite preamble. The regression
is that a second load used to render the route before the hook was installed, so later hot
updates were logged but never applied to the DOM.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext

from nexy.helpers.server.server import Server
from tests.e2e.conftest import FIXTURE_DIR, _free_port, _install_node_modules, _wait_for_port

NX = "import sys; from nexy.modules.cli import CLI; sys.argv[0] = 'nx'; CLI()"
LAYOUT = (
    "export default function Layout({ children }: { children: React.ReactNode }) {\n"
    "  return (\n    <html><head><title>Reload</title></head><body>{children}</body></html>\n  );\n"
    "}\n"
)
PAGE = "export default function Home() {\n  return <h1>reload v0</h1>;\n}\n"


def _prepare(project: Path) -> Path:
    shutil.copytree(FIXTURE_DIR, project)
    config = project / "nexyconfig.py"
    config.write_text(config.read_text(encoding="utf-8") + "    useCSR = True\n", encoding="utf-8")
    routes = project / "src" / "routes"
    (routes / "layout.nexy").unlink()
    (routes / "layout.tsx").write_text(LAYOUT, encoding="utf-8")
    page = routes / "index.tsx"
    page.write_text(PAGE, encoding="utf-8")
    return page


@pytest.fixture(scope="module")
def csr_app(tmp_path_factory: pytest.TempPathFactory) -> Iterator[tuple[str, Path]]:
    project = tmp_path_factory.mktemp("hmr") / "app"
    page = _prepare(project)
    _install_node_modules(project)
    port = _free_port()
    server = subprocess.Popen(  # nosec B603 - sys.executable plus a fixed launcher
        [sys.executable, "-c", NX, "dev", "--port", str(port)],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert _wait_for_port(port), "nx dev did not listen"
        yield f"http://127.0.0.1:{port}/", page
    finally:
        Server.stop_process(server)


@pytest.mark.e2e
def test_a_second_load_keeps_hot_updates(
    context: BrowserContext, csr_app: tuple[str, Path]
) -> None:
    url, source = csr_app
    page = context.new_page()
    page.goto(url)
    page.wait_for_function("t => document.body.innerText.includes(t)", arg="reload v0")
    page.wait_for_load_state("networkidle")
    source.write_text(source.read_text(encoding="utf-8").replace("reload v0", "reload v1"))
    page.wait_for_function("t => document.body.innerText.includes(t)", arg="reload v1")
    page.reload()
    page.wait_for_function("t => document.body.innerText.includes(t)", arg="reload v1")
    page.wait_for_load_state("networkidle")
    source.write_text(source.read_text(encoding="utf-8").replace("reload v1", "reload v2"))
    page.wait_for_function(
        "t => document.body.innerText.includes(t)", arg="reload v2", timeout=10000
    )
