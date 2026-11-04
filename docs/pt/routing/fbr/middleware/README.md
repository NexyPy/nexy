# Arquivos de middleware

Um `middleware.py` em um diretório de rotas agrupa as solicitações tratadas por esse diretório. Como layouts e
`dependencies.py`, os arquivos são empilhados da raiz para baixo, as mais externas primeiro.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

A função é `async def middleware(request, call_next)`: a assinatura do FastAPI's
`@app.middleware("http")`. Ligue para `await call_next(request)` para continuar a rota ou retorne um
resposta para parar por aí. O código após a chamada é executado na saída e pode alterar a resposta.

## O que envolve

Um middleware se aplica às **rotas cujo arquivo está em seu diretório** ou abaixo, páginas e API
manipuladores, grupos de rotas incluídos:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

Para uma solicitação para `/admin/users` a ordem é `root`, `admin`, `users`, depois a rota. Um grupo não tem
URL próprio, portanto, é correspondido por meio da rota que atende a solicitação, e não por meio do URL.

Uma URL que não corresponde a nenhuma rota (a 404) recebe apenas o middleware de diretórios que não são grupos,
selecionado por prefixo de URL. `[slug]` corresponde a um segmento e `[...rest]` corresponde ao restante.

## O que não envolve

- Estrutura e URLs de ativos: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` e `/@...` (Vite).
- Manipuladores WebSocket e vida útil do servidor: apenas solicitações HTTP.
- Arquivos em diretórios começando com `_` ou `.`.

## Middleware, dependências ou guardas

| Use | quando |
|---|---|
| `middleware.py` | você também precisa da **resposta**: cabeçalhos, redirecionamentos, tempo, curto-circuito para uma área inteira |
| [`dependencies.py`](../dependencies/README.md) | você precisa de parâmetros analisados ou para injetar um valor (usuário atual, sessão de banco de dados) |
| `@UseGuard` em um manipulador | uma rota precisa de uma verificação extra |
| `useMiddlewares` em [config](../../../reference/config.md) | um middleware ASGI para toda a aplicação (CORS, GZip, sessões) |

Arquivos de middleware são executados **antes de** dependências: a solicitação passou em cada `middleware.py` de suas
diretórios quando as dependências são iniciadas.

## Regras

- O arquivo deve definir `async def middleware(request, call_next)`. Caso contrário, o Nexy para na inicialização e
  nomeia o arquivo.
- É um módulo Python normal: importe o que você precisa. Ele é carregado uma vez, quando o servidor é iniciado.
- Nunca é uma rota: `/middleware` é um 404.
- O caminho base verifica em `request.scope["path"]`, nunca em `request.url.path` ou no cabeçalho `Host`: desde
  CVE-2026-48710 o objeto URL pode discordar do caminho que o servidor recebeu. Veja
  [Segurança](../../../reference/security.md).

## Custo

Um projeto sem `middleware.py` não paga nada: a camada não está instalada. Com arquivos, cada
middleware correspondente adiciona um Starlette `BaseHTTPMiddleware`; mantenha-os pequenos.

## Próximas etapas

- [Herança](../inheritance.md)
- [Dependências](../dependencies/README.md)
- [Middleware e segurança](../../../guides/middleware-and-security.md)