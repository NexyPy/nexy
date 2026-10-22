import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

SSG_ENTRIES = [
    "excludes.ts",
    "entries.ts",
    "ssg.ts",
    "ssg.html.ts",
    "ssg.react.ts",
    "ssg.preact.ts",
    "ssg.solid.ts",
    "ssg.vue.ts",
    "ssg.svelte.ts",
    "utils.ts",
]


def _scaffold_project(tmp_path: Path) -> Path:
    routes = tmp_path / "src" / "routes"
    routes.mkdir(parents=True)
    for i in range(30):
        (routes / f"page{i}.tsx").write_text(
            "import React from 'react'\n"
            f"export default function Page{i}() {{ return <div>Page {i}</div> }}",
            encoding="utf-8",
        )
    (routes / "index.tsx").write_text(
        "import React from 'react'\nexport default function Home() { return <h1>Home</h1> }",
        encoding="utf-8",
    )

    scripts = tmp_path / "__nexy__" / "scripts"
    scripts.mkdir(parents=True)
    source = REPO_ROOT / "nexy" / "frontend" / "scripts"
    for name in SSG_ENTRIES:
        shutil.copy(source / name, scripts / name)

    manifest_dir = tmp_path / "__nexy__" / "client" / ".vite"
    manifest_dir.mkdir(parents=True)
    entries = {
        f"src/routes/page{i}.tsx": {"file": f"assets/page{i}.js", "css": []}
        for i in range(30)
    }
    entries["src/routes/index.tsx"] = {"file": "assets/index.js", "css": []}
    (manifest_dir / "manifest.json").write_text(json.dumps(entries), encoding="utf-8")
    return tmp_path


# The benchmark shells out to `node --import tsx` with react/vite installed:
# it requires the JS toolchain under repo-root node_modules/. That dependency
# was removed from the repo by the cleanup decision (QUALITY_PLAN 6.5) - skip
# rather than fail while the environment is absent (restore it to run).

@pytest.mark.slow
@pytest.mark.skipif(
    not (REPO_ROOT / "node_modules").exists(),
    reason="requires the JS toolchain (node_modules with tsx/react/vite) removed from the repo root by cleanup - restore the environment to run this benchmark",
)
def test_ssg_completes_under_sanity_ceiling(tmp_path: Path) -> None:
    """Perf claim: static generation of 31 routes finishes in a bounded time.

    Threshold (documented): a 31-route SSG pass must stay under 60s. The exact
    budget depends on the machine; this guards against gross regressions such
    as accidental serialization of the render loop.
    """
    project = _scaffold_project(tmp_path)
    node_modules = REPO_ROOT / "node_modules"
    if not (project / "node_modules").exists():
        os.symlink(node_modules, project / "node_modules", target_is_directory=True)

    start = time.perf_counter()
    result = subprocess.run(
        ["node", "--import", "tsx", "__nexy__/scripts/ssg.ts"],
        cwd=project,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start

    report_path = project / "__nexy__" / "client" / "ssg-report.json"
    assert result.returncode == 0, result.stderr[-2000:]
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "timingMs" in report
    assert elapsed < 60
