# File conventions

Reserved names and rules under `src/routes/`.

## Route files

| File | Becomes |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | the route of its directory |
| `about.nexy` | `/about` |
| `[slug].nexy` | dynamic segment `{slug}` |
| `[...path].nexy` | catch-all `{path:path}` |
| `(group)/page.nexy` | `/page`: the group does not appear in the URL |
| `name.py` | API handler; function names `GET`, `POST`, ... are the methods |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | client route when the framework is enabled with `useFF` |

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

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Reserved files

| File | Role | Details |
|---|---|---|
| `layout.nexy` | server mode: wraps every page below it; the root one owns the HTML document | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | client mode (React): the root one owns the HTML document, nested ones wrap pages | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | client mode: nested layouts | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404 page for its directory | [Error pages](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 page for its directory | [Error pages](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 page for its directory | [Error pages per folder](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 page for its directory | [Error pages per folder](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reserved; no runtime effect yet | [Error pages](../routing/fbr/errors/README.md) |
| `middleware.py` | an `async def middleware(request, call_next)` wrapping the requests of the directory and below | [Middleware files](../routing/fbr/middleware/README.md) |
| `dependencies.py` | a `dependencies = [fn, ...]` list applied to the directory and its children | [Dependencies](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python package marker | |
| `favicon.ico` | served at `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`,
`useUnauthorizedExtensions` and `useLoadingExtensions` reserve more extensions for these names. See
[Config](config.md).

The two Python files of the table, side by side in one folder:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

And a page that answers the 404 of its folder:

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Ignored files

- A file or folder starting with `_` or `.`: use it for partials, drafts and helpers.
- A file whose extension is not active for the project: it is skipped with a warning.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## One file per URL

Two files that resolve to the same URL both register. Do not put `blog.nexy` next to
`blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Outside `src/routes/`

| Folder | Purpose |
|---|---|
| `src/components/` | components imported by pages; never routes |
| `src/apps/` | controllers and modules of the [modular router](../routing/modular/README.md) |
| `public/` | static files, served at the root: `public/logo.svg` is `/logo.svg` (also under `/public/`) |
| `__nexy__/` | generated output; do not commit |

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

## Next steps

- [Routing](../routing/README.md)
- [Project structure](../getting-started/project-structure.md)
