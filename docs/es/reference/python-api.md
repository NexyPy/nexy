# API de Python

Cada nombre que Nexy exporta a su código Python, por módulo. Una prueba compara esta página con el código en
En ambas direcciones: debe existir un nombre enumerado aquí y un nombre que el código exporte debe aparecer aquí.

## `nexy`

Componentes para plantillas `.nexy` y ganchos de solicitud.

| Nombre | Qué es |
|---|---|
| `Audio`, `Video` | reproductores nativos `<audio>` y `<video>`, consulte [componentes](../views/nexy/components.md) |
| `Image` | un `<img>` que se carga lentamente por defecto |
| `Link` | un lado del cliente `<a>` con captación previa opcional |
| `Import` | importar un componente de cliente en una página `.nexy` |
| `Template` | renderizar plantillas de Jinja2 y Markdown |
| `Vite` | la etiqueta de cliente Vite que toda página necesita |
| `Form` | un marcador de posición sin comportamiento: use un `<form>` simple con una [acción](../guides/actions.md) |
| `usePathname` | la ruta de la solicitud actual |
| `useSearchParams` | la cadena de consulta como un dict |
| `useParams` | los parámetros de ruta dinámica como un dict, como `useParams()` en el cliente |
| `useQuery` | el nombre original de `useParams`, mantenido para las páginas existentes (no lee la cadena de consulta) |
| `useRequest` | la solicitud actual, por lo que los otros ganchos no cubren |
| `useHeaders` | los encabezados de solicitud como un dictado con nombres en minúsculas |
| `useUrl` | la URL completa: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | si un enlace apunta a la página actual o a una de sus principales, para una barra de navegación |
| `useRouter` | `path`, `base_url` y `url_for` de la solicitud actual |
| `useSession` | el dictado de la sesión, vacío cuando las sesiones están desactivadas |
| `useCookies` | las cookies de solicitud como un dict |
| `useToc` | la tabla de contenidos de la página actual, como HTML |
| `useViews` | renderizar un archivo de vista como `about.tsx` desde un controlador |
| `setMetadata`, `useMetadata` | nombra el título y las etiquetas de cabecera de una página y escríbelas en el diseño |
| `redirect`, `permanentRedirect` | envían al visitante a otro lugar (307, 308) y detienen la solicitud |
| `notFound`, `forbidden`, `unauthorized` | contesta 404, 403 o 401 desde cualquier lugar |

Los ganchos solo funcionan dentro de una solicitud: consulte [ganchos](../routing/fbr/navigation/hooks.md).

## `nexy.http`

El vocabulario HTTP de un controlador. Importe desde aquí en lugar de FastAPI, por lo que sus controladores dependen
en el contrato de Nexy.

| Nombre | Qué es |
|---|---|
| `Request`, `Response` | la solicitud entrante y una respuesta saliente |
| `HTTPException` | detener el controlador con un estado y un `detail` |
| `status` | códigos de estado con nombre, como `status.HTTP_404_NOT_FOUND` |
| `Depends` | ejecuta una función primero y pasa su resultado en |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | de donde proviene un parámetro |
| `Form`, `File`, `UploadFile` | campos de formulario y cargas (necesita `python-multipart`) |
| `BackgroundTasks` | trabajo que se ejecuta después de enviar la respuesta |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | respuestas con un tipo de contenido fijo |
| `RedirectResponse` | una redirección HTTP |
| `redirect`, `permanentRedirect` | levantan una redirección (307, 308) desde una página, un handler, un controlador o un guardia |
| `notFound`, `forbidden`, `unauthorized` | levantan un 404, 403 o 401 desde los mismos lugares |
| `FileResponse`, `StreamingResponse` | responden con un archivo o una secuencia |

## `nexy.decorators`

| Nombre | Qué es |
|---|---|
| `Action` | convierte una función en un `POST` punto final, ver [actions](../guides/actions.md) |
| `revalidate` | decirle al navegador qué páginas una acción dejó obsoletas |
| `Module`, `Controller` | declaran un módulo y un controlador en el [router modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [inyección de dependencia](../routing/modular/dependency-injection.md) y sus tiempos de vida |
| `UseGuard`, `Middleware` | protegen o envuelven a un manejador, ver [guardias](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nombra una ruta y descríbela para OpenAPI |
| `UseResponse`, `ResponseMeta` | describen la respuesta de una ruta |
| `HTTP_METHODS` | los métodos HTTP que un archivo controlador puede definir |
| `ACTIONS_STORE` | el registro de acciones, para herramental y pruebas |

## `nexy.testing`

| Nombre | Qué es |
|---|---|
| `render` | el HTML de un `.nexy` componente para accesorios determinados, sin un servidor, consulte [pruebas](../guides/testing.md) |

## ¿Dónde sigue?

- [Config](config.md): los campos `use*` detrás de estos nombres
- [Excepciones y errores](exceptions.md): qué responde cada falla
- [Índice de documentación](../README.md): la página de lo que estás creando