import asyncio

from nexy.modules.runtime.hmr import HMR_MANAGER


class _FakeWS:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.accepted = False
        self.sent_json_calls = 0

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, data: dict) -> None:
        self.sent_json_calls += 1
        self.sent.append(data)

    async def receive_text(self) -> str:
        return ""


def _reset():
    HMR_MANAGER._connections.clear()
    HMR_MANAGER.loop = None


def test_loop_captured_at_connect():
    _reset()

    async def _run() -> None:
        ws = _FakeWS()
        await HMR_MANAGER.connect(ws)
        assert HMR_MANAGER.loop is asyncio.get_running_loop()
        HMR_MANAGER.disconnect(ws)

    asyncio.run(_run())


def test_broadcast_gathers_and_disconnects_broken_sockets():
    _reset()
    ok = _FakeWS()
    broken = _FakeWS()

    async def _boom(_data):
        raise RuntimeError("gone")

    broken.send_json = _boom

    HMR_MANAGER._connections.extend([ok, broken])

    async def _run() -> None:
        await HMR_MANAGER.broadcast_reload("page.nexy")
        assert ok.sent == [{"type": "nexy:reload", "path": "page.nexy"}]
        assert broken not in HMR_MANAGER._connections
        assert ok in HMR_MANAGER._connections

    asyncio.run(_run())


def test_broadcast_error_emits_nexy_error_message():
    _reset()
    ws = _FakeWS()
    HMR_MANAGER._connections.append(ws)

    async def _run() -> None:
        await HMR_MANAGER.broadcast_error([{"file": "page.nexy", "message": "boom"}])
        assert ws.sent == [
            {"type": "nexy:error", "errors": [{"file": "page.nexy", "message": "boom"}]}
        ]

    asyncio.run(_run())
