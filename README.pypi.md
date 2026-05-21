# Nexy

Nexy is a full-stack Python meta-framework that bridges FastAPI backends with Vite-powered frontends (React, Vue, Svelte, Solid, Preact). Sub-second startup, sub-100ms HMR.

## Quick start

```bash
uvx nexy new
cd my-project
nexy dev
```

No pip install needed. `uvx` runs Nexy directly — your project gets its own isolated environment.

## The .nexy format

One file. Python logic, Jinja2 template, optional interactive islands.

```html
---
title : prop[str] = "Dashboard"
from "@/components/Chart.tsx" import Chart
---

<h1>{{ title }}</h1>
<Chart data="{{ api_data }}" />
```

- **`---` blocks**: Python — props, imports, logic
- **Body**: Jinja2 — server-rendered HTML
- **`<script>`**: JavaScript/TypeScript — client interactivity via Vite

## Routing

| Pattern | URL |
|---------|-----|
| `index.nexy` | `/` |
| `about.mdx` | `/about` |
| `blog/[slug].nexy` | `/blog/:slug` |
| `api/users.py` | `/api/users` |

File-based for small projects, module-based (NestJS-style) for enterprise.

## Supported frontends

React, Vue, Svelte, Solid, Preact — or none for vanilla SSR.

## CLI

| Command | What it does |
|---------|-------------|
| `nexy new` | Scaffold a project |
| `nexy dev` | Dev server + HMR |
| `nexy build` | Production build (SSR + SSG) |
| `nexy start` | Production server |

## License

MIT
