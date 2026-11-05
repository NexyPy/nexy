# Excepciones y errores

Una solicitud puede fallar en cuatro lugares y Nexy responde a cada uno de manera diferente. Esta página es el índice: busque el estado que ve, luego la línea que lo produjo, luego el archivo que decide el cuerpo.

> [!NOTA]
> Tres cosas están separadas y son fáciles de mezclar: la **respuesta HTTP** (un estado y un cuerpo), la **página de error** (`notfound.nexy`, `errors.nexy`) y la **línea de registro** (lo que lees en la terminal). Cambiar la página no cambia el estado y personalizar la página no oculta el registro.

## La versión corta

| Qué pasó | Estado | El navegador ve | El cliente API ve |
|---|---|---|---|
| ninguna ruta coincide con la URL | `404` | `notfound.nexy`; de lo contrario, la página incorporada | `{"detail": "Not Found"}` |
| un segmento de camino no se ajusta a su anotación | `404` | la misma página | `{"detail": "Not Found"}` |
| falta una consulta, encabezado, cookie o campo de cuerpo o no es válido | `422` | FastAPI cuerpo JSON de | FastAPI cuerpo JSON |
| `notFound()` | `404` | la página | `{"detail": ...}` |
| `unauthorized()` | `401` | la página incorporada | `{"detail": ...}` |
| `forbidden()` | `403` | la página incorporada | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | la página incorporada | `{"detail": ...}` |
| una excepción no detectó nada | `500` | `errors.nexy`; de lo contrario, la página incorporada | `{"detail", "reference"}` |
| `redirect(url)` | `307` | el destino, sin página | el destino, sin cuerpo |
| `permanentRedirect(url)` | `308` | el destino, sin página | el destino |

Un cliente API es una solicitud cuyo encabezado `Accept` solicita JSON y no una página:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!ADVERTENCIA]
> `curl` envía `Accept: */*` de forma predeterminada, que obtiene la página HTML. Agregue `-H "Accept: application/json"` cuando pruebe la forma JSON. Los navegadores siguen recibiendo páginas.

## De donde viene un fracaso

```diagram filename="Una petición, cuatro salidas"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Etapa | Qué puede fallar | La respuesta |
|---|---|---|
| Middleware | su `middleware.py`, CORS, sesiones | el estado de la excepción, de lo contrario `500` |
| Enrutador | la URL no coincide con ningún archivo | `404` |
| Validación | un segmento de ruta no se puede convertir | `404` |
| Validación | una consulta, encabezado, cookie o campo de cuerpo | `422` |
| Página, controlador, acción, guardia | `HTTPException` | su estado |
| Página, controlador, acción, guardia | cualquier otra cosa | `500` |

## Salir desde cualquier lugar

`redirect`, `permanentRedirect`, `notFound`, `forbidden` y `unauthorized` generan una excepción HTTP, por lo que la misma llamada funciona en una página `.nexy`, un controlador API, un controlador modular, un guardia, un `dependencies.py` y una acción.

```python filename="src/rutas/publicaciones/[slug].py"
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

| Llamar a | Responder | Cuando |
|---|---|---|
| `notFound(detail=None)` | `404` | el recurso no existe |
| `unauthorized(detail=None, scheme=None)` | `401` | el visitante debe iniciar sesión primero |
| `forbidden(detail=None)` | `403` | el visitante es conocido pero puede que no lo vea |
| `redirect(url, status=307)` | `307` | enviarlos a otro lado, manteniendo el método |
| `redirect(url, status=303)` | `303` | después de un formulario: la siguiente solicitud es un `GET` |
| `permanentRedirect(url)` | `308` | una página movida que los motores de búsqueda deben recordar |

Construya el destino a partir de valores en los que confíe. `redirect(request.query_params["next"])` envía visitantes a donde dice el enlace; es una redirección abierta. Se rechaza un destino que contenga un salto de línea.

## Validación: 422 o 404

Los parámetros del controlador son validados por FastAPI contra sus anotaciones.

```python filename="src/rutas/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problema | Estado | Por qué |
|---|---|---|
| consulta, encabezado, cookie o campo de cuerpo faltantes o no válidos | `422` | la solicitud llegó al controlador, los datos son incorrectos |
| segmento de ruta no válido (`/api/users/abc` para `id: int`) | `404` | la carpeta no tiene ruta para un no número, por lo que la URL no existe |

El cuerpo de `422` tiene la forma estándar de FastAPI, por lo que los clientes y los SDK generados siguen funcionando:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Para un formulario o una acción, el cliente recibe un `ActionError` con `status` y `detail`; un `422` también llena `error.fields` con un mensaje por campo. Consulte [Acciones](../guides/actions.md#errors-and-failures).

> [!CONSEJO]
> Validar en la firma cuando la regla sea de un campo (`limit: int = 10`). Validar en el cuerpo cuando la regla necesita la base de datos u otro campo ("este correo ya está usado"): subir `HTTPException(409)` y conservar el mensaje para el cliente.

## Páginas de error personalizadas

```nexy filename="src/rutas/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/rutas/errores.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| Archivo | Estado | Alcance |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | cada ruta del proyecto |
| `src/routes/errors.nexy` | `500` | cada ruta del proyecto |
| `src/routes/forbidden.nexy` | `403` | cada ruta del proyecto |
| `src/routes/unauthorized.nexy` | `401` | cada ruta del proyecto |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` y menores |
| `src/routes/blog/errors.nexy` | `500` | `/blog` y menores |
| `src/routes/loading.nexy` | - | reservado, aún sin efecto de tiempo de ejecución |

Un archivo en algún lugar de las rutas instala la respuesta para su estado: una copia en la raíz responde a todo el proyecto, una copia en una carpeta responde a esa carpeta y gana el archivo más profundo que coincida con la URL. Una URL fuera de cada copia y un estado sin ningún archivo obtienen las páginas con estilo integradas. Consulte [Páginas de error por carpeta](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANTE]
> Una página `errors.nexy` reemplaza a la página `500`; no detecta la excepción y no cambia la línea de registro. Si el controlador que generó es la página misma, la página no puede mostrar sus propios detalles de error: mantenga `errors.nexy` simple e independiente.

## Excepciones no controladas

Una excepción en la que no se detecta nada se registra una vez, con su referencia, de dónde proviene y el código que la rodea. El estado es `500` y el cuerpo depende del medio ambiente.

| | `nexy dev` | `nexy build` luego `nexy start` |
|---|---|---|
| Navegador | el error, las líneas de su código y el rastreo | `errors.nexy`, de lo contrario, la página incorporada, con una referencia |
| Cliente API | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | la excepción y las líneas de su código | la excepción, el rastreo completo y la referencia |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

La referencia son ocho caracteres, nuevos para cada fallo. Un visitante puede citarlo y usted encontrará el rastreo buscándolo en el registro. Ni la excepción ni el código llegan al visitante en producción.

> [!PRECAUCIÓN]
> No devuelva el rastreo a un visitante en producción y no incluya secretos en un mensaje de error: el `detail` de un `HTTPException` se envía al cliente con formato de escape HTML. Pon el secreto en el registro, no en la respuesta.

## Acciones y formas

Una acción es un punto final `POST` con una ruta generada. Sus fallos siguen las mismas reglas:

| Situación | Estado | Cliente |
|---|---|---|
| falta un campo o no es válido | `422` | `ActionError` con `fields` |
| `HTTPException(403)` planteado en la acción | `403` | `ActionError` con `status` y `detail` |
| una excepción no controlada | `500` | `ActionError`; la referencia está en el registro del servidor |
| el encabezado `Origin` es otro sitio | `403` | rechazado antes de que se ejecute la acción |

Un formulario sin JavaScript publicaciones en la ruta de acción; un éxito responde `303` de regreso a la página, un error muestra la página de error. Ver [Acciones](../guides/actions.md#forms-without-javascript).

## Una lista de verificación cuando una página responde algo incorrecto

1. **Mire el estado**, no la página. Un `notfound.nexy` personalizado todavía responde `404`.
2. **Lea la terminal.** Una página que no se puede importar no está registrada, por lo que su URL responde `404` mientras el archivo existe. El error de importación está en el registro.
3. **Verifique la extensión.** Con `useCSR = True`, las páginas `.nexy` pertenecen al modo servidor; una página en el modo incorrecto no es una ruta.
4. **Verifique la profundidad.** Un `notfound.nexy` o `errors.nexy` solo funciona cuando existe la copia raíz.
5. **Solicite JSON** con `Accept: application/json` para ver la forma que recibe su cliente API.
6. **Cite la referencia** de un `500` cuando abra un número o busque en el registro.

## Próximos pasos

- [Páginas de error](../routing/fbr/errors/README.md): el comportamiento de la página completa, con ejemplos
- [Validación y errores](../routing/fbr/handlers/validation-and-errors.md): Controladores de API
- [Solución de problemas](../guides/troubleshooting.md): los errores que la gente realmente encuentra
- [Prueba](../guides/testing.md): afirmar un estado y un cuerpo
