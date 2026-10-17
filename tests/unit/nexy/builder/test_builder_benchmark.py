import time

import pytest

from nexy.builder import Builder


@pytest.mark.slow
def test_builder_completes_under_sanity_ceiling() -> None:
    """Perf claim: builds finish fast enough to keep the DX promise.

    Threshold (documented): cold build of the workspace must stay under 60s.
    The exact budget depends on the machine and route count; this guards
    against gross regressions (e.g. accidental serialization).
    """
    builder = Builder()
    start = time.perf_counter()
    result = builder.build(showlog=False, incremental=False)
    elapsed = time.perf_counter() - start

    assert result.success
    assert elapsed < 60
