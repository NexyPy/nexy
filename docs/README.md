# Nexy documentation

Nexy is a fullstack Python meta-framework: FastAPI and Starlette serve the app, Vite builds the
client. A route is a file under `src/routes/` - `.nexy` is a page, `.py` is an API handler.

These pages are plain Markdown, written from the code. Start with the task you have, not with the
architecture.

## Getting started

| Page | What you will do |
|---|---|
| [Installation](getting-started/installation.md) | Requirements, `uvx`, `uv tool install` |
| [Quick start](getting-started/quick-start.md) | Create a project, run it, build it |
| [Tutorial](getting-started/tutorial.md) | A page, an endpoint and a production build in 10 minutes |
| [Project structure](getting-started/project-structure.md) | Know what every folder is for |
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Map FastAPI, Next.js and Express to Nexy |

## Routing

| Page | What you will do |
|---|---|
| [Routing](routing/README.md) | Choose between the file-based and the modular router |
| [File-based routing](routing/fbr/README.md) | Turn a file path into a URL |
| [Server mode and client mode](routing/fbr/modes.md) | `useCSR`, and what each mode allows |
| [Pages](routing/fbr/pages/README.md) | Write a page |
| [Dynamic routes](routing/fbr/pages/dynamic-routes.md) | `[slug]`, `[...path]`, route groups |
| [Layouts](routing/fbr/layouts/README.md) | Root and nested layouts |
| [layout.nexy](routing/fbr/layouts/layout.nexy.md) | The server-mode layout |
| [layout.tsx](routing/fbr/layouts/layout.tsx.md) | The React client-mode layout that owns `<html>` |
| [layout.vue](routing/fbr/layouts/layout.vue.md), [layout.svelte](routing/fbr/layouts/layout.svelte.md) | Nested layouts for Vue and Svelte |
| [Route handlers](routing/fbr/handlers/README.md) | Add a Python endpoint |
| [Validation and errors](routing/fbr/handlers/validation-and-errors.md) | `422`, `404`, `HTTPException` |
| [Dependencies and guards](routing/fbr/dependencies/README.md) | `dependencies.py` and its inheritance |
| [Middleware files](routing/fbr/middleware/README.md) | `middleware.py`, inherited by directory |
| [Inheritance](routing/fbr/inheritance.md) | Layouts, dependencies and error pages in one table |
| [Error pages](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON errors |
| [Linking and navigating](routing/fbr/navigation/linking-and-navigating.md) | `Link`, client navigation, prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Read the path, query, cookies and session |
| [WebSocket](routing/fbr/realtime/websocket.md) | Handle a `SOCKET` connection |
| [Modular routing](routing/modular/README.md) | Controllers and modules |
| [Dependency injection](routing/modular/dependency-injection.md) | Services, scopes, the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |
| [Nexy and NestJS](routing/modular/vs-nestjs.md) | What matches and what is missing |

## Rendering

| Page | What you will do |
|---|---|
| [Rendering](rendering/README.md) | Pick a rendering mode |
| [SSR](rendering/ssr.md) | Server rendering, the default |
| [ISR](rendering/isr.md) | Cache pages with stale-while-revalidate |
| [CSR](rendering/csr.md) | Client-side routing |
| [Islands](rendering/islands.md) | Hydrate on idle, visible or media query |

## Views

| Page | What you will do |
|---|---|
| [Views](views/README.md) | Choose the format of a page |
| [.nexy files](views/nexyfile.md) | Write a page with Python, Jinja2 and props |
| [Markdown and MDX](views/markdown.md) | Write content pages |
| [Components](views/components.md) | Use `Image`, `Link`, `Audio`, `Video`, `Import` |
| [React](views/react.md), [Vue](views/vue.md), [Svelte](views/svelte.md), [Solid](views/solid.md), [Preact](views/preact.md) | Framework setup |

## Guides

| Page | What you will do |
|---|---|
| [Actions](guides/actions.md) | Call a Python function from a form or a typed TypeScript function |
| [i18n](guides/i18n.md) | Internationalize an application |
| [Databases](guides/databases.md) | ORMs and migrations |
| [Middleware and security](guides/middleware-and-security.md) | CORS, GZip, trusted hosts, sessions |
| [Frontend](guides/frontend.md) | Vite, styling and the client build |
| [Testing](guides/testing.md) | pytest, `TestClient` and vitest |
| [Dev toolbar](guides/devtools.md) | the toolbar of `nexy dev`, and how to turn it off |
| [Coding agents](guides/ai-agents.md) | Give Claude Code, Codex and OpenCode the rules of your project |

## Deployment

| Page | What you will do |
|---|---|
| [Deploy](deployment/README.md) | Build, containerise and serve |
| [Performance](deployment/performance.md) | Defaults, measurements and tuning |

## Reference

| Page | What it lists |
|---|---|
| [CLI](reference/cli.md) | Commands and flags |
| [Config](reference/config.md) | Every `nexyconfig.py` field and its default |
| [File conventions](reference/file-conventions.md) | Reserved files and routing rules |
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
- Every claim is checked against `nexy/`. When a page and the code disagree, the code wins.
- English, like the rest of the repository.

## Elsewhere

- [README](../README.md): what Nexy is, quick start, comparison
- [ARCHITECTURE.md](../ARCHITECTURE.md): internals, request lifecycle, compiler pipeline
- [CONTRIBUTING.md](../CONTRIBUTING.md): working on Nexy itself
- [llms.txt](../llms.txt): entry point for AI agents
