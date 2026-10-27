import asyncio
from typing import Any

from fastapi import WebSocket

# More browsers than this on one dev server is a leak or abuse; the extra ones are turned away.
MAX_CONNECTIONS = 32
_TRY_AGAIN_LATER = 1013


class HMRManager:
    """The browsers listening for reloads and compile errors (development only)."""

    _instance: "HMRManager | None" = None
    _connections: list[WebSocket]
    loop: asyncio.AbstractEventLoop | None

    def __new__(cls) -> "HMRManager":
        if cls._instance is None:
            instance = super().__new__(cls)
            instance._connections = []
            instance.loop = None
            cls._instance = instance
        return cls._instance

    async def connect(self, websocket: WebSocket) -> bool:
        """Accept *websocket* and keep it; False (and closed) when there are too many."""
        if len(self._connections) >= MAX_CONNECTIONS:
            await websocket.close(code=_TRY_AGAIN_LATER)
            return False
        await websocket.accept()
        self.loop = asyncio.get_running_loop()
        self._connections.append(websocket)
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)

    async def _send(self, websocket: WebSocket, path: str) -> None:
        try:
            await websocket.send_json({"type": "nexy:reload", "path": path})
        except Exception:
            self.disconnect(websocket)

    async def _send_error(self, websocket: WebSocket, errors: list[dict[str, Any]]) -> None:
        try:
            await websocket.send_json({"type": "nexy:error", "errors": errors})
        except Exception:
            self.disconnect(websocket)

    async def broadcast_reload(self, path: str = "") -> None:
        """Sends a reload signal to all connected clients."""
        connections = list(self._connections)
        await asyncio.gather(*(self._send(ws, path) for ws in connections))

    async def broadcast_error(self, errors: list[dict[str, Any]]) -> None:
        """Sends compile errors to all connected clients (browser overlay)."""
        connections = list(self._connections)
        await asyncio.gather(*(self._send_error(ws, errors) for ws in connections))


HMR_MANAGER = HMRManager()
