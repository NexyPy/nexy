"""An island given props costs at most a little more than one without, on every request (#554).

With props, the island also looks for the build snapshot of those props: one hash and one file
lookup. Both cases run in this process, so the ratio does not depend on how fast the machine is.
"""

from __future__ import annotations

import timeit
from pathlib import Path

import pytest

from nexy.helpers.imports.ncc import NexyClientComponent

# Measured 1.13 on 2026-11-21 (AMD Ryzen 5 4500U), times about 1.5 for the noise of a CI runner.
BUDGET = 1.7
PROPS = {"label": "clicks", "count": 3, "open": True}


def _seconds(props: dict[str, object]) -> float:
    island = NexyClientComponent("src/components/spike.tsx", "react", "Spike")
    return min(timeit.repeat(lambda: island.generate(dict(props)), number=2000, repeat=5))


def test_an_island_with_props_stays_within_its_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    static = Path("__nexy__/client/static/src/components")
    static.mkdir(parents=True)
    (static / "spike.Default.html").write_text("<button>count: 0</button>", encoding="utf-8")
    assert _seconds(PROPS) / _seconds({}) < BUDGET
