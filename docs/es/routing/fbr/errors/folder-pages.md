# Páginas de error por carpeta

Una carpeta puede responder a sus propios errores: un blog con un 404 en sus propias palabras, un área privada que ofrece el formulario de inicio de sesión en lugar de un simple `401`. El resto del sitio mantiene la página que ya tenía.

Esta página agrega uno de esos archivos y muestra su respuesta.

## la regla

**El archivo más profundo que coincide con la URL responde.** Todo lo demás permanece como está: los mismos códigos de estado, JSON para un cliente API y la página incorporada una vez que ninguna carpeta de la cadena tiene un archivo.

![Los alcances de una página de error](../../../assets/error-page-scopes.svg)

Para `/blog/2024/hello` Nexy sube al árbol: `/blog/2024`, luego `/blog`, luego `/`. La primera carpeta que contiene un archivo responde. Una carpeta coincide completa: `/blogger/hello` no está en `/blog`, por lo que una copia en `blog/` nunca responde.

## Los cuatro archivos

| Archivo | Respuestas | Lo que le llega |
|---|---|---|
| `notfound.nexy` | `404` | una URL sin coincidencias de ruta, `notFound()` |
| `errors.nexy` | `500` | una excepción, nada manejado |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` permanece reservado: aún no tiene efecto de tiempo de ejecución.

Un archivo en algún lugar de `src/routes/` es suficiente para que Nexy responda a ese estado: una copia en la raíz responde a todo el proyecto, una copia en una carpeta responde a esa carpeta y una URL fuera de cada copia obtiene la página incorporada. Reserve otra extensión para estos nombres en `nexyconfig.py` con `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` y `useUnauthorizedExtensions`.

## Tu primera página de carpeta

```nexy filename="src/rutas/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Ejecute el proyecto y solicite una publicación que no existe:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

Una URL fuera de la carpeta mantiene la página que ya tenía:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## Un 401 que lleva a alguna parte

La carpeta de un área protegida responde `401` con la página que ofrece la forma de entrar:

```nexy filename="src/rutas/privado/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/rutas/privado/dependencias.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Cada llamada y cada estado conserva sus dos respuestas:

| Quien pregunta | `401` con un expediente | `401` sin uno |
|---|---|---|
| Navegador (`Accept: text/html`) | la página de la carpeta | la página incorporada |
| Cliente (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` agrega `WWW-Authenticate: Bearer` a ambas respuestas. Un detalle creado a partir de la entrada del usuario tiene un formato de escape HTML en la página.

> [!TIP]
> `Accept: */*`, el valor predeterminado de `curl` y de muchas bibliotecas HTTP, no solicita ninguna de las dos cosas y recibe la página HTML. Agregue `-H "Accept: application/json"` cuando desee la respuesta JSON.

## Compruébalo

```python filename="pruebas/test_private.py"
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

## Próximos pasos

- [Páginas de error](README.md): qué activa cada estado, HTML o JSON
- [Dependencias y guardias](../dependencies/README.md): protege una carpeta completa
- [Prueba](../../../guides/testing.md): `TestClient` de la primera prueba
