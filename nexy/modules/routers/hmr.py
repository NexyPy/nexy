from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from nexy.modules.runtime.hmr import HMR_MANAGER


def setup_hmr(server: FastAPI) -> None:
    """Setup WebSocket for Hot Module Replacement in development."""

    @server.websocket("/_nexy/hmr")
    async def hmr_endpoint(websocket: WebSocket) -> None:
        if not await HMR_MANAGER.connect(websocket):
            return
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            HMR_MANAGER.disconnect(websocket)
