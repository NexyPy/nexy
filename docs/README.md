# Nexy documentation

Nexy is a fullstack Python meta-framework: FastAPI and Starlette serve the app, Vite builds the
client. A route is a file under `src/routes/` - `.nexy` is a page, `.py` is an API handler.

## What Nexy gives you

- **A page from a file**: `.nexy`, Markdown and MDX routes, layouts, metadata. [Pages](routing/fbr/pages/README.md)
- **A Python API**: FastAPI handlers named after the HTTP method, validation, WebSocket. [Route handlers](routing/fbr/handlers/README.md)
- **A client framework**: React, Vue, Svelte, Solid or Preact, one per project. [Views](views/README.md)
- **Control over rendering**: SSR, ISR, CSR and islands, per page. [Rendering](rendering/README.md)
- **A typed call to Python**: Actions, from a form or from TypeScript. [Actions](guides/actions.md)
- **A structured backend**: Modular router with injection, guards and metadata. [Modular routing](routing/modular/README.md)
- **A product ready for the world**: i18n, sessions, middleware, databases. [Internationalization](guides/i18n.md)
- **A fast loop**: Dev server, browser error overlay, dev toolbar. [Dev toolbar](guides/devtools.md)
- **A deployable build**: `nx build` and `nx start`, no Node at runtime. [Deploy](deployment/README.md)
- **Help from a coding agent**: Project rules for Claude Code, Codex and OpenCode. [Coding agents](guides/ai-agents.md)

The menu holds every section at once. Pick your router once (file-based, modular or custom): only
the routing pages change with it. Every page states what you will be able to do and ends with the
page that answers the next question.

## Where to start

- **I want to see it work**: [Quick start](getting-started/quick-start.md), then the [Tutorial](getting-started/tutorial.md).
- **I am writing routes**: open [Routing](#routing) for the router you chose.
- **I am writing a view**: open [Views](#views) at your format: `.nexy`, React, Vue, Svelte, Solid or Preact.
- **I need an exact name or flag**: open [Reference](#reference).

## Get started

Install, run, understand.

### First steps

Install, run, build a page.

| Page | What you will do |
|---|---|
| [Installation](getting-started/installation.md) | Install uv and the Nexy CLI, then create your first project |
| [Quick start](getting-started/quick-start.md) | Create a project, run it with live reload, and build it for production |
| [Tutorial](getting-started/tutorial.md) | Build a notes page with an endpoint, shared data and a production build in 10 minutes |

### Understand the model

What Nexy generates, and what to pick.

| Page | What you will do |
|---|---|
| [How Nexy works](getting-started/how-nexy-works.md) | Follow one request from the URL to the file that answers it |
| [Project structure](getting-started/project-structure.md) | Know what every folder and file in a project is for |
| [Choose a router](routing/README.md) | Pick the file-based, modular or custom router |
| [Choose a view format](views/README.md) | Pick `.nexy`, Markdown or a client framework for a page |

### Coming from elsewhere

Translate, or upgrade.

| Page | What you will do |
|---|---|
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Translate FastAPI, Next.js and Express habits into Nexy |
| [Upgrading to 2.2](getting-started/upgrading.md) | Apply the breaking changes from 2.1 to 2.2 |

## Routing

The router you picked: a URL, then the code that answers it.

### Routing

A file path becomes a URL.

| Page | What you will do |
|---|---|
| [File-based routing](routing/fbr/README.md) | Turn a file path into a URL |
| [Pages](routing/fbr/pages/README.md) | Write a page |
| [Dynamic routes](routing/fbr/pages/dynamic-routes.md) | Use `[slug]`, `[...path]` and route groups |
| [Page metadata](routing/fbr/pages/metadata.md) | Set the title, description and share image of a page |
| [Layouts](routing/fbr/layouts/README.md) | Share a frame between pages |
| [Inheritance](routing/fbr/inheritance.md) | Read the resolution order of layouts, dependencies and error pages |
| [Server mode and client mode](routing/fbr/modes.md) | `useCSR`, and what each mode allows |
| [Linking and navigating](routing/fbr/navigation/linking-and-navigating.md) | Link pages, navigate on the client, prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Read the path, query, cookies and session |

### Handle routes

Endpoints, guards and errors.

| Page | What you will do |
|---|---|
| [Route handlers](routing/fbr/handlers/README.md) | Add a Python endpoint |
| [Validation and errors](routing/fbr/handlers/validation-and-errors.md) | Answer `422` and `404`, and raise an `HTTPException` |
| [WebSocket handlers](routing/fbr/realtime/websocket.md) | Handle a `SOCKET` connection |
| [Dependencies and guards](routing/fbr/dependencies/README.md) | Run `dependencies.py` before a handler, and inherit it |
| [Middleware files](routing/fbr/middleware/README.md) | Wrap requests with `middleware.py`, inherited by directory |
| [Error pages](routing/fbr/errors/README.md) | Answer with `notfound.nexy`, `errors.nexy` and JSON errors |
| [Error pages per folder](routing/fbr/errors/folder-pages.md) | Answer 404, 500, 403 and 401 from a folder |

### Modular router

Controllers and modules.

| Page | What you will do |
|---|---|
| [Modular routing](routing/modular/README.md) | Mount controllers and modules |
| [Nexy and NestJS](routing/modular/vs-nestjs.md) | See what matches NestJS and what is missing |

### Services and guards

Injection and protection.

| Page | What you will do |
|---|---|
| [Dependency injection](routing/modular/dependency-injection.md) | Define services, their scopes and the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |

### Custom router

Your own router.

| Page | What you will do |
|---|---|
| [Custom routing](routing/custom/README.md) | Include an existing FastAPI app |

## Views

What a page is written in.

### Nexy views

Python, Jinja2 and Markdown.

| Page | What you will do |
|---|---|
| [.nexy files](views/nexy/README.md) | Write a page with Python, Jinja2 and props |
| [Components](views/nexy/components.md) | Use `Image`, `Link`, `Audio`, `Video` and `Import` |
| [layout.nexy](views/nexy/layouts.md) | Write the server-mode layout |
| [Markdown and MDX](views/nexy/markdown.md) | Write content pages |

### React

Pages, layouts and islands in React.

| Page | What you will do |
|---|---|
| [React](views/react/README.md) | Enable React and pick server or client mode |
| [Pages](views/react/pages.md) | Write a `.tsx` page, read its params, know when it renders |
| [Layouts](views/react/layouts.md) | Write the `layout.tsx` that owns `<html>` |
| [Islands](views/react/islands.md) | Put a React component in a `.nexy` page |
| [Actions and navigation](views/react/actions-and-navigation.md) | Call Python, link pages, read the URL |

### Vue

Pages, layouts and islands in Vue.

| Page | What you will do |
|---|---|
| [Vue](views/vue/README.md) | Enable Vue and pick server or client mode |
| [Pages](views/vue/pages.md) | Write a `.vue` page, read its params, know when it renders |
| [Layouts](views/vue/layouts.md) | Write the `layout.vue` that owns `<html>` |
| [Islands](views/vue/islands.md) | Put a Vue component in a `.nexy` page |
| [Actions and navigation](views/vue/actions-and-navigation.md) | Call Python, link pages, read the URL |

### Svelte

Pages, layouts and islands in Svelte.

| Page | What you will do |
|---|---|
| [Svelte](views/svelte/README.md) | Enable Svelte and pick server or client mode |
| [Pages](views/svelte/pages.md) | Write a `.svelte` page, read its params, know when it renders |
| [Layouts](views/svelte/layouts.md) | Write the `layout.svelte` that owns `<html>` |
| [Islands](views/svelte/islands.md) | Put a Svelte component in a `.nexy` page |
| [Actions and navigation](views/svelte/actions-and-navigation.md) | Call Python, link pages, read the URL |

### Solid

Pages, layouts and islands in Solid.

| Page | What you will do |
|---|---|
| [Solid](views/solid/README.md) | Enable Solid and pick server or client mode |
| [Pages](views/solid/pages.md) | Write a `.tsx` page, read its params, know when it renders |
| [Layouts](views/solid/layouts.md) | Write the `layout.tsx` that owns `<html>` |
| [Islands](views/solid/islands.md) | Put a Solid component in a `.nexy` page |
| [Actions and navigation](views/solid/actions-and-navigation.md) | Call Python, link pages, read the URL |

### Preact

Pages and islands in Preact.

| Page | What you will do |
|---|---|
| [Preact](views/preact.md) | Use Preact in a page |

## Rendering and data

When a page renders, and where its data comes from.

### Rendering

When pages are rendered.

| Page | What you will decide |
|---|---|
| [Rendering](rendering/README.md) | Which rendering mode fits a page |
| [SSR](rendering/ssr.md) | Server rendering, the default |
| [ISR](rendering/isr.md) | Cache pages with stale-while-revalidate |
| [CSR](rendering/csr.md) | Client-side routing |
| [Islands](rendering/islands.md) | Hydrate on idle, visible or media query |

### Forms and data

Actions, databases, translations.

| Page | What you will do |
|---|---|
| [Actions](guides/actions.md) | Call a Python function from a form or a typed TypeScript function |
| [Databases](guides/databases.md) | Choose an ORM and run migrations |
| [Internationalization (i18n)](guides/i18n.md) | Add translations with the library of your choice |
| [Recipes](guides/recipes.md) | Sign in with a session, build a JSON API and upload a file, all tested |

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
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/      WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
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
