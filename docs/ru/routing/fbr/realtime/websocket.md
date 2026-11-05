# WebSocket обработчики

Обработайте соединения WebSocket в файле маршрута `.py`, определив `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Правила

- URL-адрес — это путь к файлу, то же правило, что и [routing](../../README.md).
- Только `.py` файлы маршрутов регистрируют обработчики WebSocket через `SOCKET`.
- Убедитесь, что ваш обратный прокси-сервер пересылает WebSocket запросы на обновление.

## Следующие шаги

- [API](../handlers/README.md): обработчики HTTP в тех же файлах.
- [Развертывание](../../../deployment/README.md): конфигурация прокси-сервера
- [Модульная маршрутизация](../../modular/README.md): `SOCKET` на контроллере
