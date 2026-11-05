# Enrutamiento basado en archivos

Una ruta es un archivo. La URL es la ruta del archivo relativa a `src/routes/`, menos la extensión.

## Archivo a URL

| Archivo | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` se asigna a su directorio, no a `/index`. Un directorio entre paréntesis es un **grupo**: organiza archivos sin aparecer en la URL.

En modo cliente los archivos de página son `.tsx`, `.vue` o `.svelte` en lugar de `.nexy`; las reglas de URL son las mismas.

## Dos modos

`useCSR` decide cuáles son las páginas. Los dos no se pueden mezclar en un proyecto: Nexy se niega a iniciarse cuando una página del servidor se encuentra al lado de la ruta de un cliente.

| Modo | Páginas | Diseño raíz | Ver |
|---|---|---|---|
| Servidor (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Modo servidor y modo cliente](modes.md) |
| Cliente (`useCSR = True`) | archivos de marco | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` los archivos son controladores de API en ambos modos.

## que no es una ruta

- Nombres de archivos reservados: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- Archivos y carpetas que comienzan con `_` o `.`: utilícelos para parciales y borradores.
- Extensiones que no están activas para su proyecto. Un archivo cuya extensión está inactiva se omite con una advertencia.

## Un archivo por URL

Se registran dos archivos que se resuelven en la misma URL. No cree `blog.nexy` junto a `blog/index.nexy` y no mezcle `index.nexy` y `index.py` para la misma ruta. Elige uno.

## En esta sección

| Carpeta | Qué cubre |
|---|---|
| [páginas/](pages/README.md) | páginas, [rutas dinámicas](pages/dynamic-routes.md), grupos de rutas |
| [layouts/](layouts/README.md) | una página por tipo de archivo de diseño |
| [handlers/](handlers/README.md) | `.py` handlers, validación y errores |
| [dependencias/](dependencies/README.md) | `dependencies.py`, guardias |
| [middleware/](middleware/README.md) | `middleware.py` |
| [errores/](errors/README.md) | páginas no encontradas y de error |
| [navegación/](navigation/linking-and-navigating.md) | enlaces, ganchos |
| [tiempo real/](realtime/websocket.md) | WebSocket |
| [herencia](inheritance.md) | las reglas de herencia en una tabla |

## Próximos pasos

- [Modo servidor y modo cliente](modes.md)
- [Diseños](layouts/README.md)
- [Enrutamiento modular](../modular/README.md)
