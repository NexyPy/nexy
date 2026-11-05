# WebSocket manipuladores

Lide com conexões WebSocket em um arquivo de rota `.py` definindo `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Regras

- A URL é o caminho do arquivo, mesma regra de [routing](../../README.md).
- Somente `.py` arquivos de rota registram WebSocket manipuladores via `SOCKET`.
- Certifique-se de que seu proxy reverso encaminhe WebSocket solicitações de atualização.

## Próximas etapas

- [API](../handlers/README.md): manipuladores HTTP nos mesmos arquivos
- [Implantar](../../../deployment/README.md): configuração de proxy
- [Roteamento modular](../../modular/README.md): `SOCKET` em um controlador
