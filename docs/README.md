# Nexy documentation

Nexy is a fullstack Python meta-framework: FastAPI and Starlette serve the app, Vite builds the
client. A route is a file under `src/routes/` - `.nexy` is a page, `.py` is an API handler.

## Getting Started

### First steps
| Page | What you will do |
|---|---|
| [Installation](getting-started/installation.md) | Install uv and the Nexy CLI, then create your first project |
| [Quick start](getting-started/quick-start.md) | Create a project, run it with live reload, and build it for production |
| [Tutorial](getting-started/tutorial.md) | Build a notes page with an endpoint, shared data and a production build in 10 minutes |

### Understand the model
| Page | What you will do |
|---|---|
| [How Nexy works](getting-started/how-nexy-works.md) | Follow one request from the URL to the file that answers it |
| [Project structure](getting-started/project-structure.md) | Know what every folder and file in a project is for |
| [Choose a router](routing/README.md) | Pick the file-based, modular or custom router |
| [Choose a view format](views/README.md) | Pick `.nexy`, Markdown or a client framework for a page |

### Coming from elsewhere
| Page | What you will do |
|---|---|
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Translate FastAPI, Next.js and Express habits into Nexy |
| [Upgrading to 2.2](getting-started/upgrading.md) | Apply the breaking changes from 2.1 to 2.2 |

## Routing

### Routing
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

### Route handlers
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
| [Dependency injection](routing/modular/dependency-injection.md) | Define services, their scopes and the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |

### Custom router
Your own router.
| Page | What you will do |
|---|---|
| [Custom routing](routing/custom/README.md) | Include an existing FastAPI app |

## React

### React
| Page | What you will do |
|---|---|
| [React](views/react/README.md) | Enable React and pick server or client mode |
| [Pages](views/react/pages.md) | Write a `.tsx` page, read its params, know when it renders |
| [Layouts](views/react/layouts.md) | Write the `layout.tsx` that owns `<html>` |
| [Islands](views/react/islands.md) | Put a React component in a `.nexy` page |
| [Actions and navigation](views/react/actions-and-navigation.md) | Call Python, link pages, read the URL |

## Vue

### Vue
| Page | What you will do |
|---|---|
| [Vue](views/vue/README.md) | Enable Vue and pick server or client mode |
| [Pages](views/vue/pages.md) | Write a `.vue` page, read its params, know when it renders |
| [Layouts](views/vue/layouts.md) | Write the `layout.vue` that owns `<html>` |
| [Islands](views/vue/islands.md) | Put a Vue component in a `.nexy` page |
| [Actions and navigation](views/vue/actions-and-navigation.md) | Call Python, link pages, read the URL |

## Svelte

### Svelte
| Page | What you will do |
|---|---|
| [Svelte](views/svelte/README.md) | Enable Svelte and pick server or client mode |
| [Pages](views/svelte/pages.md) | Write a `.svelte` page, read its params, know when it renders |
| [Layouts](views/svelte/layouts.md) | Write the `layout.svelte` that owns `<html>` |
| [Islands](views/svelte/islands.md) | Put a Svelte component in a `.nexy` page |
| [Actions and navigation](views/svelte/actions-and-navigation.md) | Call Python, link pages, read the URL |

## Solid

### Solid
| Page | What you will do |
|---|---|
| [Solid](views/solid/README.md) | Enable Solid and pick server or client mode |
| [Pages](views/solid/pages.md) | Write a `.tsx` page, read its params, know when it renders |
| [Layouts](views/solid/layouts.md) | Write the `layout.tsx` that owns `<html>` |
| [Islands](views/solid/islands.md) | Put a Solid component in a `.nexy` page |
| [Actions and navigation](views/solid/actions-and-navigation.md) | Call Python, link pages, read the URL |

## Preact

### Preact
| Page | What you will do |
|---|---|
| [Preact](views/preact/README.md) | Enable Preact and pick server or client mode |
| [Pages](views/preact/pages.md) | Write a `.tsx` page, read its params, know when it renders |
| [Layouts](views/preact/layouts.md) | Write the `layout.tsx` that owns `<html>` |
| [Islands](views/preact/islands.md) | Put a Preact component in a `.nexy` page |
| [Actions and navigation](views/preact/actions-and-navigation.md) | Call Python, link pages, read the URL |

## Nexy Views

### Nexy views
| Page | What you will do |
|---|---|
| [.nexy files](views/nexy/README.md) | Write a page with Python, Jinja2 and props |
| [Components](views/nexy/components.md) | Use `Image`, `Link`, `Audio`, `Video` and `Import` |
| [layout.nexy](views/nexy/layouts.md) | Write the server-mode layout |
| [Markdown and MDX](views/nexy/markdown.md) | Write content pages |

## Rendering

### Rendering
| Page | What you will decide |
|---|---|
| [Rendering](rendering/README.md) | Which rendering mode fits a page |
| [SSR](rendering/ssr.md) | Server rendering, the default |
| [ISR](rendering/isr.md) | Cache pages with stale-while-revalidate |
| [CSR](rendering/csr.md) | Client-side routing |
| [Islands](rendering/islands.md) | Hydrate on idle, visible or media query |

## Guides

### Forms and data
| Page | What you will do |
|---|---|
| [Actions](guides/actions.md) | Call a Python function from a form or a typed TypeScript function |
| [Databases](guides/databases.md) | Choose an ORM and run migrations |
| [Internationalization (i18n)](guides/i18n.md) | Add translations with the library of your choice |
| [Recipes](guides/recipes.md) | Sign in with a session, build a JSON API and upload a file, all tested |

### Security and deployment
| Page | What you will do |
|---|---|
| [Middleware and security](guides/middleware-and-security.md) | Set up CORS, GZip, trusted hosts and sessions |
| [Deploy](deployment/README.md) | Build, containerise and serve |
| [Performance](deployment/performance.md) | Measure and tune the defaults |

### Frontend and testing
| Page | What you will do |
|---|---|
| [Frontend](guides/frontend.md) | Set up Vite, styling and the client build |
| [Testing](guides/testing.md) | Test with pytest, `TestClient` and vitest |

### Tooling and help
| Page | What you will do |
|---|---|
| [Dev toolbar](guides/devtools.md) | Use the toolbar of `nexy dev`, and turn it off |
| [Coding agents](guides/ai-agents.md) | Give Claude Code, Codex and OpenCode the rules of your project |
| [Troubleshooting](guides/troubleshooting.md) | Fix the first problems people hit |

## Reference

### Commands and config
| Page | What it lists |
|---|---|
| [CLI](reference/cli.md) | Commands, flags, prompts and exit codes |
| [Config](reference/config.md) | Every `nexyconfig.py` field and its default |

### Python API and errors
| Page | What it lists |
|---|---|
| [Python API](reference/python-api.md) | Every name Nexy exports, by module |
| [Exceptions and errors](reference/exceptions.md) | Every failure, its status, and the file that answers it |

### Conventions and concepts
| Page | What you will do |
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
│  │  └─ realtime/    WebSocket
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
