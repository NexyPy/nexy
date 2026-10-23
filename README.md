<p align="center">
  <img src="./nexy.png" alt="Nexy - The Python fullstack meta-framework: FastAPI backend, Vite frontend, zero config" width="100%" />
</p>

# Nexy

**The fullstack Python meta-framework.** FastAPI on the server, Vite on the client, one file per
page. Startup in under a second, HMR in under 100 ms.

<p>
  <a href="https://pypi.org/project/nexy"><img src="https://img.shields.io/pypi/v/nexy?color=%2334D058&label=version" alt="PyPI version"></a>
  <a href="https://pypi.org/project/nexy"><img src="https://img.shields.io/pypi/pyversions/nexy?color=%2334D058" alt="Python versions"></a>
  <a href="https://github.com/NexyPy/nexy/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/NexyPy/nexy/ci.yml?branch=main&color=%2334D058" alt="CI"></a>
  <a href="https://github.com/NexyPy/nexy"><img src="https://img.shields.io/github/stars/NexyPy/nexy?style=flat&color=%2334D058" alt="GitHub stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/NexyPy/nexy?color=%2334D058" alt="License"></a>
  <a href="https://github.com/NexyPy/nexy/commits/main"><img src="https://img.shields.io/github/last-commit/NexyPy/nexy?color=%2334D058" alt="Last commit"></a>
</p>

## What Nexy is

A route is a file. Put `.nexy` under `src/routes/` and you get a page: Python for the logic, Jinja2
for the markup, an optional React, Vue, Svelte, Solid or Preact component for interactivity. Put
`.py` there and you get an API handler: the function names are the HTTP methods.

The server is FastAPI and Starlette. The client is Vite. There is no second process, no second
origin, no glue project between the frontend and the backend.

| You get | Instead of |
|---|---|
| Sub-second startup | 10-30 s waiting for Next.js, Rails, Django |
| One file = server logic, markup, interactive island | Separate API, UI and build-tooling projects |
| Zero-config Vite integration | Hand-wiring Webpack, Vite or Parcel |
| Any supported client framework, or none | Being locked into React or Vue |
| SSR, ISR and parallel SSG built in | SSG bolted on afterwards |

## Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | runs and manages Nexy |
| Node.js 18+ | only for React, Vue, Svelte, Solid or Preact |

## Install and run

```bash
uvx nexy new my-app
cd my-app
uvx nexy dev
```

Open <http://localhost:3000>. `uvx` downloads Nexy and runs it, so nothing is installed globally.
Install the CLI once with `uv tool install nexy` to drop the prefix and use `nx dev` (or
`nexy dev`).

`new` asks four questions: file-based router or modular, web or API, client framework or none, ORM or
none. The answers decide what the scaffold writes.

Change a file, the page reloads. `nx dev` compiles the routes you touched and proxies Vite through
its own port, so the browser only ever talks to `3000`.

## Project layout

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

## Routing

The URL is the file path relative to `src/routes/`, minus the extension.

| File | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` maps to its directory, not to `/index`. A directory in parentheses is a group: it organises
files without appearing in the URL.

These names are not routes: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`,
`dependencies.py`, `__init__.py`. Files and folders starting with `_` or `.` are ignored, which is
the place for partials and drafts.

One file per URL. `blog.nexy` next to `blog/index.nexy` registers two routes for the same path; pick
one.

### Dynamic segments

One segment, `[slug]`, becomes a page property:

```nexy
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

Several segments, `[...path]`, arrive as a single string with the slashes included. In a `.nexy`
page only `int` and `float` annotations are converted; every other segment arrives as a string.

### Layouts and error pages

`layout.nexy` wraps every page in its directory and in its children. The page is passed as
`children`:

```nexy
---
children: prop[str]
---
<header>...</header>
<main>{{ children }}</main>
<footer>...</footer>
```

With a client framework configured, `layout.tsx`, `layout.jsx`, `layout.vue` and `layout.svelte`
work too.

`notfound.nexy` answers `404` and `errors.nexy` answers `500`, each scoped to its directory. Both
must exist at the routes root to be installed at all; a copy in a subdirectory refines the page for
that prefix. The `500` handler catches every unhandled exception, API handlers included, and answers
with HTML - return a `JSONResponse` when the caller expects JSON.

`dependencies.py` follows the same hierarchy: a dependency declared there applies to that directory
and its children.

`loading.nexy` is reserved but has no runtime effect yet.

### Rendering modes

| Mode | How | Behaviour |
|---|---|---|
| SSR | default | rendered per request by Jinja2, or by the framework at build time for framework routes |
| ISR | `revalidate = 60` in the frontmatter | in-process, per-path cache; sends `Cache-Control: public, s-maxage=60, stale-while-revalidate=60` |
| CSR | `useCSR = True` in `nexyconfig.py` | first load returns HTML, then the client router navigates; `.nexy` routes are disabled |
| SSG | `nx build` | framework routes pre-rendered to HTML by a per-file esbuild pipeline, one file per worker |

CSR requires a client framework, and is incompatible with a modular `useRouter`. Only `.tsx`,
`.jsx`, `.vue` and `.svelte` routes are navigable client-side; `.md` can use a CSR shell.

## API handlers

A `.py` file under `src/routes/` is an API handler. The file path is the URL, and each function
named after an HTTP method becomes an endpoint.

```python
# src/routes/api/items.py  →  /api/items
from fastapi import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Supported names: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`.

| Parameter source | How it arrives |
|---|---|
| Path segment `[id]` | function argument `id`, converted to its annotation |
| Query string | `page: int = 1` |
| JSON body | Pydantic model argument |
| FastAPI primitives | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - unchanged |

FastAPI validates the annotation and answers `422` on a mismatch. Return a `dict`, a `list` or a
`BaseModel` for JSON; return a response object for a custom status or content type.

Every handler appears in the generated OpenAPI schema, served at `/openapi.json` and rendered by
Scalar at `/docs`. Disable both with `useDocs = False`.

### WebSocket

Define `SOCKET` in a `.py` route file to register a WebSocket at the same path:

```python
# src/routes/ws/chat.py
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

### Modular routing

Files are the default, not the only option. Classes and decorators produce an `APIRouter` that is
mounted with `useRouter`:

```python
# src/apps/app_controller.py
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller(prefix="/users")
class UserController:
    def get(self) -> JsonResponse:
        return {"users": []}
```

```python
# src/apps/app_module.py
from nexy.decorators import Module
from .app_controller import UserController


@Module(prefix="/api")
class AppModule:
    controllers = [UserController]
```

```python
# nexyconfig.py
class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

Methods are matched by name, case-insensitively; one handler per HTTP method, duplicates raise at
startup. `@Injectable()` classes are resolved into a controller's `__init__`; register them in
`providers` to resolve them eagerly at startup. `Scope.SINGLETON`, `Scope.REQUEST` and
`Scope.TRANSIENT` are available for their lifetime, and `Container.resolve(Service)` builds one
yourself. `@UseGuard()` and `@Middleware()` add FastAPI dependencies; `@UseRoute()` is OpenAPI
metadata only.

File-based routing keeps working when a modular router is mounted: `src/routes/` is scanned whenever
it exists.

## Views

A view renders the page body. Pick one format per file.

| Format | File | Server render | Client framework |
|---|---|---|---|
| `.nexy` | page | Jinja2 + Python logic, streamed | optional |
| `.md` | pure Markdown | cmarkgfm at request time, GFM, layout-wrapped | optional via layout |
| `.mdx` | Markdown with components | framework SSR | React or Preact |
| `.tsx`, `.jsx` | component | framework SSR / SSG | React or Preact |
| `.vue` | SFC | framework SSR / SSG | Vue |
| `.svelte` | SFC | framework SSR / SSG | Svelte |

### The `.nexy` file

Python on top, HTML in the middle, CSS at the bottom.

```nexy
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

Everything between the `---` lines is Python. Imports are resolved when the component is compiled;
the rest runs on every request, so it can read request state. `prop[type]` declares a property and
`= value` gives a default; a property without a default must be passed by the parent.

The body is Jinja2 with the frontmatter variables and the properties in scope. Autoescaping is
**off**: `{{ value }}` is inserted as written. Escape untrusted values with `{{ value | e }}`, and
wrap JavaScript containing `{{` or `{%` in `{% raw %}...{% endraw %}`.

Declare props before using them: an undeclared variable renders as an empty string. Keep side
effects inside functions - the frontmatter runs again on every request.

### Components

Import a `.nexy` component and use it as a tag; children go through `<slot />`:

```nexy
---
from "@components/card.nexy" import Card
---
<Card title="Hello">
  <p>Child content</p>
</Card>
```

Aliases come from `useAliases`. The common setup maps `@` to `src/`, so `@components/card.nexy`
means `src/components/card.nexy`.

Import a client component by path; the compiler mounts it and passes the attributes as props:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`<style>` blocks are emitted with the page that declares them and are not scoped. Prefix your
classes.

### Markdown and MDX

A `.md` file is pure content: rendered with `cmarkgfm`, heading IDs added, a table of contents
derived, then wrapped in the nearest `layout.*`. Frontmatter there is not Python logic; use `.nexy`
when you need server logic. Locale variants such as `about.fr.md` are supported.

`.mdx` is compiled by the framework pipeline and needs React or Preact. The framework is detected
from imports; if both are imported, React wins.

### Client frameworks

```python
# nexyconfig.py
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()  # vue(), svelte(), solid(), preact()
```

With a framework enabled, its extensions become active routes, and `nx new` sets it up with Vite and
Tailwind. `useVite` defaults to `True`.

A framework route is a normal page, not a client-only island: the HTML exists before the bundle
runs, so the first paint does not wait for JavaScript.

## Built-in components

They return HTML strings and are used two ways: as a Jinja call or as an HTML-style tag. The
compiler turns the tag into the call, so both lines below are equivalent.

```nexy
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

Tags are self-closing, attributes are keyword arguments, and `True` / `False` / numbers stay
unquoted (`controls` alone would become an empty string - write `controls=True`).

| Helper | Signature |
|---|---|
| `Image` | `Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` |
| `Link` | `Link(href, children="", class_name=None, prefetch=True, **attrs)` |
| `Audio` | `Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` |
| `Video` | `Video(src, width=None, height=None, ...)` |
| `Import` | `Import(path, framework, symbol)`, same as importing a component in Python |

`Link` renders `<a data-nexy-link>` and is handled by the client router; `prefetch=True` warms the
target on hover or touch. `sources` adds `<source>` tags with the MIME type derived from each
extension.

`Template().render(path, context)` renders a template file and `Template().invalidate(path)` drops
it from the cache. `Vite()` returns the client tags for the current mode; Nexy calls it for every
page.

`Form` and `Script` are exported placeholders with no behaviour yet.

## Hooks

Hooks read the current request from inside a `.nexy` page. They only work while a request is being
handled; calling one elsewhere raises `RuntimeError`.

| Hook | Returns |
|---|---|
| `usePathname()` | request path, e.g. `"/blog/post-1"` |
| `useSearchParams()` | query string as `dict[str, str]`, first value per key |
| `useQuery()` | dynamic path parameters, e.g. `{"slug": "post-1"}` |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | all cookies as `dict[str, str]` |
| `useSession()` | the session dict, `{}` when sessions are not enabled |
| `useToc(depth_range="2-6")` | table of contents HTML, `""` when there is none |
| `useViews(path, context=None)` | renders another view and returns an `HTMLResponse` |

```nexy
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

`useSession()` needs `useSession = {...}` in `nexyconfig.py`. `useRouter()` here is the request hook,
not the config field.

## Config

Configuration is a class in `nexyconfig.py` at the project root. Nexy loads it from the directory it
runs in; a project without the file uses the defaults.

```python
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useHost = "0.0.0.0"
    useTitle = "My App"
    useAliases = {"@": "src/"}
```

| Field | Default | Meaning |
|---|---|---|
| `usePort` | `3000` | port for `dev` and `start` |
| `useHost` | `"0.0.0.0"` | bind address |
| `useSslKeyfile`, `useSslCertfile` | `None` | serve HTTPS directly |
| `useCSR` | `False` | client-side routing; disables `.nexy` routes |
| `useRouter` | `None` | an `APIRouter` or module mounted next to the file-based routes |
| `excludeDirs` | `["templates", "extension", "docs"]` | directories skipped when scanning routes |
| `useAliases` | `None` | import aliases, e.g. `{"@": "src/"}` |
| `useFF` | `None` | `react()`, `vue()`, `svelte()`, `solid()` or `preact()` |
| `useVite` | `True` | build and serve client bundles with Vite |
| `useMarkdownExtensions` | `[]` | extra extensions for `.md` and `.mdx` |
| `useDocs` | `True` | serve the OpenAPI schema and the Scalar page |
| `useDocsUrl` | `"/docs"` | path of that page |
| `useTocDepth`, `useTocTitle`, `useTocAuto` | `"2-6"`, `"Table of Contents"`, `True` | table of contents |
| `useMiddlewares`, `useCORS`, `useGZip`, `useTrustedHost`, `useSession`, `useAuth` | `[]`, `None` | middleware |
| `useHTTPSRedirect` | `False` | redirect HTTP to HTTPS |

Reserved-name extensions are configurable too: `useLayoutExtensions = ["md"]` makes `layout.md`
reserved exactly like `layout.nexy`. The same exists for `notfound`, `errors` and `loading`.

Three fields are declared but read by nothing: `useViteDevUrl`, `useLocaleDetection`, `useRTL`.
`useRedocsUrl` is read but no route is mounted for it. Setting any of them has no effect.

## i18n

```python
class NexyConfig(NexyConfigModel):
    useLocales = ["en", "fr"]
    useDefaultLocale = "en"
    useLocaleCookieName = "nexy-locale"
    useLocalesDir = "locales"            # runtime locale files
    useLocalesSourceDir = "src/locales"  # source for `nx translate`
```

For every request, the locale is resolved in this order: the URL prefix `/fr/...` (stripped from the
path before routing), the `nexy-locale` cookie, `Accept-Language`, then `useDefaultLocale`.

```python
from nexy import current_locale, t, trans, useLocale

trans("hero.title", "Hello")   # dotted key, default, current locale
t("hero.title", "Hello")       # alias
current_locale.get()           # "fr"
useLocale()                    # {"locale", "is_rtl", "available", "default", "trans"}
```

`trans` is available in every template:

```html
<h1>{{ trans("hero.title", "Hello") }}</h1>
```

A missing key falls back to the default, then to the key itself.

`useLocalesDir` holds one file per locale, with nested objects matching the dotted keys
(`locales/fr.json`, `locales/en.json`); a `<locale>.py` exporting a `translations` dict works too.

`@i18n()` classes give you class attributes that translate at access time, and `nx translate`
scans them under `useLocalesSourceDir`, translates them and writes generated packs to
`__nexy__/i18n/`:

```python
from nexy.modules.i18n import i18n


@i18n()
class Home:
    title = "Hello"
```

```bash
nx translate --source en --target fr
```

The command uses an online translator and needs network access.

## Actions

`@Action` turns a function into a `POST` endpoint with a generated path, so a page can call server
code without declaring a route file.

```python
# src/actions/user.py
from nexy.decorators import Action


@Action
async def create_user(name: str) -> dict:
    return {"name": name}
```

At startup Nexy imports every module under `src/`, registers each action, and mounts it at
`POST /_nx_<hash>`. Parameters and body models follow the function signature, like any FastAPI
route.

Inside a `.nexy` template an action is exposed three ways:

| Variable | Content |
|---|---|
| `create_user` | the function itself, callable in the template |
| `__actions["create_user"]` | the same function, by name |
| `__actions_path["create_user"]` | the generated URL |

```nexy
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

The path is deterministic - a hash of the function's module and name. It keeps the endpoint out of
casual discovery but it is not a secret; do not rely on it for authorization. No TypeScript client
is generated by the current build.

## CLI

The binary is `nx`, also installed as `nexy`. Without a global install, prefix with `uvx nexy`.

| Command | Alias | What it does |
|---|---|---|
| `nx dev` | `nx d` | development server: compile on change, Vite, HMR |
| `nx start` | `nx s` | production server on the compiled output |
| `nx build` | `nx b` | production build |
| `nx new` | `nx n` | scaffold a project |
| `nx init` | `nx i` | add Nexy to an existing project |
| `nx migrate` | `nx m` | migrate from another framework |
| `nx check` | `nx c` | type-check: mypy on Python, `tsc` on TypeScript |
| `nx format` | `nx f` | format Python, JS/TS and `.nexy` files |
| `nx test` | - | run pytest; `--client` adds vitest |
| `nx translate` | `nx t` | generate locale files |

Common flags: `--port` and `--host` for `dev` and `start` (defaults from `usePort` and `useHost`);
`--check` for `build` (runs ruff and mypy after the build) and for `format` (report instead of
rewrite); `--template` / `-t` for `new`; `--client` and `--no-server` for `test`.

## Testing

`nx test` runs pytest. Extra arguments are forwarded to it:

```bash
nx test                 # pytest
nx test -k create_user  # forwarded to pytest
nx test --client        # pytest, then vitest
```

pytest runs on `tests/` when that directory exists, otherwise on the project root. If pytest is not
installed, the run is skipped with a warning. vitest runs with `npx vitest run`, and only when
`vitest.config.ts` exists or `vitest` appears in `package.json`. There is no built-in end-to-end
runner: drive the app with `TestClient` for server behaviour, and add Playwright or Cypress yourself
for the browser.

A server test uses the ASGI app directly:

```python
# tests/test_pages.py
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

For per-test isolation, build a fresh application instead of reusing the module-level one:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


with TestClient(AppServer().run()) as client:
    assert client.get("/api/hello").json() == {"message": "Hello"}
```

`AppServer().run()` reads `nexyconfig.py` from the working directory and assembles routes,
middleware and locale state. Test API handlers with `client.get` / `client.post`; test actions by
posting to `__actions_path["create_user"]`, which the rendered page exposes.

## Build and deploy

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

`nx build` writes everything to `__nexy__/`: the compiled Python routes, the client bundle under
`__nexy__/client/`, and the pre-rendered HTML for framework routes. `nx start` runs Uvicorn on that
output - Python only, no Node process and no Vite process at runtime.

Deploy by copying the project with `__nexy__/`, or build inside the image. The build stage needs
Node and Python; the runtime stage needs Python only.

```dockerfile
FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

Static hosting is a deployment choice, not a build mode: there is no `--static` flag. Put static
files in `public/`; they are served from `/` in development and production. Behind a reverse proxy,
remember to forward WebSocket upgrade requests.

## How it works

- A `.nexy` file is compiled to a Python module in `__nexy__/`, mounted through a virtual file
  system, and rendered with Jinja2 at request time.
- Framework routes are pre-rendered to HTML at build time by a per-file esbuild pipeline; the worker
  pool runs one file per worker, sized to the CPU count. A route whose server render fails is
  reported as client-only instead of failing the build.
- In development, the watcher recompiles what changed and restarts Uvicorn cleanly - no importlib
  hacks, no stale modules. Vite runs on an internal port and Nexy proxies it through the app origin.
- In production, one Uvicorn process serves the routes, the HTML and the assets from one origin.

Internals, request lifecycle and compiler pipeline: [ARCHITECTURE.md](ARCHITECTURE.md).

## How it compares

| Feature | Nexy | Next.js | Django + HTMX | Remix |
|---|---|---|---|---|
| Language | Python + any JS framework | JS/TS only | Python + HTMX | JS/TS only |
| Server process | Uvicorn + FastAPI, one process | Node | Python (ASGI/WSGI) | Node |
| Startup | < 1 s | 10-30 s | 3-8 s | 8-15 s |
| HMR | < 100 ms | ~500 ms | N/A | ~300 ms |
| File format | `.nexy` (Python + Jinja2 + UI) | `.tsx` / `.jsx` | `.py` + `.html` | `.tsx` |
| SSR | Built-in (esbuild) | Built-in (React) | Manual | Built-in (React) |
| SSG | Parallel worker pool | `next export` | Third-party | Via Vite |
| Routing | File-based + modular | File-based | Manual | File-based |

## Framework support

| Framework | SSR | SSG | HMR |
|---|:---:|:---:|:---:|
| React | ✓ | ✓ | ✓ |
| Vue | ✓ | ✓ | ✓ |
| Svelte | ✓ | ✓ | ✓ |
| Solid | ✓ | ✓ | ✓ |
| Preact | ✓ | ✓ | ✓ |
| None (vanilla) | ✓ | - | ✓ |

## Documentation

This README covers the whole framework. The pages below go deeper on one topic each, in plain
Markdown, and are written from the code.

| I want | Read |
|---|---|
| to create a project and run it | [Getting started](docs/getting-started.md) |
| the files and folders | [Project structure](docs/project-structure.md) |
| the URL of a file | [Routing](docs/routing/README.md) |
| dynamic segments, layouts, error pages | [Pages](docs/routing/pages.md) |
| the current path, query, cookies, session | [Hooks](docs/routing/hooks.md) |
| to write a page | [.nexy files](docs/views/nexyfile.md) |
| Markdown or MDX | [Markdown](docs/views/markdown.md) |
| built-in HTML helpers | [Components](docs/views/components.md) |
| SSR, CSR, ISR | [SSR](docs/routing/fbr/ssr.md), [CSR](docs/routing/fbr/csr.md), [ISR](docs/routing/fbr/isr.md) |
| a WebSocket | [WebSocket](docs/routing/fbr/websocket.md) |
| controllers and modules | [Modular routing](docs/routing/modular.md) |
| to add an endpoint | [API](docs/api.md) |
| a form posted from a page | [Actions](docs/actions.md) |
| translations | [i18n](docs/i18n.md) |
| a config field | [Config](docs/config.md) |
| the client build and Vite | [Frontend](docs/frontend.md) |
| every command and flag | [CLI](docs/cli.md) |
| to test a project | [Testing](docs/testing.md) |
| build output and Docker | [Deploy](docs/deploy.md) |
| rules for an AI agent | [Agents](docs/agents.md) |

[llms.txt](llms.txt) is the same map in one file, for tools that read plain text.

## Contributing

Contributions are welcome - seasoned engineers and first-time PR authors alike.

- [Good first issues](https://github.com/NexyPy/nexy/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
- [CONTRIBUTING.md](CONTRIBUTING.md) - setup, quality gates, pull requests
- [ARCHITECTURE.md](ARCHITECTURE.md) - internals
- [Discussions](https://github.com/NexyPy/nexy/discussions) and [Discord](https://discord.gg/nexy)
- [Issues](https://github.com/NexyPy/nexy/issues) - bugs and feature requests

Security issues: see [SECURITY.md](SECURITY.md). Do not open a public issue for a vulnerability.

## License

[MIT](LICENSE) - free forever, built in the open.
