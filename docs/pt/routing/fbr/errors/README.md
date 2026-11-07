# Páginas de erro

Uma solicitação que falha ainda deve responder como o resto do seu site: uma página com suas próprias palavras para um visitante, a mesma falha que JSON para um cliente API. Nexy responde a ambas e um arquivo substitui cada resposta.

Esta página é o mapa: qual arquivo responde qual status e como fazer o primeiro. As páginas de uma pasta obtêm [sua própria página](folder-pages.md).

## Uma falha, duas respostas

```diagram filename="quem responde a uma solicitação falhada"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Sua primeira página

Crie `src/routes/notfound.nexy` e escreva o que um visitante deve ler:

```nexy filename="src/rotas/notfound.nexy"
---
metadata = {"title": "Page not found"}
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Salve e peça uma URL que nada serve:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

O arquivo na raiz das rotas responde a todo o projeto; uma cópia em uma pasta responde apenas a essa pasta e [mantém o resto como está](folder-pages.md). Sem nenhum arquivo, o Nexy exibe sua página com estilo integrado.

## Qual arquivo responde

| Arquivo | Respostas |
|---|---|
| `notfound.nexy` | `404` para seu diretório |
| `errors.nexy` | `500` para seu diretório |
| `forbidden.nexy` | `403` para seu diretório |
| `unauthorized.nexy` | `401` para seu diretório |
| `loading.nexy` | reservado; nenhum efeito de tempo de execução ainda |

| Situação | Resposta |
|---|---|
| Nenhuma rota corresponde | `404` |
| Um segmento dinâmico não pode ser convertido em sua anotação | `404` |
| Uma exceção não tratada, em uma página ou manipulador de API | `500` |
| `raise HTTPException(status_code=403)` | o status que você levantou, como HTML ou JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, de qualquer lugar em uma solicitação |
| `redirect()`, `permanentRedirect()` | um redirecionamento real sem página de erro |

## Deixe uma página ou responda do código

`redirect`, `permanentRedirect`, `notFound`, `forbidden` e `unauthorized` levantam uma exceção HTTP, então a mesma chamada funciona em uma página `.nexy`, um manipulador de API, um controlador modular, um guarda e um `dependencies.py`. Eles têm os mesmos nomes no cliente (`@nexy/client`).

```nexy filename="src/rotas/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Ligar | Resposta |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` transforma um POST em um GET após um formulário |
| `permanentRedirect(url)` | `308`; navegadores e mecanismos de pesquisa lembram disso |
| `notFound(detail=None)` | `404`: a página `notfound` ou JSON para um cliente API |
| `forbidden(detail=None)` | `403`: o visitante é conhecido, mas pode não ver isso |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` adiciona `WWW-Authenticate` |

Um redirecionamento responde com o cabeçalho `Location` e sem página, também para um cliente API. Construa o destino a partir de valores em que você confia: um `redirect(request.query_params["next"])` envia visitantes para onde o link indicar. Um destino com quebra de linha é recusado.

Um guarda protege uma pasta inteira:

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML ou JSON

A mesma exceção responde de forma diferente dependendo de quem pergunta:

- Um navegador (`Accept: text/html`) obtém uma página HTML. O detalhe tem escape de HTML, portanto, uma mensagem criada a partir da entrada do usuário não pode injetar marcação.
- Um cliente que solicita JSON e não uma página (`Accept: application/json`) obtém `{"detail": "..."}` com o mesmo código de status.

```python filename="src/rotas/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!NOTE]
> um cliente que envia `Accept: */*` (o padrão de `curl` e muitas bibliotecas HTTP) recebe a página HTML. Defina `Accept: application/json` para erros JSON.

## Exceções não tratadas

Uma exceção de que nada tratado é registrado uma vez, com exceção de onde veio e o código ao seu redor, e respondido de acordo com o modo.

| | `nx dev` | `nx start` |
|---|---|---|
| Navegador | uma página com o erro, as linhas do seu código que o geraram e o traceback completo | a página interna `500` (ou sua `errors.nexy`) com uma referência |
| Cliente JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Registro do servidor | a exceção e as linhas do seu código | a exceção e todo o traceback, com a mesma referência |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

A referência são oito caracteres, novos para cada falha. Um visitante pode citá-lo e você encontrará o rastreamento pesquisando-o no log. Nem a exceção nem o código chegam ao visitante em produção. Um `errors.nexy` personalizado substitui apenas a página; a linha de log permanece.

## Erros de validação

Um cabeçalho, parâmetro de consulta ou campo de corpo ausente responde `422` com o corpo JSON de FastAPI, para cada cliente. Consulte [Validação e erros](../handlers/validation-and-errors.md).

## Próximas etapas

- [Páginas de erro por pasta](folder-pages.md): um 404, 403 ou 401 de sua preferência em uma pasta
- [Rotas dinâmicas](../pages/dynamic-routes.md)
- [Rotas de API](../handlers/README.md)
- [Teste](../../../guides/testing.md)
