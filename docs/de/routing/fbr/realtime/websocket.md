# WebSocket-Handler

Behandeln Sie WebSocket-Verbindungen in einer `.py`-Routendatei, indem Sie `SOCKET` definieren.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Regeln

- Die URL ist der Dateipfad, dieselbe Regel wie beim [Routing](../../README.md).
- Nur `.py` Routendateien registrieren WebSocket-Handler über `SOCKET`.
- Stellen Sie sicher, dass Ihr Reverse-Proxy WebSocket-Upgrade-Anfragen weiterleitet.

## Nächste Schritte

- [API](../handlers/README.md): HTTP-Handler in denselben Dateien
- [Bereitstellen](../../../deployment/README.md): Proxy-Konfiguration
- [Modulares Routing](../../modular/README.md): `SOCKET` auf einem Controller