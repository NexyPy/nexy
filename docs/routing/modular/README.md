# Modular routing

Modular routing uses classes with decorators instead of files under `src/routes/`: controllers
handle requests, modules group them, and providers are injected. Mount the resulting `APIRouter`
with `useRouter` in `nexyconfig.py`.

**Before you start:** a Nexy project and one working page. The modular router replaces the
file-based one, so read [Routing](../README.md) first if you have not chosen a router yet.

| Page | What it covers |
|---|---|
| This page | Mount a module, write a controller, group controllers |
| [Dependency injection](dependency-injection.md) | `@Injectable`, scopes, the container |
| [Guards and metadata](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy and NestJS](vs-nestjs.md) | What matches NestJS and what does not |

## Set up the router

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> file-based routing keeps working. If `src/routes/` exists, it is scanned even
> when `useRouter` is set.

## Write a controller

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Methods are matched by name, case-insensitively: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`.

A controller declares one handler per HTTP method; a duplicate raises at startup. Add a prefix with
`@Controller(prefix="/users")` - every handler is mounted on `prefix/`. `async def SOCKET(...)` on a
controller registers a WebSocket at the same path.

## Group controllers in a module

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` returns an `APIRouter`. `controllers` is required; `providers`, `imports`
and `exports` are optional. Imported modules are mounted as sub-routers, and their exported providers
are resolved at startup.

## Views from a controller

A controller can return a page. `useViews` renders a `.nexy` view; nest one inside another to wrap it
in a layout:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

See [Layouts](../fbr/layouts/README.md).

## Example

See `examples/Modular/api/minimal/`.

## Next steps

- [Dependency injection](dependency-injection.md): services and scopes
- [Guards and metadata](guards-and-metadata.md): protect and document routes
- [Routing](../README.md): the file-based router
- [Config](../../reference/config.md): every option, including `useRouter`
