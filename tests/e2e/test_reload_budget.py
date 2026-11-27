"""The reload a developer feels: from saving a file to the new text in the browser.

`nx dev` runs on a copy of the client_router fixture, once as a server project with a `.nexy`
page and once as a client project with a `.tsx` page (a project is one or the other, see
`useCSR`). Each test opens its page in a real Chromium, edits the file RUNS times and times every
edit from the write to the new text in the DOM. That covers the watcher, the compile, the HMR
message and the browser, so it is longer than the recompile alone that `scripts/measure_speed.py`
reports.
"""

from __future__ import annotations

import shutil
import statistics
import subprocess  # nosec B404
import sys
import time
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

import pytest
from playwright.sync_api import BrowserContext, Page

from nexy.helpers.server.server import Server
from tests.e2e.conftest import FIXTURE_DIR, _free_port, _install_node_modules, _wait_for_port

# Starts at 1 second and is lowered once the number is known (issue #470).
BUDGET_SECONDS = 1.0
RUNS = 5
NX = "import sys; from nexy.modules.cli import CLI; sys.argv[0] = 'nx'; CLI()"
NEXY_PAGE = '<main>\n    <p data-testid="reload">reload v0</p>\n</main>\n'
TSX_PAGE = (
    'export default function Home() {\n  return <h1 data-testid="reload">reload v0</h1>;\n}\n'
)
TSX_LAYOUT = (
    "export default function Layout({ children }: { children: React.ReactNode }) {\n"
    '  return (\n    <html lang="en">\n      <head><title>Reload</title></head>\n'
    "      <body>{children}</body>\n    </html>\n  );\n}\n"
)


class Reload(NamedTuple):
    """The page a project edits, and where it is served."""

    url: str
    file: Path


def _nexy_project(routes: Path) -> Path:
    """A server project: the `.nexy` layout of the fixture and one `.nexy` page."""
    (routes / "index.tsx").unlink()
    (routes / "about.tsx").unlink()
    shutil.rmtree(routes / "docs")
    page = routes / "hello.nexy"
    page.write_text(NEXY_PAGE, encoding="utf-8")
    return page


def _tsx_project(routes: Path) -> Path:
    """A client project: `useCSR` and a `.tsx` layout in place of the `.nexy` one."""
    config = routes.parents[1] / "nexyconfig.py"
    config.write_text(config.read_text(encoding="utf-8") + "    useCSR = True\n", encoding="utf-8")
    (routes / "layout.nexy").unlink()
    (routes / "layout.tsx").write_text(TSX_LAYOUT, encoding="utf-8")
    page = routes / "index.tsx"
    page.write_text(TSX_PAGE, encoding="utf-8")
    return page


CASES = {"nexy": (_nexy_project, "/hello"), "tsx": (_tsx_project, "/")}


@pytest.fixture(scope="module", params=list(CASES))
def reload_app(request: pytest.FixtureRequest, tmp_path_factory) -> Iterator[Reload]:
    """`nx dev` on a copy of the fixture shaped for `request.param`; yields what to edit."""
    project = tmp_path_factory.mktemp("reload") / "app"
    shutil.copytree(FIXTURE_DIR, project)
    prepare, route = CASES[request.param]
    page = prepare(project / "src" / "routes")
    _install_node_modules(project)
    port = _free_port()
    server = subprocess.Popen(  # nosec B603 - sys.executable with a fixed launcher
        [sys.executable, "-c", NX, "dev", "--port", str(port)],
        cwd=project,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert _wait_for_port(port), "nx dev did not listen"
        yield Reload(f"http://127.0.0.1:{port}{route}", page)
    finally:
        # The whole tree: on Windows terminate() alone leaves the Vite child of `nx dev` running.
        Server.stop_process(server)


def _time_edit(page: Page, path: Path, before: str, after: str) -> float:
    """Seconds from writing *after* over *before* in *path* to *after* showing in the page."""
    source = path.read_text(encoding="utf-8").replace(before, after)
    start = time.perf_counter()
    path.write_text(source, encoding="utf-8")
    page.wait_for_function("t => document.body.innerText.includes(t)", arg=after)
    return time.perf_counter() - start


def _open(page: Page, url: str, text: str) -> None:
    """Load *url* until *text* shows and the network is idle, so every HMR socket is connected."""
    page.goto(url)
    page.wait_for_function("t => document.body.innerText.includes(t)", arg=text)
    page.wait_for_load_state("networkidle")


def _timed_run(context: BrowserContext, app: Reload, n: int) -> float:
    """Time edit *n* in a tab of its own.

    A `.tsx` hot update stops reaching the DOM once a tab has loaded the page a second time, so
    each edit is timed in a new tab: the number is the reload of a page opened once.
    """
    page = context.new_page()
    try:
        _open(page, app.url, f"reload v{n}")
        return _time_edit(page, app.file, f"reload v{n}", f"reload v{n + 1}")
    finally:
        page.close()


def _edit_runs(context: BrowserContext, app: Reload) -> list[float]:
    """Time RUNS edits, each one replacing the text the previous edit wrote."""
    return [_timed_run(context, app, n) for n in range(RUNS)]


@pytest.mark.e2e
def test_reload_median_under_budget(
    context: BrowserContext, reload_app: Reload, request: pytest.FixtureRequest
) -> None:
    median = statistics.median(_edit_runs(context, reload_app))
    print(f"\n{request.node.callspec.id} reload: median {median * 1000:.0f} ms over {RUNS} runs")
    assert median < BUDGET_SECONDS
