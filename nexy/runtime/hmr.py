import asyncio
from typing import Any

from fastapi import WebSocket


class HMRManager:
    _instance = None
    _connections: list[WebSocket] = []
    loop: asyncio.AbstractEventLoop | None = None

    def __new__(cls) -> "HMRManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        # Capture the running loop at connect time. Capturing at import time
        # points to a loop that may never run (uvicorn creates its own loop).
        self.loop = asyncio.get_running_loop()
        self._connections.append(websocket)

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
