# Convenciones de archivos

Nombres y reglas reservados en `src/routes/`.

## Archivos de ruta

| Archivo | Se convierte en |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | la ruta de su directorio |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmento dinámico `{slug}` |
| `[...path].nexy` | general `{path:path}` |
| `(group)/page.nexy` | `/page`: el grupo no aparece en la URL |
| `name.py` | Controlador API; los nombres de las funciones `GET`, `POST`, ... son los métodos |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | ruta del cliente cuando el marco está habilitado con `useFF` |

## Archivos reservados

| Archivo | Rol | Detalles |
|---|---|---|
| `layout.nexy` | modo servidor: envuelve cada página debajo de él; el raíz posee el documento HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | modo cliente (React): el raíz posee el documento HTML, los anidados envuelven las páginas | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | modo cliente: diseños anidados | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Página 404 para su directorio | [Páginas de error](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 páginas para su directorio | [Páginas de error](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 página para su directorio | [Páginas de error por carpeta](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 página para su directorio | [Páginas de error por carpeta](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reservado; aún no hay efecto de tiempo de ejecución | [Páginas de error](../routing/fbr/errors/README.md) |
| `middleware.py` | y `async def middleware(request, call_next)` envolviendo las solicitudes del directorio y debajo | [Archivos middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | una lista `dependencies = [fn, ...]` aplicada al directorio y sus hijos | [Dependencias](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Marcador de paquete Python | |
| `favicon.ico` | servido en `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`,
`useUnauthorizedExtensions` y `useLoadingExtensions` reservan más extensiones para estos nombres. Ver
[Configuración](config.md).

## Archivos ignorados

- Un archivo o carpeta que comienza con `_` o `.`: úselo para parciales, borradores y ayudas.
- Un archivo cuya extensión no está activa para el proyecto: se omite con una advertencia.

## Un archivo por URL

Se registran dos archivos que se resuelven en la misma URL. No pongas `blog.nexy` al lado de
`blog/index.nexy`.

## Afuera `src/routes/`

| Carpeta | Propósito |
|---|---|
| `src/components/` | componentes importados por páginas; nunca rutas |
| `src/apps/` | controladores y módulos del [enrutador modular](../routing/modular/README.md) |
| `public/` | archivos estáticos, servidos en la raíz: `public/logo.svg` es `/logo.svg` (también en `/public/`) |
| `__nexy__/` | salida generada; no cometas |

## Próximos pasos

- [Enrutamiento](../routing/README.md)
- [Estructura del proyecto](../getting-started/project-structure.md)