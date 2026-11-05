# What is Nexy?

Nexy is a Python framework for fullstack web applications: your pages and your API live in one
project and are served by one server.

## What you get

- **Pages in Python.** A `.nexy` file is HTML with a few lines of Python on top; a `.md` file is a
  page too. No JavaScript is needed to render a page.
- **An API in the same project.** A `.py` file under `src/routes/` answers HTTP requests: a function
  named `GET` answers `GET`, a function named `POST` answers `POST`.
- **API documentation for free.** Every API route appears in an OpenAPI schema, and Scalar shows it
  as an interactive reference at `/docs`.
- **Forms that call Python.** A form, or a typed call from the browser, reaches the same Python
  function.
- **A frontend framework when you want one.** React, Vue, Svelte, Solid or Preact, for one
  component or for the whole site.
- **One command to work, one to ship.** `nx dev` reloads as you save; `nx build` prepares
  production.

## What it is built on

The current version, 2.2, stands on tools you may already know:

| Part | Built on | What it means for you |
|---|---|---|
| Server and API | [FastAPI](https://fastapi.tiangolo.com/) | an API route is a FastAPI route: Pydantic validation and dependencies work as usual |
| API reference | OpenAPI and [Scalar](https://scalar.com/) | the schema is at `/openapi.json`, the reference at `/docs` |
| Pages | Jinja2 | a `.nexy` page uses Jinja2 tags such as `{{ title }}` |
| Frontend (optional) | [Vite](https://vite.dev/) | only with a frontend framework, which also needs Node.js |

## A first page and a first endpoint

A page, at `/hello`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

An endpoint, at `GET /api/items`, listed at `/docs` without any extra code:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## What Nexy leaves to you

The database, the login and the rules about who may do what belong to your application, so you
choose the libraries. [Databases](../guides/databases.md) and
[Middleware and security](../guides/middleware-and-security.md) show where each one plugs in.

## Next steps

- [Installation](installation.md): install uv and create a project
- [Quick start](quick-start.md): run it, change a page, build it
- [Core concepts](core-concepts.md): the few words the rest of the docs use
