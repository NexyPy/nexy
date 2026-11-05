# Manipuladores de rota

Um arquivo `.py` em `src/routes/` é um manipulador de API. O caminho do arquivo é o URL e cada função nomeada após um método HTTP se torna um terminal.

## Crie um ponto final

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Este arquivo responde `GET /api/items` e `POST /api/items`.

Nomes de funções suportadas: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` abre um WebSocket no mesmo caminho - veja [WebSocket](../realtime/websocket.md).

## O vocabulário HTTP

Importe o que um manipulador precisa de `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Ele expõe as classes de solicitação e resposta (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), as fontes de parâmetros (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` e `status`. Os manipuladores escritos neste módulo dependem do contrato da Nexy, não do mecanismo que os atende. Pydantic modelos descrevem corpos e respostas como de costume.

## Parâmetros

| Fonte | Como chega |
|---|---|
| Segmento de caminho `[id]` | argumento de função `id`, convertido em sua anotação |
| Sequência de consulta | `page: int = 1` |
| Corpo JSON | Pydantic argumento do modelo |
| FastAPI primitivas | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - inalteradas |

```python filename="src/rotas/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

O segmento do caminho é `{id}`, então FastAPI valida `id: int`. Um valor que não é um número inteiro responde `404`, porque uma rota dinâmica captura qualquer URL e uma URL que não pode ser convertida não existe. Consulte [Validação e erros](validation-and-errors.md).

## Respostas

| Retornar | Resposta |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, qualquer `Response` | exatamente como declarado |
| `None` | resposta vazia - retorne um `Response` quando o status for importante |

Para um código de status ou tipo de conteúdo personalizado, retorne um objeto de resposta:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Erros

Levante FastAPI exceções para clientes. Um cliente que envia `Accept: application/json` recebe `{"detail": "..."}` com o status que você levantou; um navegador recebe a página de erro. `notfound.nexy` renderiza `404` e `errors.nexy` renderiza `500`, cada um com escopo em seu diretório. Consulte [Validação e erros](validation-and-errors.md) e [Páginas de erro](../errors/README.md).

## OpenAPI

Cada rota da API aparece no esquema gerado, porque as rotas são rotas simples FastAPI. O esquema é servido em `/openapi.json` e renderizado por Scalar em `/docs`. Desative ambos com `useDocs = False` em `nexyconfig.py`.

## Próximas etapas

- [Dependências](../dependencies/README.md): autenticação e configuração compartilhadas por manipulador ou por diretório
- [Validação e erros](validation-and-errors.md): `422`, `404` e erros JSON
- [Roteamento](../../README.md): caminho do arquivo para URL
- [Ações](../../../guides/actions.md): endpoints com caminhos gerados
- [Configuração](../../../reference/config.md): middleware, CORS, sessões
