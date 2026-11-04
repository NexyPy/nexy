# ISR (obsoleto mientras se revalida)

## Definición

ISR almacena en caché el HTML de una página, por URL, y lo sirve hasta que caduque su ventana. La copia caducada
todavía se sirve mientras se representa uno nuevo en segundo plano: es decir, *obsoleto-mientras-revalidate*.

## Cómo funciona

`revalidate = N` en la portada de una página `.nexy` lo activa. `N` es una cantidad de segundos; un
El valor faltante, cero o negativo significa que no hay ningún caché.

La clave de caché es la **ruta de solicitud únicamente** - `request.scope["path"]`. La cadena de consulta no forma parte
de ello.

| Qué | Valor |
|---|---|
| Clave | la ruta URL (`/blog/hello`) |
| Almacenamiento | en memoria, en el proceso que renderiza la página |
| Enlazado | 256 entradas por proceso, menos utilizado recientemente desalojado |
| Encabezado de respuesta | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Ciclo de vida de renderizado

1. Llega una solicitud para una página que declara `revalidate`.
2. Aún no hay entrada: la página se representa, se almacena y se devuelve.
3. Entrada anterior a `N` segundos: se devuelve tal como está, la página no se representa.
4. Entrada anterior a `N` segundos: la entrada **obsoleta** se devuelve inmediatamente y se ejecuta una tarea en segundo plano.
   genera uno nuevo.
5. Si ese procesamiento en segundo plano aumenta, la entrada obsoleta permanece y la siguiente solicitud obsoleta vuelve a intentarse.

## Cuándo usar

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

`N` es un número entero simple. No hay ninguna anulación por ruta en ningún otro lugar y los controladores `.py` no son páginas:
nunca ingresan a este caché.

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

La primera solicitud a `/blog/hello` renderiza y almacena. Los siguientes 300 segundos se sirven de memoria.
`/blog/other` es una entrada independiente, renderizada y almacenada por sí sola. En un proyecto real `posts` viene
desde una base de datos o un servicio, llamado una vez por regeneración.

## Limitaciones

**Nexy garantiza** que la clave de caché es la ruta, la copia obsoleta se entrega durante la regeneración y la
La tienda está limitada y es segura para subprocesos.

**Por convención**, una página que declara `revalidate` es contenido público. Escríbalo como si cada visitante
ve el mismo HTML.

**Tu aplicación es responsable de** todo lo demás:

| Límite | Qué significa |
|---|---|
| Cadena de consulta ignorada | `/search?q=a` y `/search?q=b` comparten una entrada. No almacene en caché una página de búsqueda. |
| Sesión no aislada | La respuesta dice `public` y el HTML del primer visitante se entrega a todos. Nunca leas la sesión en una página con `revalidate`. |
| Sin invalidación del lado del servidor | Nada purga una entrada antes de que finalice su ventana. `revalidate(...)` dentro de una [Acción](../guides/actions.md) solo le dice al **navegador** que recargue una ruta; no toca este caché. |
| Un caché por proceso | Varios trabajadores mantienen varios cachés, con diferentes contenidos. |
| Regeneraciones simultáneas | Nada las deduplica: diez solicitudes obsoletas pueden iniciar diez renderizaciones. |
| Los errores son silenciosos | Una regeneración fallida sigue entregando la página anterior; el error se registra, no se devuelve. |

## Próximos pasos

- [SSR](ssr.md): cómo se representa la página antes de almacenarla en caché
- [Actions](../guides/actions.md): el encabezado `revalidate` y lo que no hace
- [Rendimiento](../deployment/performance.md)
- [Pages](../routing/fbr/pages/README.md): diseños y segmentos dinámicos