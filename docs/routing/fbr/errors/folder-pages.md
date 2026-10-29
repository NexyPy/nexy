# Error pages per folder

A folder can answer its own errors: a blog with a 404 in its own words, a private area that offers
the sign-in form instead of a bare `401`. The rest of the site keeps the page it already had.

This page adds one of those files and shows it answer.

## The rule

**The deepest file that matches the URL answers.** Everything else stays as it is: the same status
codes, JSON for an API client, and the built-in page once no folder of the chain has a file.

![The scopes of an error page](../../../assets/error-page-scopes.svg)

For `/blog/2024/hello` Nexy walks up the tree: `/blog/2024`, then `/blog`, then `/`. The first
folder holding a file answers. A folder is matched whole: `/blogger/hello` is not under `/blog`, so
a copy in `blog/` never answers it.

## The four files

| File | Answers | What reaches it |
|---|---|---|
| `notfound.nexy` | `404` | a URL no route matches, `notFound()` |
| `errors.nexy` | `500` | an exception nothing handled |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` stays reserved: it has no runtime effect yet.

One file somewhere in `src/routes/` is enough for Nexy to answer that status: a copy at the root
answers the whole project, a copy in a folder answers that folder, and a URL outside every copy
gets the built-in page. Reserve another extension for these names in `nexyconfig.py` with
`useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` and
`useUnauthorizedExtensions`.

## Your first folder page

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Run the project and ask for a post that does not exist:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

A URL outside the folder keeps the page you already had:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## A 401 that leads somewhere

The folder of a protected area answers `401` with the page that offers the way in:

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

Every call and every status keeps its two answers:

| Who asks | `401` with a file | `401` without one |
|---|---|---|
| Browser (`Accept: text/html`) | the page of the folder | the built-in page |
| Client (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` adds `WWW-Authenticate: Bearer` to both answers. A detail built
from user input is HTML-escaped in the page.

> [!TIP]
> `Accept: */*`, the default of `curl` and of many HTTP libraries, asks for neither and receives the
> HTML page. Add `-H "Accept: application/json"` when you want the JSON answer.

## Check it

```python filename="tests/test_private.py"
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

## Next steps

- [Error pages](README.md): what triggers each status, HTML or JSON
- [Dependencies and guards](../dependencies/README.md): protect a whole folder
- [Testing](../../../guides/testing.md): `TestClient` from the first test
