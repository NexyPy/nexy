# Quick start

You will create a Nexy project, run it, and see a page change as you edit it. It takes three
minutes. The [Tutorial](tutorial.md) then adds an endpoint and a production build.

## Before you start

| You need | Why |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | provides `uvx`, creates the project and installs its packages |
| Node.js 18+ | only if you use a client framework (React, Vue, Svelte, Solid, Preact) |

No uv yet? See [Installation](installation.md).

## 1. Create the project

```bash
uvx nexy new my-app
```

`uvx` comes with uv, so install uv first. It runs Nexy in a temporary environment, enough to **create** the project. `nexy new` then makes
the project's own `.venv` and installs its packages there. Four prompts decide the wiring:

| Prompt | Effect |
|---|---|
| File-based router? | `Yes` scans `src/routes/`; `No` scaffolds the modular router in `src/apps/` |
| Project type | `Web` adds a layout and client assets, `API` starts without views |
| Client component? | adds a framework and its Vite setup |
| ORM / database | adds a model layer, or nothing |

Not sure? Answer `Yes`, `Web`, and no client component. You can add each later.

## 2. Run it

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Open <http://localhost:3000>. You should see the starter page. The port comes from `usePort`
(default `3000`); `--port` and `--host` override it per run.

> [!NOTE]
> Run every command except `new` and `init` inside the project's virtual environment, or prefix it
> with `uv run`, as in `uv run nexy dev`. Outside it, a project that needs `sqlmodel` fails with
> `No module named 'sqlmodel'`.

## 3. Change a page

A file under `src/routes/` is a route. Create `src/routes/hello.nexy`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Open <http://localhost:3000/hello>. Change `"Hello"` to `"Bonjour"` and save: the page updates
without a manual reload. If the code is wrong, the browser shows the error instead of a blank page.

`prop[str]` declares a typed property. The markup under the frontmatter is Jinja2 - see
[.nexy files](../views/nexyfile.md).

## Where next

| You want to | Read |
|---|---|
| Add a Python endpoint and ship a build | [Tutorial](tutorial.md) |
| Know where each file belongs | [Project structure](project-structure.md) |
| Understand who builds what | [How Nexy works](how-nexy-works.md) |
| Use React, Vue, Svelte, Solid or Preact | [Views](../views/README.md) |
