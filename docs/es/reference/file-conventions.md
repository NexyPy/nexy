# Convenciones de archivos

Nombres y reglas reservados en `src/routes/`.

## Archivos de ruta

| Archivo | se convierte |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | la ruta de su directorio |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmento dinámico `{slug}` |
| `[...path].nexy` | comodín `{path:path}` |
| `(group)/page.nexy` | `/page`: el grupo no aparece en la URL |
| `name.py` | controlador de API; Los nombres de las funciones `GET`, `POST`, ... son los métodos. |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | ruta del cliente cuando el marco está habilitado con `useFF` |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/rutas/api/usuarios.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Archivos reservados

| Archivo | Rol | Detalles |
|---|---|---|
| `layout.nexy` | modo servidor: envuelve cada página debajo de ella; el raíz es dueño del documento HTML | [diseño.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | modo cliente (React): el raíz posee el documento HTML, los anidados envuelven las páginas | [diseño.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | modo cliente: diseños anidados | [diseño.vue](../views/vue/differences.md), [diseño.esbelto](../views/svelte/differences.md) |
| `notfound.nexy` | Página 404 para su directorio. | [Páginas de error](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 páginas para su directorio. | [Páginas de error](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | Página 403 para su directorio. | [Páginas de error por carpeta](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | Página 401 para su directorio. | [Páginas de error por carpeta](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reservado; aún no hay efecto de tiempo de ejecución | [Páginas de error](../routing/fbr/errors/README.md) |
| `middleware.py` | un `async def middleware(request, call_next)` que envuelve las solicitudes del directorio y debajo | [Archivos de middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | una lista `dependencies = [fn, ...]` aplicada al directorio y sus hijos | [Dependencias](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python marcador de paquete | |
| `favicon.ico` | servido en `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` y `useLoadingExtensions` reservan más extensiones para estos nombres. Consulte [Configuración](config.md).

Los dos Python archivos de la tabla, uno al lado del otro en una carpeta:

```python filename="src/rutas/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/rutas/admin/dependencias.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Y una página que responde al 404 de su carpeta:

```nexy filename="src/rutas/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Archivos ignorados

- Un archivo o carpeta que comience con `_` o `.`: utilícelo para parciales, borradores y ayudas.
- Un archivo cuya extensión no está activa para el proyecto: se omite con una advertencia.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Un archivo por URL

Se registran dos archivos que se resuelven en la misma URL. No coloque `blog.nexy` al lado de `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Afuera `src/routes/`

| Carpeta | Propósito |
|---|---|
| `src/components/` | componentes importados por páginas; nunca rutas |
| `src/apps/` | controladores y módulos del [enrutador modular](../routing/modular/README.md) |
| `public/` | archivos estáticos, servidos en la raíz: `public/logo.svg` es `/logo.svg` (también en `/public/`) |
| `__nexy__/` | salida generada; no te comprometas |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Próximos pasos

- [Enrutamiento](../routing/README.md)
- [Estructura del proyecto](../getting-started/project-structure.md)
