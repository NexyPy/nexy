# Coming from another framework

Nexy is FastAPI plus file-based routing, server-rendered pages and optional React, Vue, Svelte,
Solid or Preact islands. This page maps what you already know.

Each framework below also has a page of its own, task by task, with the code you know and then the
Nexy code:

| Python | Backend | Fullstack JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Express](../coming-from/express.md), [Fastify](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Elysia](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Spring Boot](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## From FastAPI

<!-- router:fbr,custom -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in a module you import | `GET` function in `src/routes/users.py` |
| `app.include_router(router)` | the file path is the URL; nothing to register |
| Path param `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | still `Depends(...)`: handlers are FastAPI handlers |
| Jinja2 `TemplateResponse` | a `.nexy` page next to the endpoint |
| Run with `uvicorn main:app` | `nx dev`, then `nx build && nx start` |

Everything under `src/routes/*.py` is ordinary FastAPI: dependencies, Pydantic models, middleware
and `/docs` keep working.

The same endpoint, before and after:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in a module you import | `async def get(self)` in a `@Controller("/users")` class |
| `app.include_router(router)` | the controller listed in the `controllers` of a `@Module` |
| Path param `/users/{id}` | `@Controller("/users/{id}")`, with `async def get(self, id: int)` |
| `Depends(...)` | still `Depends(...)`: a controller method is a FastAPI endpoint |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, returned by the method |
| Run with `uvicorn main:app` | `nx dev`, then `nx build && nx start` |

Dependencies, Pydantic models, middleware and `/docs` keep working.

The same endpoint, before and after:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## From Next.js

<!-- router:fbr,custom -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` or `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (owns `<html>`) | `src/routes/layout.tsx` with `useCSR = True` (React), or `src/routes/layout.nexy` in server mode |
| nested `layout.tsx` | nested `layout.tsx` / `layout.vue` / `layout.svelte` in client mode, nested `layout.nexy` in server mode |
| `use client` components in a server page | [islands](../rendering/islands.md) in server mode |
| Route handlers `route.ts` | `src/routes/api/x.py`, written in Python |
| `(group)` folders | same: `(group)/` |
| Server Actions | [`@Action`](../guides/actions.md) functions called from a form or as typed client functions |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

The backend is Python, so your API shares code with your data and ML work. Client components
hydrate as islands instead of a whole-page React tree.

A Next.js page moves over almost as it is, and its `"use client"` component becomes an island of a
server page:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | a controller that returns `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, with `async def get(self, slug: str)` |
| `app/layout.tsx` (owns `<html>`) | a layout view the controller wraps around its view, through `children` |
| `use client` components in a server page | [islands](../rendering/islands.md) in a view |
| Route handlers `route.ts` | a controller that returns a dict, written in Python |
| Server Actions | [`@Action`](../guides/actions.md) functions called from a form or as typed client functions |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

The backend is Python, so your API shares code with your data and ML work. Client components
hydrate as islands instead of a whole-page React tree.

A Next.js page becomes a controller and its view, and its `"use client"` component an island of the
view:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## From Express or Node backends

<!-- router:fbr,custom -->
| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` with `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, registered from `nexyconfig.py` |
| `res.json(obj)` | return a dict or a Pydantic model |
| EJS / Pug views | `.nexy` (Jinja2) pages |
| `npm run dev` | `nx dev` |

`app.use(...)` becomes a field of `nexyconfig.py`, and `res.json(...)` becomes a return value:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, with `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI middleware, registered from `nexyconfig.py` |
| `res.json(obj)` | return a dict or a Pydantic model |
| EJS / Pug views | `.nexy` (Jinja2) views, returned by `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` becomes a field of `nexyconfig.py`, and `res.json(...)` becomes a return value:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## Choosing a router

| Use | When |
|---|---|
| File-based router | pages and endpoints mapped from files; the default |
| Modular router | controllers, modules and dependency injection, NestJS-style |

The modular router in two files: a controller, and the module `nexyconfig.py` points at with
`useRouter = AppModule`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

Both are scaffolded by `nx new` and covered by the same end-to-end tests. See
[Routing](../routing/README.md) and [Modular routing](../routing/modular/README.md).

## Where next

- [Quick start](quick-start.md): create a project and run it
- [Project structure](project-structure.md): where each file belongs
- [Routing](../routing/README.md): choose the router
