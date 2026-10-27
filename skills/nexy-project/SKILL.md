---
name: nexy-project
description: Layout of a Nexy project, server mode versus client mode, file conventions under src/routes, config in nexyconfig.py, and the nx commands. Load it before creating, moving or renaming files.
---

# A Nexy project

A route is a file under `src/routes/`. The file path is the URL.

## Choose the mode first

`useCSR` in `nexyconfig.py` decides everything else.

| | Server mode (`useCSR = False`) | Client mode (`useCSR = True`) |
|---|---|---|
| Pages | `.nexy`, `.md`, `.mdx` | `.tsx`, `.vue`, `.svelte` of one framework |
| Document owner | root `layout.nexy` | root `layout.tsx`, `layout.vue` or `layout.svelte` |
| Client components | islands imported from a `.nexy` page | the pages themselves |
| Navigation | full page loads | in the browser, layouts stay mounted |
| Pick it for | content, marketing, SEO-first | dashboards, apps, a Python API with a client app |

Mixing them is rejected before `nx dev`, `nx start` and `nx build` run. One client framework per
project.

## Layout

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

## File conventions in `src/routes/`

| File | Becomes |
|---|---|
| `index.*` | the route of its directory |
| `about.*` | `/about` |
| `[slug].*` | dynamic segment |
| `[...path].*` | catch-all |
| `(group)/page.*` | `/page`; the group is not in the URL |
| `name.py` | API handler; functions `GET`, `POST`, ... are the methods |
| `layout.*` | wraps every page below it; the root one owns the document |
| `notfound.nexy`, `errors.nexy` | 404 and 500 pages of the directory |
| `middleware.py`, `dependencies.py` | applied to the directory and below |

Names starting with `_` or `.` are ignored: use them for partials and drafts. Two files that
resolve to the same URL both register: never put `blog.nexy` next to `blog/index.nexy`.

Components never live in `src/routes/`, or they become pages.

## Configuration

Only in `nexyconfig.py`. Never in scattered constants or ad-hoc environment variables.

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

Read `nexy/core/config.py` for every field and its default.

## Commands

```bash
nx dev      # development, one port, hot reload
nx build    # production build; fails on a compile error
nx start    # production server
nx test     # pytest; --client adds vitest
nx check    # mypy and tsc
```

## Rules

- `__nexy__/` is generated. Delete it to force a clean build.
- Only the root layout writes `<html>`, `<head>` and `<body>`.
- Put static files in `public/`; `public/logo.svg` is served at `/logo.svg`.
- Frontmatter of a `.nexy` file runs on every request: no module-level side effects.
