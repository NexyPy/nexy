# Manipuladores WebSocket

Lide com conexões WebSocket em um arquivo de rota `.py` definindo `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Regras

- A URL é o caminho do arquivo, mesma regra do [roteamento](../../README.md).
- Apenas `.py` arquivos de rota registram manipuladores WebSocket via `SOCKET`.
- Certifique-se de que seu proxy reverso encaminhe solicitações de atualização do WebSocket.

## Próximas etapas

- [API](../handlers/README.md): manipuladores HTTP nos mesmos arquivos
- [Implantar](../../../deployment/README.md): configuração de proxy
- [Roteamento modular](../../modular/README.md): `SOCKET` em um controlador