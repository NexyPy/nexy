"""Measure how fast a Nexy project starts, serves its first page and recompiles a change.

Each time is the median of several runs, each in a new Python process, on a project with one
`.nexy` page. The table it prints is what docs/deployment/performance.md publishes, and the
`Speed` workflow appends it to the summary of every run on main.

    python scripts/measure_speed.py [--runs 5]
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import subprocess  # nosec B404 - runs this interpreter on a script of this file
import sys
import tempfile
import time
from pathlib import Path

PAGE = "---\ntitle = 'Home'\n---\n<h1>{{ title }}</h1>\n"
CONFIG = (
    "from nexy.core.models import NexyConfigModel\n\n\n"
    "class NexyConfig(NexyConfigModel):\n    useVite: bool = False\n"
)
STARTUP = "from nexy.modules.routers.app import AppServer; AppServer().run()"
FIRST_PAGE = (
    "from fastapi.testclient import TestClient\n"
    "from nexy.modules.routers.app import AppServer\n"
    "assert TestClient(AppServer().run()).get('/').status_code == 200\n"
)
RECOMPILE = (
    "import time\nfrom pathlib import Path\nfrom nexy.modules.compiler import Compiler\n"
    "page = Path('src/routes/index.nexy')\n"
    "page.write_text(page.read_text().replace('Home', 'Changed'))\n"
    "started = time.perf_counter()\nCompiler().compile(input=str(page))\n"
    "print(time.perf_counter() - started)\n"
)
LABELS = {"startup": "Startup", "first_page": "First page", "recompile": "Recompile a page"}


def project(root: Path) -> Path:
    """A project with one page and no Vite, as small as `nx new` makes."""
    page = root / "src/routes/index.nexy"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(PAGE, encoding="utf-8")
    (root / "nexyconfig.py").write_text(CONFIG, encoding="utf-8")
    return root


def _run(root: Path, code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # nosec B603 - this interpreter, a script of this file
        [sys.executable, "-c", code], cwd=root, check=True, capture_output=True, text=True
    )


def _wall(root: Path, code: str) -> float:
    """Seconds from a new process to the end of *code*: the import is part of the time."""
    started = time.perf_counter()
    _run(root, code)
    return time.perf_counter() - started


def _recompile(root: Path) -> float:
    """Seconds to compile the page again after an edit, in a process that already runs."""
    project(root)
    return float(_run(root, RECOMPILE).stdout)


def measure(root: Path, runs: int = 5) -> dict[str, float]:
    """The median of *runs* runs of each measure, in seconds."""
    return {
        "startup": statistics.median(_wall(root, STARTUP) for _ in range(runs)),
        "first_page": statistics.median(_wall(root, FIRST_PAGE) for _ in range(runs)),
        "recompile": statistics.median(_recompile(root) for _ in range(runs)),
    }


def _ms(seconds: float) -> str:
    value = seconds * 1000
    return f"{value:.1f} ms" if value < 10 else f"{value:.0f} ms"


def _cpu() -> str:
    """The model name of the processor where Linux gives it, else what Python knows."""
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def machine() -> str:
    count = os.cpu_count() or 1
    return f"{_cpu()}, {platform.system()}, {count} CPUs, Python {platform.python_version()}"


def table(results: dict[str, float], where: str) -> str:
    rows = [f"| {LABELS[name]} | {_ms(seconds)} |" for name, seconds in results.items()]
    return "\n".join(["| Measure | Median |", "|---|---|", *rows, f"| Machine | {where} |", ""])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=5)
    runs = parser.parse_args().runs
    with tempfile.TemporaryDirectory() as folder:
        print(table(measure(project(Path(folder)), runs), machine()))


if __name__ == "__main__":
    main()
