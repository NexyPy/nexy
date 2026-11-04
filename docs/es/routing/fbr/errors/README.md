# Páginas de error

Una solicitud que falla debería responder como el resto de su sitio: una página con sus propias palabras para un
visitante, el mismo error que JSON para un cliente API. Nexy responde a ambas y un archivo reemplaza cada una
respuesta.

Esta página es el mapa: qué archivo responde a qué estado y cómo crear el primero. las paginas de
una carpeta obtiene [su propia página](folder-pages.md).

## Un fracaso, dos respuestas

```diagram filename="quién responde una solicitud fallida"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Tu primera página

Crea `src/routes/notfound.nexy` y escribe lo que un visitante debe leer:

```nexy filename="src/rutas/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Guarde y solicite una URL que no sirve:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

El archivo en la raíz de rutas responde a todo el proyecto; una copia en una carpeta responde solo a esa carpeta
y [mantiene el resto como está](folder-pages.md). Sin ningún archivo, Nexy ofrece su estilo incorporado
página.

## ¿Qué archivo responde?

| Archivo | Respuestas |
|---|---|
| `notfound.nexy` | `404` para su directorio |
| `errors.nexy` | `500` para su directorio |
| `forbidden.nexy` | `403` para su directorio |
| `unauthorized.nexy` | `401` para su directorio |
| `loading.nexy` | reservado; aún no hay efecto de tiempo de ejecución |

| Situación | Respuesta |
|---|---|
| Ninguna ruta coincide | `404` |
| Un segmento dinámico no se puede convertir a su anotación | `404` |
| Una excepción no controlada, en una página o en un controlador API | `500` |
| `raise HTTPException(status_code=403)` | el estado que planteaste, como HTML o JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, desde cualquier lugar de una solicitud |
| `redirect()`, `permanentRedirect()` | una redirección real sin página de error |

## Deja una página o responde desde el código

`redirect`, `permanentRedirect`, `notFound`, `forbidden` y `unauthorized` generan una excepción HTTP,
entonces la misma llamada funciona en una página `.nexy`, un controlador API, un controlador modular, un guardia y un
`dependencies.py`. Tienen los mismos nombres en el cliente (`@nexy/client`).

```nexy filename="src/rutas/publicaciones/[slug].nexy"
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

| Llamar | Responder |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` convierte un POST en un GET después de un formulario |
| `permanentRedirect(url)` | `308`; Los navegadores y motores de búsqueda lo recuerdan |
| `notFound(detail=None)` | `404`: la página `notfound`, o JSON para un cliente API |
| `forbidden(detail=None)` | `403`: el visitante es conocido pero puede que no lo vea |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` agrega `WWW-Authenticate` |

Una redirección responde con el encabezado `Location` y sin página, también a un cliente API. Construye el
destino a partir de valores en los que confía: un `redirect(request.query_params["next"])` envía visitantes
donde dice el enlace. Se rechaza un destino con un salto de línea.

Un guardia protege una carpeta completa:

```python filename="src/rutas/privado/dependencias.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML o JSON

La misma excepción responde de forma diferente según quién pregunte:

- Un navegador (`Accept: text/html`) obtiene una página HTML. El detalle tiene formato de escape HTML, por lo que se crea un mensaje
  a partir de la entrada del usuario no se puede inyectar marcado.
- Un cliente que solicita JSON y no una página (`Accept: application/json`) obtiene
  `{"detail": "..."}` con el mismo código de estado.

```python filename="src/rutas/api/items/[id].py"
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

> [!NOTA]
> un cliente que envía `Accept: */*` (el valor predeterminado de `curl` y muchos HTTP
> bibliotecas) recibe la página HTML. Establezca `Accept: application/json` para errores JSON.

## Excepciones no controladas

Una excepción en la que no se maneja nada se registra una vez, con la excepción de dónde vino y el
código a su alrededor y respondido de acuerdo con el modo.

| | `nx dev` | `nx start` |
|---|---|---|
| Navegador | una página con el error, las líneas de su código que lo generaron y el rastreo completo | la página incorporada `500` (o su `errors.nexy`) con una referencia |
| Cliente JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Registro del servidor | la excepción y las líneas de su código | la excepción y el rastreo completo, con la misma referencia |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

La referencia son ocho caracteres, nuevos para cada fallo. Un visitante puede citarlo y encontrará el
rastreo buscándolo en el registro. Ni la excepción ni el código llegan al visitante en
producción. Un `errors.nexy` personalizado reemplaza la página únicamente; la línea de registro permanece.

## Errores de validación

Un encabezado faltante, un parámetro de consulta o un campo de cuerpo responde `422` con el cuerpo JSON de FastAPI, para cada
cliente. Ver [Validación y errores](../handlers/validation-and-errors.md).

## Próximos pasos

- [Páginas de error por carpeta](folder-pages.md): un 404, 403 o 401 propio en una carpeta
- [Rutas dinámicas](../pages/dynamic-routes.md)
- [Rutas API](../handlers/README.md)
- [Pruebas](../../../guides/testing.md)