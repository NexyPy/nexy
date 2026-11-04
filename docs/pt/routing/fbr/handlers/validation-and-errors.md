# Validação e erros

Como um manipulador de API relata uma solicitação incorreta.

## Validação

Os parâmetros do manipulador são validados pelo FastAPI em relação às suas anotações.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problema | Status | Corpo |
|---|---|---|
| consulta, cabeçalho, cookie ou campo de corpo ausentes ou inválidos | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| segmento **caminho** inválido (`/api/users/abc` para `id: int`) | `404` | a página não encontrada ou JSON para `Accept: application/json` |

Um segmento de caminho que não pode ser convertido é um `404` em vez de um `422`: uma rota dinâmica captura qualquer
URL e não existe um URL que não possa ser convertido.

O corpo `422` é o formato padrão do FastAPI, portanto, os clientes existentes e os SDKs gerados continuam funcionando.

## Levantando erros

```python filename="src/rotas/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Cliente envia | Resposta |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` com status `404` |
| `Accept: text/html` | a [página de erro](../errors/README.md) |
| `Accept: */*` | a página de erro |

Defina `Accept: application/json` em clientes API. Os navegadores continuam recebendo páginas.

## Exceções não tratadas

Uma exceção é que seu manipulador não captura respostas `500`, com a mesma escolha de HTML ou JSON.

## Respostas personalizadas

Retorne um objeto de resposta quando você controla o corpo:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Próximas etapas

- [Rotas de API](README.md)
- [Páginas de erro](../errors/README.md)
- [Testes](../../../guides/testing.md)