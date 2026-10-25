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
    useAliases = {"@": "src/"}
```

## Server

| Field | Default | Meaning |
|---|---|---|
| `usePort` | `3000` | port for `dev` and `start` |
| `useHost` | `"0.0.0.0"` | bind address |
| `useSslKeyfile`, `useSslCertfile` | `None` | serve HTTPS directly |
| `useCSR` | `False` | client-side routing mode; `.nexy` routes are disabled |

## Routes

| Field | Default | Meaning |
|---|---|---|
| `useRouter` | `None` | an `APIRouter` instance or class mounted next to the file-based routes; `None` means file-based only |
| `excludeDirs` | `["templates", "extension", "docs"]` | directories skipped when scanning routes |
| `useAliases` | `None` | import aliases, e.g. `{"@": "src/"}` |

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
| `useLoadingExtensions` | `loading.*` |

## API documentation

| Field | Default | Meaning |
|---|---|---|
| `useDocs` | `True` | serve the OpenAPI schema and its Scalar reference page |
| `useDocsUrl` | `"/docs"` | path of the API reference page |
| `useRedocsUrl` | `"/redocs"` | declared but no route is mounted |
| `useTitle` | `"Nexy App"` | OpenAPI title and page title (`"Nexy"` in `NexyConfigModel`) |

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
