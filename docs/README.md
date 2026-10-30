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
- **A product ready for the world**: i18n, sessions, middleware, databases. [Internationalization](guides/i18n.md)
- **A fast loop**: Dev server, browser error overlay, dev toolbar. [Dev toolbar](guides/devtools.md)
- **A deployable build**: `nx build` and `nx start`, no Node at runtime. [Deploy](deployment/README.md)
- **Help from a coding agent**: Project rules for Claude Code, Codex and OpenCode. [Coding agents](guides/ai-agents.md)

The docs follow one path. Start with a running page, learn the model behind it, build the features
you need, then look up exact names when you need them. Every page states what you will be able to do
and ends with the page that answers the next question.

## Where to start

- **I want to see it work**: [Quick start](getting-started/quick-start.md), then the [Tutorial](getting-started/tutorial.md).
- **I am building a feature**: open [Build](#build) and follow the task.
- **I must pick an option**: open [Choose your stack](#choose-your-stack) (router, rendering mode, client framework).
- **I need an exact name or flag**: open [Reference](#reference).

## Start here

Install, then run a page.

### First steps

Install, run, build a page.

| Page | What you will do |
|---|---|
| [Installation](getting-started/installation.md) | Install uv and the Nexy CLI, then create your first project |
| [Quick start](getting-started/quick-start.md) | Create a project, run it with live reload, and build it for production |
| [Tutorial](getting-started/tutorial.md) | Build a notes page with an endpoint, shared data and a production build in 10 minutes |

### Understand the model

What Nexy generates.

| Page | What you will do |
|---|---|
| [How Nexy works](getting-started/how-nexy-works.md) | Follow one request from the URL to the file that answers it |
| [Project structure](getting-started/project-structure.md) | Know what every folder and file in a project is for |

### Coming from elsewhere

Translate, or upgrade.

| Page | What you will do |
|---|---|
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Translate FastAPI, Next.js and Express habits into Nexy |
| [Upgrading to 2.2](getting-started/upgrading.md) | Apply the breaking changes from 2.1 to 2.2 |

## Build

Routes, forms and data.

### Routing

A path becomes a URL.

| Page | What you will do |
|---|---|
| [File-based routing](routing/fbr/README.md) | Turn a file path into a URL |
| [Pages](routing/fbr/pages/README.md) | Write a page |
| [Dynamic routes](routing/fbr/pages/dynamic-routes.md) | Use `[slug]`, `[...path]` and route groups |
| [Page metadata](routing/fbr/pages/metadata.md) | Set the title, description and share image of a page |

### Layouts

Share a layout.

| Page | What you will do |
|---|---|
| [Layouts](routing/fbr/layouts/README.md) | Share a frame between pages |

### API endpoints

Endpoints and status codes.

| Page | What you will do |
|---|---|
| [Route handlers](routing/fbr/handlers/README.md) | Add a Python endpoint |
| [Validation and errors](routing/fbr/handlers/validation-and-errors.md) | Answer `422` and `404`, and raise an `HTTPException` |

### Forms and actions

Call Python from a form.

| Page | What you will do |
|---|---|
| [Actions](guides/actions.md) | Call a Python function from a form or a typed TypeScript function |

### Navigation

Links and prefetch.

| Page | What you will do |
|---|---|
| [Linking and navigating](routing/fbr/navigation/linking-and-navigating.md) | Link pages, navigate on the client, prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Read the path, query, cookies and session |

### Views and content

Python, Markdown, components.

| Page | What you will do |
|---|---|
| [Views](views/README.md) | Choose the format of a page |
| [.nexy files](views/nexyfile.md) | Write a page with Python, Jinja2 and props |
| [Markdown and MDX](views/markdown.md) | Write content pages |
| [Components](views/components.md) | Use `Image`, `Link`, `Audio`, `Video` and `Import` |

### Data and realtime

Databases, sockets, recipes.

| Page | What you will do |
|---|---|
| [WebSocket handlers](routing/fbr/realtime/websocket.md) | Handle a `SOCKET` connection |
| [Internationalization (i18n)](guides/i18n.md) | Add translations with the library of your choice |
| [Databases](guides/databases.md) | Choose an ORM and run migrations |
| [Recipes](guides/recipes.md) | Sign in with a session, build a JSON API and upload a file, all tested |

## Choose your stack

Router, render, framework.

### Router comparison

Compare the three routers.

| Page | What you will decide |
|---|---|
| [Routing](routing/README.md) | The file-based, modular or custom router |

### Rendering

When pages are rendered.

| Page | What you will decide |
|---|---|
| [Rendering](rendering/README.md) | Which rendering mode fits a page |
| [SSR](rendering/ssr.md) | Server rendering, the default |
| [ISR](rendering/isr.md) | Cache pages with stale-while-revalidate |
| [CSR](rendering/csr.md) | Client-side routing |
| [Islands](rendering/islands.md) | Hydrate on idle, visible or media query |
| [Server mode and client mode](routing/fbr/modes.md) | `useCSR`, and what each mode allows |

### Client framework

React, Vue, Svelte and more.

| Page | What you will decide |
|---|---|
| [React](views/react.md) | Use React in a page |
| [Vue](views/vue.md) | Use Vue in a page |
| [Svelte](views/svelte.md) | Use Svelte in a page |
| [Solid](views/solid.md) | Use Solid in a page |
| [Preact](views/preact.md) | Use Preact in a page |

## Advanced

Layouts, guards, router.

### Resolution and layouts

Which layout answers.

| Page | What you will do |
|---|---|
| [Inheritance](routing/fbr/inheritance.md) | Read the resolution order of layouts, dependencies and error pages |
| [layout.nexy](routing/fbr/layouts/layout.nexy.md) | Write the server-mode layout |
| [layout.tsx](routing/fbr/layouts/layout.tsx.md) | Write the React client-mode layout that owns `<html>` |
| [layout.vue](routing/fbr/layouts/layout.vue.md) | Write nested layouts for Vue |
| [layout.svelte](routing/fbr/layouts/layout.svelte.md) | Write nested layouts for Svelte |

### Guards and errors

Protect routes, handle errors.

| Page | What you will do |
|---|---|
| [Dependencies and guards](routing/fbr/dependencies/README.md) | Run `dependencies.py` before a handler, and inherit it |
| [Middleware files](routing/fbr/middleware/README.md) | Wrap requests with `middleware.py`, inherited by directory |
| [Error pages](routing/fbr/errors/README.md) | Answer with `notfound.nexy`, `errors.nexy` and JSON errors |
| [Error pages per folder](routing/fbr/errors/folder-pages.md) | Answer 404, 500, 403 and 401 from a folder |

### Modular router

Controllers and services.

| Page | What you will do |
|---|---|
| [Modular routing](routing/modular/README.md) | Mount controllers and modules |
| [Dependency injection](routing/modular/dependency-injection.md) | Define services, their scopes and the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |
| [Nexy and NestJS](routing/modular/vs-nestjs.md) | See what matches NestJS and what is missing |

### Custom router

Mount a FastAPI app.

| Page | What you will do |
|---|---|
| [Custom routing](routing/custom/README.md) | Include an existing FastAPI app |

## Guides

How-tos across features.

### Security and deployment

Harden, deploy, measure.

| Page | What you will do |
|---|---|
| [Middleware and security](guides/middleware-and-security.md) | Set up CORS, GZip, trusted hosts and sessions |
| [Deploy](deployment/README.md) | Build, containerise and serve |
| [Performance](deployment/performance.md) | Measure and tune the defaults |

### Frontend and testing

Build, style and test.

| Page | What you will do |
|---|---|
| [Frontend](guides/frontend.md) | Set up Vite, styling and the client build |
| [Testing](guides/testing.md) | Test with pytest, `TestClient` and vitest |

### Tooling and help

Toolbar and troubleshooting.

| Page | What you will do |
|---|---|
| [Dev toolbar](guides/devtools.md) | Use the toolbar of `nexy dev`, and turn it off |
| [Coding agents](guides/ai-agents.md) | Give Claude Code, Codex and OpenCode the rules of your project |
| [Troubleshooting](guides/troubleshooting.md) | Fix the first problems people hit |

## Reference

Names, flags, defaults.

### Commands and config

Commands and config.

| Page | What it lists |
|---|---|
| [CLI](reference/cli.md) | Commands, flags, prompts and exit codes |
| [Config](reference/config.md) | Every `nexyconfig.py` field and its default |

### Python API and errors

Exported names and errors.

| Page | What it lists |
|---|---|
| [Python API](reference/python-api.md) | Every name Nexy exports, by module |
| [Exceptions and errors](reference/exceptions.md) | Every failure, its status, and the file that answers it |

### Conventions and concepts

Reserved files and words.

| Page | What it lists |
|---|---|
| [File conventions](reference/file-conventions.md) | Reserved files and routing rules |
| [Glossary](reference/glossary.md) | The words these docs use |
| [Security](reference/security.md) | Version floors, rules Nexy follows, audits |
| [For AI agents](reference/agents.md) | Invariants of a Nexy project, for AI agents |

## Layout

```text
docs/
├─ README.md
├─ getting-started/     installation, quick start, tutorial, project structure, migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout.nexy, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/      WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               .nexy, Markdown, components, one page per client framework
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
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
