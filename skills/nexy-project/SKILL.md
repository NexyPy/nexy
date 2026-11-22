---
name: nexy-project
description: Layout of a Nexy project, its mode, file conventions under src/routes, config in nexyconfig.py, and the nx commands. Load it before creating, moving or renaming files.
---

# A Nexy project

A route is a file under `src/routes/`. The file path is the URL.

<!-- nexy:web -->
## The mode decides the page files

`useCSR` in `nexyconfig.py` decides everything else. Mixing the files of both modes is rejected
before `nx dev`, `nx start` and `nx build` run. One client framework per project.
<!-- /nexy:web -->

<!-- nexy:server -->
This project is server-rendered (`useCSR = False`):

| | |
|---|---|
| Pages | `.nexy`, `.md`, `.mdx` |
| Document owner | root `layout.nexy` |
| Client components | islands imported from a `.nexy` page |
| Navigation | full page loads |
<!-- /nexy:server -->

<!-- nexy:client -->
This project is client-routed (`useCSR = True`):

| | |
|---|---|
| Pages | `.tsx`, `.vue` or `.svelte`, of the framework of `useFF` |
| Document owner | root `layout.tsx`, `layout.vue` or `layout.svelte` |
| Client components | the pages and the components they import |
| Navigation | in the browser; layouts stay mounted |
<!-- /nexy:client -->

<!-- nexy:api -->
This project serves an API: Python handlers and no views. Errors answer JSON to a client that
asks for it (`Accept: application/json`).
<!-- /nexy:api -->

## Layout

<!-- nexy:web -->
```text
nexyconfig.py          configuration, the only place for settings
src/
  routes/              pages and API handlers; the file path is the URL
  components/          components imported by pages; never routes
  actions/             @Action functions
  apps/                controllers and modules of the modular router
  globale.css          design tokens and base styles
public/                static files served from /
__nexy__/              generated; never edit, never commit
```
<!-- /nexy:web -->
<!-- nexy:api -->
```text
nexyconfig.py          configuration, the only place for settings
src/
  routes/              API handlers; the file path is the URL
  apps/                controllers and modules of the modular router
__nexy__/              generated; never edit, never commit
```
<!-- /nexy:api -->

## File conventions in `src/routes/`

| File | Becomes |
|---|---|
| `index.*` | the route of its directory |
| `about.*` | `/about` |
| `[slug].*` | dynamic segment |
| `[...path].*` | catch-all |
| `(group)/page.*` | `/page`; the group is not in the URL |
| `name.py` | API handler; functions `GET`, `POST`, ... are the methods |
| `middleware.py`, `dependencies.py` | applied to the directory and below |

<!-- nexy:web -->
`layout.*` wraps every page below it, and the root one owns the document.
<!-- /nexy:web -->
<!-- nexy:server -->
`notfound.nexy` and `errors.nexy` are the 404 and 500 pages of their directory.
<!-- /nexy:server -->
<!-- nexy:client -->
`notfound.tsx` and `errors.tsx` (`.jsx`, `.vue` or `.svelte`: the extension of the framework) are
the 404 and 500 pages of their directory.
<!-- /nexy:client -->

Names starting with `_` or `.` are ignored: use them for partials and drafts. Two files that
resolve to the same URL both register: never put `blog.*` next to `blog/index.*`.

<!-- nexy:web -->
Components never live in `src/routes/`, or they become pages.
<!-- /nexy:web -->

## Configuration

Only in `nexyconfig.py`. Never in scattered constants or ad-hoc environment variables.

<!-- nexy:web -->
```python
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()           # vue(), svelte(), solid(), preact()
    useCSR = True
    useAliases = {"@": "src"}
    useVite = True
    useDevTools = True        # the nx dev toolbar
```
<!-- /nexy:web -->

<!-- nexy:api -->
```python
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle = "Orders API"
    useORM = "SQLModel"       # the ORM `nx migrate` migrates
```
<!-- /nexy:api -->

Read `nexy/core/config.py` for every field and its default.

## Commands

```bash
nx dev      # development, one port, hot reload
nx build    # production build; fails on a compile error
nx start    # production server
nx test     # pytest; --client adds vitest
nx check    # mypy and tsc
```

Run them inside the project's virtual environment (`.venv`), or through `uv run`, for example
`uv run nx dev`. `uvx nexy` runs in an environment with no package of the project, so it only
creates a project (`new`, `init`): a command that imports `nexyconfig.py` fails there with
`No module named ...`.

## Rules

- `__nexy__/` is generated. Delete it to force a clean build.
- Put static files in `public/`; `public/logo.svg` is served at `/logo.svg`.
<!-- nexy:web -->
- Only the root layout writes `<html>`, `<head>` and `<body>`.
<!-- /nexy:web -->
<!-- nexy:server -->
- Frontmatter of a `.nexy` file runs on every request: no module-level side effects.
<!-- /nexy:server -->
