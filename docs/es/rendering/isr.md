# ISR (obsoleto mientras se revalida)

## Definición

ISR almacena en caché el HTML de una página, por URL, y lo sirve hasta que caduque su ventana. La copia caducada todavía se entrega mientras se procesa una nueva en segundo plano: es decir, *obsoleta mientras se revalida*.

## como funciona

`revalidate = N` en la portada de una página `.nexy` lo activa. `N` es una cantidad de segundos; un valor faltante, cero o negativo significa que no hay ningún caché.

La clave de caché es la **ruta de solicitud únicamente** - `request.scope["path"]`. La cadena de consulta no forma parte de ella.

| que | Valor |
|---|---|
| clave | la ruta URL (`/blog/hello`) |
| Almacenamiento | seleccionado por `useISRCache`: memoria por defecto, archivo, Redis o una tienda personalizada |
| Atado | 256 entradas para el almacén de memoria, utilizadas menos recientemente desalojadas; El archivo y Redis mantienen las entradas hasta que se invalidan. |
| Encabezado de respuesta | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Cada respuesta ISR lleva ese encabezado, incluido el primer renderizado y un renderizado alternativo cuando la tienda no funciona. Una CDN puede utilizarlo para conservar su propia copia de la misma URL pública.

## Ciclo de vida de renderizado

1. Llega una solicitud para una página que declara `revalidate`.
2. Aún no hay entrada: la página se representa, se almacena y se devuelve.
3. Entrada anterior a `N` segundos: devuelta tal como está, la página no se representa.
4. Entrada con más de `N` segundos: la entrada **obsoleta** se devuelve inmediatamente y una tarea en segundo plano genera una nueva.
5. Si ese procesamiento en segundo plano falla, la entrada obsoleta permanece y la siguiente solicitud obsoleta lo intenta nuevamente.
6. Si el almacenamiento falla, la página se representa y se devuelve sin una entrada almacenada en caché. La solicitud aún tiene éxito.

## cuando usar

- El mismo HTML para cada visitante: una publicación de blog, una página de producto, una página de documentación.
- La página se lee con frecuencia y rara vez cambia.
- Los datos pueden tener unos segundos de antigüedad sin que nadie se dé cuenta.

## Configuración

```nexy filename="src/rutas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` es un número entero simple. No hay anulación por ruta en ningún otro lugar y los controladores `.py` no son páginas: nunca ingresan a este caché.

## Elige una tienda

Establezca `useISRCache` en `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Valor | Tienda | Compartido por |
|---|---|---|
| no establecido, `None` o `"memory"` | memoria de proceso, limitada a 256 entradas | un trabajador |
| `"file"` | Archivos JSON en `.nexy/isr` | trabajadores en un host |
| `{"type": "file", "directory": ".cache/isr"}` | Archivos JSON en el directorio dado | trabajadores en un host |
| `"redis"` | Redis en `redis://localhost:6379/0` | cualquier trabajador que llegue al servidor |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis en esa URL | cualquier trabajador que llegue al servidor |
| `{"type": "redis", "client": client}` | el cliente Redis que pasas | cualquier trabajador que llegue al servidor |
| un objeto con `get`, `set` y `invalidate` | tu propia tienda | lo que sea que comparta |

La tienda Redis necesita el paquete de cliente: `uv add redis`. No está instalado con Nexy. Una tienda personalizada implementa el protocolo `ISRCache` de `nexy.modules.runtime.cache`; su `get` devuelve un `CacheEntry` o `None`.

Las entradas de los archivos se escriben de forma atómica, por lo que un trabajador nunca lee una página a medio escribir. Los trabajadores que usan el mismo directorio o el mismo servidor Redis leen la misma entrada. Una tienda rota solo cuesta un render: nunca responde la solicitud con un error.

## Ejemplo

Una publicación de blog que lee una base de datos:

```nexy filename="src/rutas/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

La primera solicitud a `/blog/hello` renderiza y almacena. Los siguientes 300 segundos se sirven desde la tienda seleccionada. `/blog/other` es una entrada independiente, renderizada y almacenada por sí sola. En un proyecto real `posts` proviene de una base de datos o un servicio, llamado una vez por regeneración.

## Lo que una CDN puede y no puede compartir

Una CDN que respeta `cache-control` puede conservar una copia de `/blog/hello` durante `s-maxage` segundos y entregarla mientras se revalida. Comparte esa copia entre visitantes y trabajadores porque la respuesta dice `public`.

Un CDN no conoce la tienda Nexy. `revalidate()` en una [Acción](../guides/actions.md) elimina la entrada del almacén Nexy configurado, pero no purga una CDN. La CDN conserva su copia hasta que finaliza su propia ventana o hasta que usted configura su eliminación.

No le dé a una CDN una página cuyo HTML dependa del visitante. La respuesta dice `public`, y la clave de Nexy es solo la ruta: dos cadenas de consulta en una ruta comparten una entrada. Una sesión, una cookie o una identificación de usuario en el HTML se pueden enviar a otro visitante.

## Limitaciones

**Nexy garantiza** que la clave de caché es la ruta, la copia obsoleta se entrega durante la regeneración y una falla del almacenamiento vuelve a un procesamiento.

**Por convención**, una página que declara `revalidate` es contenido público. Escríbalo como si todos los visitantes vieran el mismo HTML.

**Tu aplicación es responsable de** todo lo demás:

| Límite | lo que significa |
|---|---|
| Cadena de consulta ignorada | `/search?q=a` y `/search?q=b` comparten una entrada. No almacene en caché una página de búsqueda. |
| Sesión no aislada | La respuesta dice `public` y el HTML del primer visitante se entrega a todos. Nunca leas la sesión en una página con `revalidate`. |
| CDN no purgado | `revalidate()` purga la tienda Nexy, no una CDN u otro proxy delante de ella. |
| Sin TTL en los almacenes de archivos y Redis | Las entradas permanecen hasta que `revalidate()` o su propia limpieza las elimine. El almacén de memoria desaloja la entrada utilizada menos recientemente después de 256. |
| Regeneraciones concurrentes | Nada los deduplica: diez solicitudes obsoletas pueden iniciar diez renderizados. |
| Los errores son silenciosos | Una operación de regeneración o de almacenamiento fallida sigue entregando la página; el error no se devuelve. |

## Próximos pasos

- [SSR](ssr.md): cómo se representa la página antes de almacenarla en caché
- [Acciones](../guides/actions.md): el encabezado `revalidate` y la invalidación de la tienda
- [Configuración](../reference/config.md#server): `useISRCache`
- [Rendimiento](../deployment/performance.md)
- [Páginas](../routing/fbr/pages/README.md): diseños y segmentos dinámicos
