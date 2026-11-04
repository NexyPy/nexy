# Manejadores WebSocket

Maneje las conexiones WebSocket en un archivo de ruta `.py` definiendo `SOCKET`.

```python filename="src/rutas/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Reglas

- La URL es la ruta del archivo, la misma regla que [enrutamiento](../../README.md).
- Solo los archivos de ruta `.py` registran controladores WebSocket a través de `SOCKET`.
- Asegúrese de que su proxy inverso reenvíe las solicitudes de actualización de WebSocket.

## Próximos pasos

- [API](../handlers/README.md): controladores HTTP en los mismos archivos
- [Implementar](../../../deployment/README.md): configuración de proxy
- [Enrutamiento modular](../../modular/README.md): `SOCKET` en un controlador