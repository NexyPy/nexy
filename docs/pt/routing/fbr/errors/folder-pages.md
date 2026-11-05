# Páginas de erro por pasta

Uma pasta pode responder aos seus próprios erros: um blog com um 404 em suas próprias palavras, uma área privada que oferece o formulário de login em vez de um simples `401`. O resto do site mantém a página que já possuía.

Esta página adiciona um desses arquivos e mostra a resposta.

## A regra

**O arquivo mais profundo que corresponde à URL responde.** Todo o resto permanece como está: os mesmos códigos de status, JSON para um cliente API e a página integrada, uma vez que nenhuma pasta da cadeia possui um arquivo.

![Os escopos de uma página de erro](../../../assets/error-page-scopes.svg)

Para `/blog/2024/hello` Nexy sobe na árvore: `/blog/2024`, depois `/blog`, depois `/`. A primeira pasta contendo um arquivo responde. Uma pasta é correspondida inteira: `/blogger/hello` não está abaixo de `/blog`, então uma cópia em `blog/` nunca responde.

## Os quatro arquivos

| Arquivo | Respostas | O que chega até ele |
|---|---|---|
| `notfound.nexy` | `404` | um URL sem correspondência de rota, `notFound()` |
| `errors.nexy` | `500` | uma exceção, nada tratado |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` permanece reservado: ainda não tem efeito de execução.

Um arquivo em algum lugar em `src/routes/` é suficiente para Nexy responder a esse status: uma cópia na raiz responde a todo o projeto, uma cópia em uma pasta responde a essa pasta e uma URL fora de cada cópia obtém a página interna. Reserve outra extensão para esses nomes em `nexyconfig.py` com `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` e `useUnauthorizedExtensions`.

## Sua primeira página de pasta

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Execute o projeto e peça um post que não existe:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

Uma URL fora da pasta mantém a página que você já tinha:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## Um 401 que leva a algum lugar

A pasta de uma área protegida responde `401` com a página que oferece o caminho para entrar:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Cada chamada e cada status mantém suas duas respostas:

| Quem pergunta | `401` com um arquivo | `401` sem um |
|---|---|---|
| Navegador (`Accept: text/html`) | a página da pasta | a página interna |
| Cliente (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` adiciona `WWW-Authenticate: Bearer` a ambas as respostas. Um detalhe criado a partir da entrada do usuário tem escape de HTML na página.

> [!TIP]
> `Accept: */*`, o padrão de `curl` e de muitas bibliotecas HTTP, não solicita nenhuma delas e recebe a página HTML. Adicione `-H "Accept: application/json"` quando quiser a resposta JSON.

## Verifique

```python filename="testes/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## Próximas etapas

- [Páginas de erro](README.md): o que aciona cada status, HTML ou JSON
- [Dependências e guardas](../dependencies/README.md): protege uma pasta inteira
- [Teste](../../../guides/testing.md): `TestClient` desde o primeiro teste
