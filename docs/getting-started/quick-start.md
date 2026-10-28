# Getting started

Create a Nexy project, run it, and build it for production.

## Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | provides `uvx`, creates the project and installs its packages |
| Node.js 18+ | only if you use a client framework (React, Vue, Svelte, Solid, Preact) |

## Create a project

```bash
uvx nexy new my-app
```

`uvx` comes with uv, so install uv first (see [Installation](installation.md)). It runs Nexy in a
temporary environment, which is enough to **create** the project. `nexy new` then makes the project's
own virtual environment, `.venv`, and installs its packages there.

Four prompts decide how the project is wired:

| Prompt | Effect |
|---|---|
| File-based router? | `Yes` scans `src/routes/`; `No` scaffolds the modular router in `src/apps/`, mounted with `useRouter` |
| Project type | `Web` adds a layout and client assets, `API` starts without views |
| Client component? | adds a framework and its Vite setup |
| ORM / database | adds a model layer, or nothing |

## Start the dev server

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Open <http://localhost:3000>. The port comes from `usePort` (default `3000`); `--port` and `--host`
override it per run.

> **Good to know**: run `nexy dev`, `build`, `migrate` and every command except `new` and `init`
> inside the project's virtual environment, where your packages are. To skip the activation, use
> `uv run nexy dev`. Outside it, a project that needs `sqlmodel` fails with `No module named
> 'sqlmodel'`.

## Create your first page

A file under `src/routes/` is a route. `src/routes/index.nexy` is served at `/`:

```nexy filename="src/routes/index.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

`prop[str]` declares a typed property. The markup under the frontmatter is Jinja2 - see
[.nexy files](../views/nexyfile.md).

## Create your first endpoint

A `.py` file under `src/routes/` is an API handler. `src/routes/api/hello.py` is served at
`/api/hello`:

```python filename="src/routes/api/hello.py"
from fastapi import Request


async def GET(request: Request):
    return {"message": "Hello"}
```

```bash
curl http://localhost:3000/api/hello
```

The function name is the HTTP method - see [API](../routing/fbr/handlers/README.md).

## Build and serve

```bash
nx build
nx start
```

`nx build` compiles your routes into `__nexy__/`; `nx start` runs Uvicorn on that output. No Node
process and no Vite process are needed at runtime.

## Next steps

- [Project structure](project-structure.md): where each file belongs
- [Routing](../routing/README.md): dynamic segments, groups, layouts
- [Views](../views/README.md): `.nexy`, Markdown, React, Vue, Svelte, Solid, Preact
