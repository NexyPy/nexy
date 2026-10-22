import asyncio
import time

import pytest

from nexy.modules.runtime.hmr import HMR_MANAGER


class _FakeWS:
    async def accept(self) -> None:
        pass

    async def send_json(self, data: dict) -> None:
        pass


@pytest.mark.slow
def test_hmr_broadcast_roundtrip_under_100ms():
    """Perf claim: sub-100ms HMR broadcast (capture stub, in-process)."""
    ws = _FakeWS()
    HMR_MANAGER._connections.append(ws)

    async def _run() -> None:
        start = time.perf_counter()
        await HMR_MANAGER.broadcast_reload("page.nexy")
        return (time.perf_counter() - start) * 1000

    elapsed_ms = asyncio.run(_run())
    HMR_MANAGER._connections.clear()
    assert elapsed_ms < 100
