# WebSocket handlers

Handle WebSocket connections in a `.py` route file by defining `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Rules

- The URL is the file path, same rule as [routing](../../README.md).
- Only `.py` route files register WebSocket handlers via `SOCKET`.
- Make sure your reverse proxy forwards WebSocket upgrade requests.

## Next steps

- [API](../handlers/README.md): HTTP handlers in the same files
- [Deploy](../../../deployment/README.md): proxy configuration
- [Modular routing](../../modular/README.md): `SOCKET` on a controller
