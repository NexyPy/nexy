# Core concepts

The words the rest of the docs use - route, page, view, component, handler, endpoint - each in one
line, with a link to the page that goes deeper. New to Nexy? Start with
[What is Nexy?](what-is-nexy.md).

## How to read these docs

| Level | The question it answers | Start with |
|---|---|---|
| Application architecture | which layer answers a request, and what it refuses to do | [How Nexy works](how-nexy-works.md) |
| Application structure | where the code lives, and what a file becomes | [Project structure](project-structure.md) |
| Presentation and rendering | what the reader sees, and who produces the HTML | [Views](../views/README.md), [Rendering](../rendering/README.md) |
| Application interaction | what the reader does, and what runs in response | [Actions](../guides/actions.md) |

The levels are read in that order once. After that, a page you need is a lookup, not a course.

## Application architecture

Three ways to decide which code answers a URL. They are alternatives, not layers:

- **File-based routing (FBR)**: a file under `src/routes/` is a route. The default.
- **Modular router**: controllers and modules under `src/apps/`, declared with decorators, for a
  NestJS-style codebase.
- **Custom router**: an existing FastAPI `APIRouter` included in the application.

The choice is one line of the `NexyConfig` class in `nexyconfig.py`.

<!-- router:fbr -->
File-based routing needs no line: without `useRouter`, Nexy reads `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
The modular router is the root module of `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
A custom router is an `APIRouter` you already have:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Choosing one of the three is one decision. Choosing a frontend framework is another, separate one:
see [Choose a router](../routing/README.md) and [Views](../views/README.md).

## Application structure

Five notions that a reader coming from Next.js usually merges into one. They are not the same thing,
and the difference explains most "why is my page not rendering" questions.

| Notion | What it is | What it is not |
|---|---|---|
| **Route** | a URL pattern, produced by the path of a file | a file: one file can answer several URLs (`[slug]`) |
| **Page** | a route file that renders a view: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | an endpoint: it answers a document, not data |
| **View** | what produces the body of a page: Jinja2 and Python, Markdown, or a client component | a route: the same view can serve several pages |
| **Component** | a reusable piece a page imports | a route: in server mode a component is never served on its own |
| **Route handler** | the function of a `.py` route file, named after the HTTP method (`GET`, `POST`, …) | a page: it returns JSON, a file or a `Response` |
| **Endpoint** | the pair (URL, method) that a handler answers | a handler: one file can answer several endpoints |

In one sentence: **a page is a route file, a view is what renders it, a component is what a page
reuses, a handler answers an endpoint.**

<!-- router:fbr -->
All five in one small project:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

The frontmatter and the template below it are the view of the page; `Like` is the component it
reuses.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
With the modular router, a route is the path of a controller, and a handler is one of its methods,
named after the HTTP verb:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

A page is still a file of `src/routes/`, or a view a controller returns with `useViews`.
<!-- /router -->

<!-- router:custom -->
With a custom router, a route is a path of your `APIRouter`, and a handler is the function its
decorator registers:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Pages are still files of `src/routes/`: a `.nexy` page answers next to the included routes.
<!-- /router -->

Two more words that come back everywhere:

- **Layout**: a `layout.*` file that wraps the pages below its folder; the root one owns the HTML
  document. See [Layouts](../routing/fbr/layouts/README.md).
- **Dependency**: a function that runs before a handler, applied per route or per folder. See
  [Dependencies](../routing/fbr/dependencies/README.md).

## Presentation and rendering

Two independent decisions, often confused:

- **The format** decides which file renders the page: [Views](../views/README.md).
- **The mode** decides who produces the HTML and when: [Rendering](../rendering/README.md).

| Notion | One line |
|---|---|
| Server mode | the server renders `.nexy` and `.md` pages; components are islands ([modes](../routing/fbr/modes.md)) |
| Client mode | `useCSR = True`: framework files are the routes, and navigation happens in the browser |
| SSR, ISR, CSR, islands | four rendering modes, decided per page except CSR, which is per project ([rendering](../rendering/README.md)) |
| Hydration | the browser attaching a framework to HTML the server already sent ([islands](../rendering/islands.md)) |
| Props | the values a parent passes to a component, declared `name: prop[type]` in a `.nexy` file ([.nexy files](../views/nexy/README.md)) |

A server-mode page with one island: the server renders the page, the browser hydrates the chart
only when it scrolls into view.

```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

## Application interaction

| Notion | One line |
|---|---|
| Action | a Python function marked `@Action`, served as a `POST`, callable from a form or as a typed function ([actions](../guides/actions.md)) |
| Form | an HTML form that posts to an Action, with validation errors coming back to the page ([actions](../guides/actions.md)) |
| Navigation | links that prefetch, and hooks that read the path, the query, the cookies and the session ([hooks](../routing/fbr/navigation/hooks.md)) |
| Data fetching | done by the page or the handler that needs it; Nexy ships no client data layer ([handlers](../routing/fbr/handlers/README.md)) |

An action and the form that posts to it, which works before any script loads:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```

## What Nexy does not do

Authentication, authorisation, database, internationalisation, background jobs, email, payments and
search are **your application's responsibility**, not the framework's. Nexy gives the extension
points and says where to plug each one: see [What Nexy leaves to you](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
Authentication, for example, plugs into a dependency of the folder it protects. Nexy runs it before
every route below; who the user is stays your decision:

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
Authentication, for example, plugs into a guard on the controller it protects. Nexy runs it before
every handler of the class; who the user is stays your decision:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
Authentication, for example, plugs into a dependency of the router it protects, as in FastAPI;
who the user is stays your decision:

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

The reason is not minimalism for its own sake: a framework that picks your ORM or your auth library
has decided something only your application can decide.

## Next steps

- [Project structure](project-structure.md): every folder and file of a project
- [Glossary](../reference/glossary.md): the same words, in one alphabetical index
- [How Nexy works](how-nexy-works.md): the layers, who builds what, and what Nexy leaves to you
