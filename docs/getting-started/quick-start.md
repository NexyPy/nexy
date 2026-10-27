# Getting started

Create a Nexy project, run it, and build it for production.

## Requirements

| Requirement | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | runs Nexy without a global install |
| Node.js 18+ | only if you use a client framework (React, Vue, Svelte, Solid, Preact) |

## Create a project

```bash
uvx nexy new my-app
```

`uvx` fetches Nexy and runs the `new` command, so nothing is installed globally.

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
nx dev
```

Open <http://localhost:3000>. The port comes from `usePort` (default `3000`); `--port` and `--host`
override it per run.

> **Good to know**: without a global install, run `uvx nexy dev` instead of `nx dev`. `uv tool
> install nexy` adds the `nx` and `nexy` binaries to your PATH.

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
