# Project structure

Every file in a Nexy project has one job, and where it goes depends on the router: `src/routes/`
for file-based routing, `src/apps/` for the modular router.

## Top level

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

To choose a folder, ask what the file is:

- **Something the browser can open** - a route: `src/routes/`.
- **A piece used by several routes** - a component or a module: `src/components/`, `src/`.
- **A file served as it is** - `public/`.
- **Generated** - `__nexy__/`; never edit it.

> [!WARNING]
> `src/routes/` is scanned: a helper placed there becomes a route. Put a helper that is not a route
> outside `src/routes/`, or start its name with `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

To choose a folder, ask what the file is:

- **A URL** - a method of a controller in `src/apps/`, registered by its module.
- **A page** - a `.nexy` view next to its controller, returned with `useViews`.
- **A piece used by several views** - `src/components/`.
- **A file served as it is** - `public/`.
- **Generated** - `__nexy__/`; never edit it.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

To choose a folder, ask what the file is:

- **A route of the included app** - where it already is, here `src/legacy/`.
- **A new page or route** - `src/routes/`, next to the included router.
- **A file served as it is** - `public/`.
- **Generated** - `__nexy__/`; never edit it.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Every file becomes a route, except the reserved names below. The file path minus the extension is
the URL - see [file-based routing](../routing/fbr/README.md).

| File | Role |
|---|---|
| `layout.nexy` | wraps sibling and child pages |
| `errors.nexy` | 500 page for the directory |
| `notfound.nexy` | 404 page for the directory |
| `dependencies.py` | shared FastAPI dependencies for the directory |
| `__init__.py` | Python package marker |
| `loading.nexy` | reserved - excluded from routes, but it has no runtime effect yet |

Each page name also exists per framework. With `react()` configured, `layout.jsx` and `layout.tsx`
are reserved exactly like `layout.nexy`. The lists are built in `nexy/core/config.py`
(`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` and `errors.nexy` are only installed when a copy exists at the
> routes root. A copy in a subdirectory then refines the page for that prefix.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

A controller answers URLs, a module groups controllers and providers, and the root module is
mounted with `useRouter` in `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

No file in `src/apps/` is a route by its name: only the controllers a module lists answer. See
[modular routing](../routing/modular/README.md).
<!-- /router -->

## `public/`

Files here are served from the site root: `/favicon.ico`, `/robots.txt`, images, fonts.

## `__nexy__/`

Generated by `nx build` (and by `nx dev` for the parts it needs). It contains:

- the compiled `.nexy` files, as a Python package (`__nexy__/src/...`);
- the generated client entry points (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` after a Vite build - assets, manifest, pre-rendered HTML;
- `build-cache.json`.

Treat the whole directory as disposable: delete it, rebuild it. Editing it by hand loses the change
on the next build. Add it to `.gitignore`.

## Next steps

<!-- router:fbr -->
- [File-based routing](../routing/fbr/README.md): how a path becomes a URL
<!-- /router -->
<!-- router:modular -->
- [Modular routing](../routing/modular/README.md): controllers, modules and providers
<!-- /router -->
<!-- router:custom -->
- [Custom routing](../routing/custom/README.md): include an existing FastAPI router
<!-- /router -->
- [Config](../reference/config.md): every project option
- [Frontend](../guides/frontend.md): Vite, styling and the client build
