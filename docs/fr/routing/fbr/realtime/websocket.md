# Gestionnaires WebSocket

Gérez les connexions WebSocket dans un fichier de route `.py` en définissant `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Règles

- L'URL est le chemin du fichier, même règle que [routage](../../README.md).
- Seuls les fichiers de route `.py` enregistrent les gestionnaires WebSocket via `SOCKET`.
- Assurez-vous que votre proxy inverse transmet les demandes de mise à niveau de WebSocket.

## Prochaines étapes

- [API](../handlers/README.md) : gestionnaires HTTP dans les mêmes fichiers
- [Déployer](../../../deployment/README.md) : configuration du proxy
- [Routage modulaire](../../modular/README.md) : `SOCKET` sur un contrôleur