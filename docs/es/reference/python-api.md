# Python API

Cada nombre que Nexy exporta a su código Python, por módulo. Una prueba compara esta página con el código en ambas direcciones: debe existir un nombre enumerado aquí y un nombre que el código exporte debe aparecer aquí.

## `nexy`

Componentes para plantillas `.nexy` y ganchos de solicitud.

| Nombre | que es |
|---|---|
| `Audio`, `Video` | reproductores nativos `<audio>` y `<video>`, consulte [componentes](../views/nexy/components.md) |
| `Image` | un `<img>` que se carga lentamente por defecto |
| `Link` | un lado del cliente `<a>` con captación previa opcional |
| `Import` | importar un componente de cliente a una página `.nexy` |
| `Template` | renderizar plantillas Jinja2 y Markdown |
| `Vite` | la etiqueta de cliente Vite que toda página necesita |
| `Form` | un marcador de posición sin comportamiento: use un `<form>` simple con una [acción](../guides/actions.md) |
| `usePathname` | la ruta de la solicitud actual |
| `useSearchParams` | la cadena de consulta como un dict |
| `useParams` | los parámetros de ruta dinámica como un dict, como `useParams()` en el cliente |
| `useQuery` | el nombre original de `useParams`, mantenido para las páginas existentes (no lee la cadena de consulta) |
| `useRequest` | la solicitud actual, para lo que los otros ganchos no cubren |
| `useHeaders` | los encabezados de solicitud como un dictado con nombres en minúsculas |
| `useUrl` | la URL completa: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | si un enlace apunta a la página actual o a uno de sus padres, para una barra de navegación |
| `useRouter` | `path`, `base_url` y `url_for` de la solicitud actual |
| `useSession` | el dictado de la sesión, vacío cuando las sesiones están apagadas |
| `useCookies` | las cookies de solicitud como un dict |
| `useToc` | la tabla de contenidos de la página actual, como HTML |
| `useViews` | renderizar un archivo de vista como `about.tsx` desde un controlador |
| `setMetadata`, `useMetadata` | nombrar el título y las etiquetas de cabecera de una página y escribirlas en el diseño |
| `redirect`, `permanentRedirect` | enviar al visitante a otro lugar (307, 308) y detener la solicitud |
| `notFound`, `forbidden`, `unauthorized` | contesta 404, 403 o 401 desde cualquier lugar |

Los ganchos solo funcionan dentro de una solicitud: consulte [ganchos](../routing/fbr/navigation/hooks.md).

```nexy filename="src/rutas/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## `nexy.http`

El vocabulario HTTP de un controlador. Importe desde aquí en lugar de FastAPI, por lo que sus controladores dependen del contrato de Nexy.

| Nombre | que es |
|---|---|
| `Request`, `Response` | la solicitud entrante y una respuesta saliente |
| `HTTPException` | detener el controlador con un estado y un `detail` |
| `status` | códigos de estado con nombre, como `status.HTTP_404_NOT_FOUND` |
| `Depends` | ejecutar una función primero y pasar su resultado en |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | de dónde viene un parámetro |
| `Form`, `File`, `UploadFile` | campos de formulario y cargas (necesita `python-multipart`) |
| `BackgroundTasks` | trabajo que se ejecuta después de enviar la respuesta |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | respuestas con un tipo de contenido fijo |
| `RedirectResponse` | una redirección HTTP |
| `redirect`, `permanentRedirect` | generar una redirección (307, 308) desde una página, un controlador, un controlador o un guardia |
| `notFound`, `forbidden`, `unauthorized` | levantar un 404, 403 o 401 desde los mismos lugares |
| `FileResponse`, `StreamingResponse` | responder con un archivo o una secuencia |

```python filename="src/rutas/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```

## `nexy.decorators`

| Nombre | que es |
|---|---|
| `Action` | convertir una función en un punto final `POST`, consulte [acciones](../guides/actions.md) |
| `revalidate` | decirle al navegador qué páginas una acción quedó obsoleta |
| `Module`, `Controller` | declarar un módulo y un controlador en el [enrutador modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [inyección de dependencia](../routing/modular/dependency-injection.md) y su vida útil |
| `UseGuard`, `Middleware` | proteger o envolver a un controlador, ver [guardas](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nombra una ruta y descríbela para OpenAPI |
| `UseResponse`, `ResponseMeta` | describir la respuesta de una ruta |
| `HTTP_METHODS` | Los métodos HTTP que un archivo controlador puede definir. |
| `ACTIONS_STORE` | el registro de acciones, para utillaje y pruebas |

```python filename="src/acciones/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Nombre | que es |
|---|---|
| `render` | el HTML de un componente `.nexy` para accesorios determinados, sin un servidor, consulte [pruebas](../guides/testing.md) |

```python filename="pruebas/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## donde sigue

- [Configuración](config.md): los campos `use*` detrás de estos nombres
- [Excepciones y errores](exceptions.md): qué responde cada fallo
- [Índice de documentación](../README.md): la página de lo que estás creando
