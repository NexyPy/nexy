# Nexy documentation

Nexy is a fullstack Python meta-framework: FastAPI and Starlette serve the app, Vite builds the
client. A route is a file under `src/routes/` - `.nexy` is a page, `.py` is an API handler.

## What Nexy gives you

- **A page from a file**: `.nexy`, Markdown and MDX routes, layouts, metadata. [Pages](routing/fbr/pages/README.md)
- **A Python API**: FastAPI handlers named after the HTTP method, validation, WebSocket. [Route handlers](routing/fbr/handlers/README.md)
- **A client framework**: React, Vue, Svelte, Solid and Preact, mixed in one project. [Views](views/README.md)
- **Control over rendering**: SSR, ISR, CSR and islands, per page. [Rendering](rendering/README.md)
- **A typed call to Python**: Actions, from a form or from TypeScript. [Actions](guides/actions.md)
- **A structured backend**: Modular router with injection, guards and metadata. [Modular routing](routing/modular/README.md)
- **A product ready for the world**: i18n, sessions, middleware, databases. [Guides](guides/i18n.md)
- **A fast loop**: Dev server, browser error overlay, dev toolbar. [Dev toolbar](guides/devtools.md)
- **A deployable build**: `nx build` and `nx start`, no Node at runtime. [Deploy](deployment/README.md)
- **Help from a coding agent**: Project rules for Claude Code, Codex and OpenCode. [Coding agents](guides/ai-agents.md)

Start with the task you have, not with the architecture. Every page is plain Markdown, written from
the code.

## Where to start

- **I want to see it work**: [Quick start](getting-started/quick-start.md), then the [Tutorial](getting-started/tutorial.md).
- **I am building a feature**: open [Build](#build) and follow the task.
- **I must pick an option**: open [Choose](#choose) (router, rendering mode, client framework).
- **I need an exact name or flag**: open [Reference](#reference).

## Getting started

| Page | What you will do |
|---|---|
| [Installation](getting-started/installation.md) | Requirements, `uvx`, `uv tool install` |
| [Quick start](getting-started/quick-start.md) | Create a project, run it, build it |
| [Tutorial](getting-started/tutorial.md) | A page, an endpoint and a production build in 10 minutes |
| [How Nexy works](getting-started/how-nexy-works.md) | The mental model: who builds what, and one request |
| [Project structure](getting-started/project-structure.md) | Know what every folder is for |
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Map FastAPI, Next.js and Express to Nexy |
| [Upgrading to 2.2](getting-started/upgrading.md) | What changes for an existing project |

## Build

| Page | What you will do |
|---|---|
| [File-based routing](routing/fbr/README.md) | Turn a file path into a URL |
| [Pages](routing/fbr/pages/README.md) | Write a page |
| [Dynamic routes](routing/fbr/pages/dynamic-routes.md) | `[slug]`, `[...path]`, route groups |
| [Page metadata](routing/fbr/pages/metadata.md) | Title, description and share image of a page |
| [Layouts](routing/fbr/layouts/README.md) | Share a frame between pages |
| [Route handlers](routing/fbr/handlers/README.md) | Add a Python endpoint |
| [Validation and errors](routing/fbr/handlers/validation-and-errors.md) | `422`, `404`, `HTTPException` |
| [Actions](guides/actions.md) | Call a Python function from a form or a typed TypeScript function |
| [Linking and navigating](routing/fbr/navigation/linking-and-navigating.md) | `Link`, client navigation, prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Read the path, query, cookies and session |
| [Views](views/README.md) | Choose the format of a page |
| [.nexy files](views/nexyfile.md) | Write a page with Python, Jinja2 and props |
| [Markdown and MDX](views/markdown.md) | Write content pages |
| [Components](views/components.md) | Use `Image`, `Link`, `Audio`, `Video`, `Import` |
| [WebSocket](routing/fbr/realtime/websocket.md) | Handle a `SOCKET` connection |
| [i18n](guides/i18n.md) | Internationalize an application |
| [Databases](guides/databases.md) | ORMs and migrations |
| [Recipes](guides/recipes.md) | Sign in with a session, a JSON API and a file upload, all tested |

## Choose

| Page | What you will decide |
|---|---|
| [Routing](routing/README.md) | The file-based or the modular router |
| [Modular routing](routing/modular/README.md) | Controllers and modules |
| [Rendering](rendering/README.md) | Which rendering mode fits a page |
| [SSR](rendering/ssr.md) | Server rendering, the default |
| [ISR](rendering/isr.md) | Cache pages with stale-while-revalidate |
| [CSR](rendering/csr.md) | Client-side routing |
| [Islands](rendering/islands.md) | Hydrate on idle, visible or media query |
| [Server mode and client mode](routing/fbr/modes.md) | `useCSR`, and what each mode allows |
| [React](views/react.md) | Use React in a page |
| [Vue](views/vue.md) | Use Vue in a page |
| [Svelte](views/svelte.md) | Use Svelte in a page |
| [Solid](views/solid.md) | Use Solid in a page |
| [Preact](views/preact.md) | Use Preact in a page |
| [Nexy and NestJS](routing/modular/vs-nestjs.md) | What matches and what is missing |

## Go deeper

| Page | What you will do |
|---|---|
| [Inheritance](routing/fbr/inheritance.md) | Layouts, dependencies and error pages in one table |
| [layout.nexy](routing/fbr/layouts/layout.nexy.md) | The server-mode layout |
| [layout.tsx](routing/fbr/layouts/layout.tsx.md) | The React client-mode layout that owns `<html>` |
| [layout.vue](routing/fbr/layouts/layout.vue.md), [layout.svelte](routing/fbr/layouts/layout.svelte.md) | Nested layouts for Vue and Svelte |
| [Dependencies and guards](routing/fbr/dependencies/README.md) | `dependencies.py` and its inheritance |
| [Middleware files](routing/fbr/middleware/README.md) | `middleware.py`, inherited by directory |
| [Error pages](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON errors |
| [Error pages per folder](routing/fbr/errors/folder-pages.md) | Answer 404, 500, 403 and 401 from a folder |
| [Dependency injection](routing/modular/dependency-injection.md) | Services, scopes, the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |

## Guides

| Page | What you will do |
|---|---|
| [Middleware and security](guides/middleware-and-security.md) | CORS, GZip, trusted hosts, sessions |
| [Frontend](guides/frontend.md) | Vite, styling and the client build |
| [Testing](guides/testing.md) | pytest, `TestClient` and vitest |
| [Dev toolbar](guides/devtools.md) | The toolbar of `nexy dev`, and how to turn it off |
| [Coding agents](guides/ai-agents.md) | Give Claude Code, Codex and OpenCode the rules of your project |
| [Troubleshooting](guides/troubleshooting.md) | The first problems people hit, and the fix |
| [Deploy](deployment/README.md) | Build, containerise and serve |
| [Performance](deployment/performance.md) | Defaults, measurements and tuning |

## Reference

| Page | What it lists |
|---|---|
| [CLI](reference/cli.md) | Commands and flags |
| [Config](reference/config.md) | Every `nexyconfig.py` field and its default |
| [Python API](reference/python-api.md) | Every name Nexy exports, by module |
| [Exceptions and errors](reference/exceptions.md) | Every failure, its status, and the file that answers it |
| [File conventions](reference/file-conventions.md) | Reserved files and routing rules |
| [Glossary](reference/glossary.md) | The words these docs use |
| [Security](reference/security.md) | Version floors, rules Nexy follows, audits |
| [Agents](reference/agents.md) | Invariants of a Nexy project, for AI agents |

## Layout

```text
docs/
├─ README.md
├─ getting-started/     installation, quick start, tutorial, project structure, migration
├─ routing/
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups
│  │  ├─ layouts/       layout.nexy, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/      WebSocket
│  └─ modular/          controllers, injection, guards, NestJS comparison
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               .nexy, Markdown, components, one page per client framework
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, file conventions, security, agents
```

## How these pages are written

- Plain Markdown, rendered by GitHub. No site generator, no build step, no second repository.
- One question per page. A directory when a feature needs several pages, a file otherwise.
- A page earns its place in this order: what you will be able to do, the rule in one sentence, a
  picture when the feature has moving parts, an example you can run, the details, then the tables.
- Every claim is checked against `nexy/`. When a page and the code disagree, the code wins.
- An image in `docs/assets/` is an illustration: the site draws the SVG inside the page, so it takes
  the colours of the theme, and GitHub shows the file itself.
- Every page ends with the pages that answer the next question.
- English, like the rest of the repository.

## Elsewhere

- [README](../README.md): what Nexy is, quick start, comparison
- [ARCHITECTURE.md](../ARCHITECTURE.md): internals, request lifecycle, compiler pipeline
- [CONTRIBUTING.md](../CONTRIBUTING.md): working on Nexy itself
- [llms.txt](../llms.txt): entry point for AI agents
- [sites/](../sites/README.md): the two websites that show these pages
