# Config

Configuration is a class in `nexyconfig.py` at the project root. Nexy loads it from the directory it
runs in; a project without the file uses the defaults.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Server

| Field | Default | Meaning |
|---|---|---|
| `usePort` | `3000` | port for `dev` and `start` |
| `useHost` | `"0.0.0.0"` | bind address |
| `useSslKeyfile`, `useSslCertfile` | `None` | serve HTTPS directly |
| `useDevTools` | `True` | the toolbar `nexy dev` adds to every page (page info, routes, errors, config); `False` removes it. Never present in production |
| `useHealth` | `False` | serve `GET /health/live` and `GET /health/ready` for load balancers and Kubernetes probes; see [Deploy](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | the largest request body a worker reads, in bytes (1 MiB); a larger one is a `413`, and `0` turns the limit off. Raise it for a route that takes file uploads |
| `useSiteUrl` | `None` | the public origin of the site, such as `"https://example.com"`; once set, Nexy serves `/sitemap.xml` and `/robots.txt`. See [Sitemap and robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | processes `nx start` runs; `0` is one per CPU on Linux and macOS, one on Windows |
| `useCSR` | `False` | client-side routing mode; `.nexy` routes are disabled |
| `useBasePath` | `None` | public prefix for the whole application, such as `"/app"`; requests outside it answer 404, and generated links, client routes, action calls and assets carry the prefix. See [Deploy](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | pixel widths `nx build` generates for local images; the conversion needs `Pillow`, and without it images keep their original URL. See [Image](../routing/fbr/navigation/linking-and-navigating.md#image) |
| `useISRCache` | `None` | ISR store: `None` or `"memory"` for one process, `"file"` for one host, `"redis"` for several workers, a mapping with `type` and options, or an object with `get`, `set` and `invalidate`. See [ISR](../rendering/isr.md#choose-a-store) |

## Database

| Field | Default | Meaning |
|---|---|---|
| `useORM` | `None` | the ORM of the project: `"SQLModel"`, `"SQLAlchemy"` or `"Tortoise-ORM"`. `nx new` writes it, and `nx migrate` picks Alembic or Aerich from it; without it, `nx migrate` takes the first ORM installed. See [Databases](../guides/databases.md#migrations) |

## Routes

| Field | Default | Meaning |
|---|---|---|
| `useRouter` | `None` | an `APIRouter` instance or class mounted next to the file-based routes; `None` means file-based only |
| `excludeDirs` | `["templates", "extension", "docs"]` | directories skipped when scanning routes |
| `useAliases` | `None` | import aliases, e.g. `{"@": "src"}` (`@/components/Counter.tsx` means `src/components/Counter.tsx`); `nx new` writes the one you chose, and Vite and `tsconfig.json` follow it |

## Frontend

| Field | Default | Meaning |
|---|---|---|
| `useFF` | `None` | client framework factory: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | build and serve client bundles with Vite |
| `useMarkdownExtensions` | `[]` | extra extensions for `.md`/`.mdx` rendering |
| `useWatchExtensions` | `None` | extra extensions the dev server watches |
| `useWatchExcludePatterns` | `None` | glob patterns the dev server ignores |

> **Good to know**: `NexyConfigModel` declares `useVite = False`; the runtime `Config` default is
> `True`.

## Reserved file names

Each field adds extensions to a reserved role. `useLayoutExtensions = ["md"]` makes `layout.md`
reserved, exactly like `layout.nexy`.

| Field | Adds extensions to |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API documentation

| Field | Default | Meaning |
|---|---|---|
| `useDocs` | `"dev"` | where the Scalar reference page and `/openapi.json` are served: `"dev"` on `nx dev` only, `True` in production too (the schema lists every route and server action), `False` nowhere |
| `useDocsUrl` | `"/docs"` | path of the API reference page |
| `useRedocsUrl` | `"/redocs"` | declared but no route is mounted |
| `useTitle` | `"Nexy App"` | OpenAPI title and page title (`"Nexy"` in `NexyConfigModel`) |

### Free `/docs` for a page of the project

The API reference answers `/docs` before any route, so `src/routes/docs.nexy` or
`src/routes/docs/[[...slug]].nexy` is never served there. `nx dev` and `nx start` name such a page
at startup. Move the reference with `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Or turn it off with `useDocs = False`, which also stops serving `/openapi.json`. While the
reference is on, keep the routes of the project off that path.

## Middleware

| Field | Default | Meaning |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI middleware classes |
| `useCORS` | `None` | kwargs for `CORSMiddleware` |
| `useGZip` | `None` | kwargs for `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs for `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs for `SessionMiddleware` |
| `useAuth` | `None` | authentication middleware config |
| `useHTTPSRedirect` | `False` | redirect HTTP to HTTPS |
| `useRateLimit` | `None` | the requests one client address may send per window, such as `{"requests": 60, "per": 60}`; one more is a `429` with `Retry-After`, and `"paths": ["/api/"]` limits only those prefixes. Each worker counts on its own. See [Rate limiting](../guides/middleware-and-security.md#rate-limiting) |

## Markdown

| Field | Default | Meaning |
|---|---|---|
| `useTocDepth` | `"2-6"` | heading levels included in the table of contents |
| `useTocTitle` | `"Table of Contents"` | TOC title |
| `useTocAuto` | `True` | generate the table of contents for Markdown pages |

## Routes outside the file tree

Build a FastAPI `APIRouter` and mount it with `useRouter`. It is served next to the file-based
routes:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Defaults above are read from `nexy/core/config.py`.

## Declared, not read yet

These fields exist in `NexyConfigModel` but no code consumes them. Setting them has no effect:

`useViteDevUrl`, `useRTL`.

## Next steps

- [i18n](../guides/i18n.md): internationalization
- [Frontend](../guides/frontend.md): `useFF` and the client build
- [Deploy](../deployment/README.md): production options
