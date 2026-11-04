# Exceções e erros

Uma solicitação pode falhar em quatro lugares e o Nexy responde a cada um de maneira diferente. Esta página é o índice:
encontre o status que você vê, depois a linha que o produziu e, a seguir, o arquivo que decide o corpo.

> [!NOTA]
> Três coisas são separadas e fáceis de confundir: a **resposta HTTP** (um status e um corpo), o
> **página de erro** (`notfound.nexy`, `errors.nexy`) e a **linha de log** (o que você lê no
> terminal). Alterar a página não altera o status e personalizar a página não oculta
> o registro.

## A versão curta

| O que aconteceu | Status | Navegador vê | Cliente API vê |
|---|---|---|---|
| nenhuma rota corresponde ao URL | `404` | `notfound.nexy`, caso contrário, a página interna | `{"detail": "Not Found"}` |
| um segmento de caminho não cabe em sua anotação | `404` | a mesma página | `{"detail": "Not Found"}` |
| uma consulta, cabeçalho, cookie ou campo de corpo está faltando ou é inválido | `422` | Corpo JSON do FastAPI | Corpo JSON do FastAPI |
| `notFound()` | `404` | a página | `{"detail": ...}` |
| `unauthorized()` | `401` | a página integrada | `{"detail": ...}` |
| `forbidden()` | `403` | a página integrada | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | a página interna | `{"detail": ...}` |
| uma exceção, nada capturado | `500` | `errors.nexy`, caso contrário, a página interna | `{"detail", "reference"}` |
| `redirect(url)` | `307` | o destino, sem página | o destino, sem corpo |
| `permanentRedirect(url)` | `308` | o destino, sem página | o destino |

Um cliente API é uma solicitação cujo cabeçalho `Accept` pede JSON e não uma página:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!AVISO]
> `curl` envia `Accept: */*` por padrão, que obtém a página HTML. Adicionar
> `-H "Accept: application/json"` ao testar a forma JSON. Os navegadores continuam recebendo páginas.

## De onde vem uma falha

```diagram filename="Um pedido, quatro saídas"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Estágio | O que pode falhar | A resposta |
|---|---|---|
| Middleware | seu `middleware.py`, CORS, sessões | o status da exceção, caso contrário `500` |
| Roteador | o URL não corresponde a nenhum arquivo | `404` |
| Validação | um segmento de caminho não pode ser convertido | `404` |
| Validação | uma consulta, cabeçalho, cookie ou campo de corpo | `422` |
| Página, manipulador, ação, guarda | `HTTPException` | seu status |
| Página, manipulador, ação, guarda | qualquer outra coisa | `500` |

## Saia de qualquer lugar

`redirect`, `permanentRedirect`, `notFound`, `forbidden` e `unauthorized` levantam uma exceção HTTP,
então a mesma chamada funciona em uma página `.nexy`, um manipulador de API, um controlador modular, um guarda, um
`dependencies.py` e uma ação.

```python filename="src/rotas/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```

| Ligar | Atender | Quando |
|---|---|---|
| `notFound(detail=None)` | `404` | o recurso não existe |
| `unauthorized(detail=None, scheme=None)` | `401` | o visitante deve fazer login primeiro |
| `forbidden(detail=None)` | `403` | o visitante é conhecido, mas pode não ver isso |
| `redirect(url, status=307)` | `307` | envie-os para outro lugar, mantendo o método |
| `redirect(url, status=303)` | `303` | após um formulário: a próxima solicitação é um `GET` |
| `permanentRedirect(url)` | `308` | uma página movida que os mecanismos de pesquisa devem lembrar |

Construa o destino a partir de valores em que você confia. `redirect(request.query_params["next"])` envia visitantes
onde quer que o link diga; é um redirecionamento aberto. Um destino que contém uma quebra de linha é recusado.

## Validação: 422 ou 404

Os parâmetros do manipulador são validados pelo FastAPI em relação às suas anotações.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problema | Status | Por que |
|---|---|---|
| consulta, cabeçalho, cookie ou campo de corpo ausentes ou inválidos | `422` | a solicitação chegou ao manipulador, os dados estão errados |
| segmento de caminho inválido (`/api/users/abc` para `id: int`) | `404` | a pasta não tem rota para um não-número, então o URL não existe |

O corpo `422` é o formato padrão do FastAPI, então os clientes e SDKs gerados continuam funcionando:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Para um formulário ou ação, o cliente recebe um `ActionError` com `status` e `detail`; um `422`
também preenche `error.fields` com uma mensagem por campo. Consulte [Ações](../guides/actions.md#errors-and-failures).

> [!DICA]
> Validar na assinatura quando a regra for sobre um campo (`limit: int = 10`). Valide no
> body quando a regra precisa do banco de dados ou outro campo ("este e-mail já está em uso"): raise
> `HTTPException(409)` e guarde a mensagem para o cliente.

## Páginas de erro personalizadas

```nexy filename="src/rotas/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/rotas/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| Arquivo | Status | Escopo |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | todas as rotas do projeto |
| `src/routes/errors.nexy` | `500` | todas as rotas do projeto |
| `src/routes/forbidden.nexy` | `403` | todas as rotas do projeto |
| `src/routes/unauthorized.nexy` | `401` | todas as rotas do projeto |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` e abaixo de |
| `src/routes/blog/errors.nexy` | `500` | `/blog` e abaixo de |
| `src/routes/loading.nexy` | - | reservado, nenhum efeito de tempo de execução ainda |

Um arquivo em algum lugar nas rotas instala a resposta para seu status: uma cópia na raiz responde ao
todo o projeto, uma cópia em uma pasta responde a essa pasta e o arquivo mais profundo que corresponde ao URL
vence. Um URL fora de cada cópia e um status sem nenhum arquivo obtêm as páginas com estilo integrado.
Consulte [Páginas de erro por pasta](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANTE]
> Uma página `errors.nexy` substitui a página `500`; ele não captura a exceção e não
> altere a linha do log. Se o manipulador gerado for a própria página, a página não poderá mostrar sua própria
>  detalhes do erro: mantenha `errors.nexy` simples e independente.

## Exceções não tratadas

Uma exceção que nada capturado é logado uma vez, com sua referência, de onde veio e o código
em torno disso. O status é `500` e o corpo depende do ambiente.

| | `nexy dev` | `nexy build` então `nexy start` |
|---|---|---|
| Navegador | o erro, as linhas do seu código e o traceback | `errors.nexy`, caso contrário a página interna, com uma referência |
| Cliente API | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | a exceção e as linhas do seu código | a exceção, todo o traceback e a referência |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

A referência são oito caracteres, novos para cada falha. Um visitante pode citá-lo e você encontrará o
traceback pesquisando o log por ele. Nem a exceção nem o código chegam ao visitante em
produção.

> [!CUIDADO]
> Não retorne o rastreamento para um visitante em produção e não coloque segredos em um erro
> mensagem: o `detail` de um `HTTPException` é enviado ao cliente, com escape HTML. Coloque o segredo
> no log, não na resposta.

## Ações e formulários

Uma ação é um endpoint `POST` com um caminho gerado. Suas falhas seguem as mesmas regras:

| Situação | Status | Cliente |
|---|---|---|
| um campo está faltando ou é inválido | `422` | `ActionError` com `fields` |
| `HTTPException(403)` suscitada na ação | `403` | `ActionError` com `status` e `detail` |
| uma exceção não tratada | `500` | `ActionError`; a referência está no log do servidor |
| o cabeçalho `Origin` é outro site | `403` | recusado antes da ação ser executada |

Um formulário sem JavaScript posta no caminho da ação; um sucesso responde `303` de volta à página, um
falha mostra a página de erro. Consulte [Ações](../guides/actions.md#forms-without-javascript).

## Uma lista de verificação quando uma página responde à coisa errada

1. **Observe o status**, não a página. Um `notfound.nexy` personalizado ainda responde `404`.
2. **Leia o terminal.** Uma página que falha na importação não é registrada, então seu URL responde `404`
   enquanto o arquivo existir. O erro de importação está no log.
3. **Verifique a extensão.** Com `useCSR = True`, `.nexy` as páginas pertencem ao modo servidor; uma página no
   o modo errado não é uma rota.
4. **Verifique a profundidade.** Um `notfound.nexy` ou `errors.nexy` só funciona quando a cópia raiz existe.
5. **Peça JSON** com `Accept: application/json` para ver a forma que seu cliente API recebe.
6. **Cite a referência** de um `500` ao abrir um problema ou pesquisar no log.

## Próximas etapas

- [Páginas de erro](../routing/fbr/errors/README.md): o comportamento da página inteira, com exemplos
- [Validação e erros](../routing/fbr/handlers/validation-and-errors.md): manipuladores de API
- [Solução de problemas](../guides/troubleshooting.md): os erros que as pessoas realmente encontraram
- [Teste](../guides/testing.md): afirmar um status e um corpo