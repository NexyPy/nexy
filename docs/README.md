# Nexy documentation

Nexy is a fullstack Python meta-framework: FastAPI and Starlette serve the app, Vite builds the
client. A route is a file under `src/routes/` - `.nexy` is a page, `.py` is an API handler.

These pages are plain Markdown, written from the code. Start with the task you have, not with the
architecture.

## Getting started

| Page | What you will do |
|---|---|
| [Getting started](getting-started.md) | Create a project, run it, build it |
| [Project structure](project-structure.md) | Know what every folder is for |
| [Routing](routing/README.md) | Turn a file path into a URL |
| [Views](views/README.md) | Choose the format of a page |
| [API](api.md) | Add a Python endpoint |
| [Tutorial](tutorial.md) | Build a page, an endpoint and a production build in 10 minutes |
| [Coming from another framework](comparison.md) | Map FastAPI, Next.js and Express to Nexy |

## Guides

| Page | What you will do |
|---|---|
| [.nexy files](views/nexyfile.md) | Write a page with Python, Jinja2 and props |
| [Markdown and MDX](views/markdown.md) | Write content pages |
| [Components](views/components.md) | Use `Image`, `Link`, `Audio`, `Video`, `Import` |
| [Hooks](routing/hooks.md) | Read the path, query, cookies and session |
| [Pages](routing/pages.md) | Dynamic segments, error pages |
| [Layouts](routing/layouts.md) | The root document and nested layouts |
| [Modular routing](routing/modular.md) | Controllers, modules and injection |
| [SSR](routing/fbr/ssr.md), [CSR](routing/fbr/csr.md), [ISR](routing/fbr/isr.md) | Pick a rendering mode |
| [WebSocket](routing/fbr/websocket.md) | Handle a `SOCKET` connection |
| [Actions](actions.md) | Call a Python function from a form |
| [i18n](i18n.md) | Translate a page |
| [Frontend](frontend.md) | Understand Vite, styling and the client build |
| [Testing](testing.md) | Run pytest, `TestClient` and vitest |
| [Deploy](deploy.md) | Build, containerise and serve |

## Reference

| Page | What it lists |
|---|---|
| [CLI](cli.md) | Commands and flags |
| [Config](config.md) | Every `nexyconfig.py` field and its default |
| [React](views/react.md), [Vue](views/vue.md), [Svelte](views/svelte.md), [Solid](views/solid.md), [Preact](views/preact.md) | Framework setup |

## For agents

[Agents](agents.md) lists the invariants of a Nexy project. Repository-wide agent rules live in the
root [`AGENTS.md`](../AGENTS.md).

## Layout

```text
docs/
├─ README.md               this page
├─ getting-started.md      create a project, run it, build it
├─ tutorial.md             a 10 minute walkthrough
├─ comparison.md           FastAPI, Next.js and Express mapped to Nexy
├─ project-structure.md    files, folders, generated output
├─ frontend.md             Vite, dev server, build, styling
├─ api.md                  Python handlers
├─ actions.md              @Action endpoints called from a page
├─ cli.md                  commands and flags
├─ testing.md              pytest, TestClient, vitest, CI
├─ config.md               nexyconfig.py, field by field
├─ i18n.md                 locales, trans, nx translate
├─ deploy.md               build output, Docker, reverse proxy
├─ agents.md               rules for AI agents
├─ routing/
│  ├─ README.md            file path to URL
│  ├─ pages.md             dynamic segments, error pages
│  ├─ layouts.md           root document, nested layouts
│  ├─ hooks.md             reading the current request from a page
│  ├─ modular.md           controllers, modules, injection
│  └─ fbr/
│     ├─ ssr.md            server rendering (default)
│     ├─ csr.md            client-side rendering
│     ├─ isr.md            stale-while-revalidate
│     └─ websocket.md      SOCKET handlers
└─ views/
   ├─ README.md            which view format to use
   ├─ nexyfile.md          the .nexy format
   ├─ markdown.md          .md and .mdx
   ├─ components.md        Image, Link, Audio, Video, Import
   ├─ react.md             React
   ├─ vue.md               Vue
   ├─ svelte.md            Svelte
   ├─ solid.md             Solid
   └─ preact.md            Preact
```

## How these pages are written

- Plain Markdown, rendered by GitHub. No site generator, no build step, no second repository.
- One question per page. A directory when a feature needs several pages, a file otherwise.
- Every claim is checked against `nexy/`. When a page and the code disagree, the code wins.
- English, like the rest of the repository.

## Elsewhere

- [README](../README.md): what Nexy is, quick start, comparison
- [ARCHITECTURE.md](../ARCHITECTURE.md): internals, request lifecycle, compiler pipeline
- [CONTRIBUTING.md](../CONTRIBUTING.md): working on Nexy itself
- [llms.txt](../llms.txt): entry point for AI agents
