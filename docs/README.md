# Nexy documentation

**A Python framework for fullstack web applications.**

Nexy is about the seam between a Python backend and a browser frontend. Instead of two servers, two
build systems and two route tables, you get one origin: FastAPI and Starlette serve the application,
Vite builds the client, and a file under `src/routes/` is a route - `.nexy` is a page, `.py` is an
API handler.

- **Python first.** Pages, endpoints, forms and actions are Python, and a server-rendered page needs
  no frontend framework.
- **Three routers, one integration.** File-based, modular, or an existing FastAPI `APIRouter`.
- **A frontend when you want one.** React, Vue, Svelte, Solid or Preact, per page as islands, or for
  the whole project in client mode.
- **Rendering, one model.** Server rendering, cached pages and islands are decided per page; client
  routing is a project switch.
- **Typed actions.** A form post and a typed client call reach the same Python function.

Start with one file under `src/routes/`, and add structure when the project grows.

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
| [Core concepts](getting-started/core-concepts.md) | Get the mental model: route, page, view, component, handler, endpoint |
| [How Nexy works](getting-started/how-nexy-works.md) | Follow one request from the URL to the file that answers it |
| [Architecture](architecture.md) | Know which layer does what, and what Nexy leaves to your application |
| [Project structure](getting-started/project-structure.md) | Know what every folder and file in a project is for |
| [Choose a router](routing/README.md) | Pick the file-based, modular or custom router |
| [Choose a view format](views/README.md) | Pick `.nexy`, Markdown or a client framework for a page |

### Coming from elsewhere
| Page | What you will do |
|---|---|
| [Coming from another framework](getting-started/coming-from-other-frameworks.md) | Translate FastAPI, Next.js and Express habits into Nexy |

## Routing

### File-based {fbr}
| Page | What you will do |
|---|---|
| [File-based routing](routing/fbr/README.md) | Turn a file path into a URL |
| [Pages](routing/fbr/pages/README.md) | Write a page |
| [Dynamic routes](routing/fbr/pages/dynamic-routes.md) | Use `[slug]`, `[...path]` and route groups |
| [Page metadata](routing/fbr/pages/metadata.md) | Set the title, description and share image of a page {new} |
| [Layouts](routing/fbr/layouts/README.md) | Share a frame between pages |
| [Inheritance](routing/fbr/inheritance.md) | Read the resolution order of layouts, dependencies and error pages |
| [Server mode and client mode](routing/fbr/modes.md) | `useCSR`, and what each mode allows |
| [Linking and navigating](routing/fbr/navigation/linking-and-navigating.md) | Link pages, navigate on the client, prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Read the path, query, cookies and session |

### Handlers and errors {fbr}
| Page | What you will do |
|---|---|
| [Route handlers](routing/fbr/handlers/README.md) | Add a Python endpoint |
| [Validation and errors](routing/fbr/handlers/validation-and-errors.md) | Answer `422` and `404`, and raise an `HTTPException` |
| [WebSocket handlers](routing/fbr/realtime/websocket.md) | Handle a `SOCKET` connection |
| [Dependencies and guards](routing/fbr/dependencies/README.md) | Run `dependencies.py` before a handler, and inherit it |
| [Middleware files](routing/fbr/middleware/README.md) | Wrap requests with `middleware.py`, inherited by directory |
| [Error pages](routing/fbr/errors/README.md) | Answer with `notfound.nexy`, `errors.nexy` and JSON errors |
| [Error pages per folder](routing/fbr/errors/folder-pages.md) | Edge case: errors from sub-folders |

### Modular router {modular}
Controllers and modules.
| Page | What you will do |
|---|---|
| [Modular routing](routing/modular/README.md) | Mount controllers and modules |
| [Dependency injection](routing/modular/dependency-injection.md) | Define services, their scopes and the container |
| [Guards and metadata](routing/modular/guards-and-metadata.md) | Protect and document routes |
| [Modular router vs NestJS](routing/modular/vs-nestjs.md) | Comparison with NestJS |

### Custom router integration {custom}
| Page | What you will do |
|---|---|
| [Custom routing](routing/custom/README.md) | Include an existing FastAPI app |

## Frontend

### Shared contracts
| Page | What it defines |
|---|---|
| [Frontend pages](views/frontend/pages.md) | One file, one route: props, rendering, metadata |
| [Frontend layouts](views/frontend/layouts.md) | The document shell, nesting, and what a layout cannot do |
| [Actions and navigation](views/frontend/actions-and-navigation.md) | Call a typed Action, link pages, read the URL |

### Nexy views
| Page | What you will do |
|---|---|
| [.nexy files](views/nexy/README.md) | Write a page with Python, Jinja2 and props |
| [Components](views/nexy/components.md) | Use `Image`, `Link`, `Audio`, `Video` and `Import` |
| [layout.nexy](views/nexy/layouts.md) | Write the server-mode layout |
| [Markdown and MDX](views/nexy/markdown.md) | Write content pages |

### Framework differences
| Page | What changes |
|---|---|
| [React differences](views/react/differences.md) | Components, hooks and `layout.tsx` {new} |
| [Vue differences](views/vue/differences.md) | SFCs, refs and `layout.vue` {new} |
| [Svelte differences](views/svelte/differences.md) | Runes, stores and `layout.svelte` {new} |
| [Solid differences](views/solid/differences.md) | Signals, accessors and `layout.tsx` {new} |
| [Preact differences](views/preact/differences.md) | Hooks, signals and `layout.tsx` {new} |

## Rendering

### Modes
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

### Security and deployment
| Page | What you will do |
|---|---|
| [Middleware and security](guides/middleware-and-security.md) | Set up CORS, GZip, trusted hosts and sessions |
| [Deploy](deployment/README.md) | Build, containerise and serve |
| [Performance](deployment/performance.md) | Measure and tune the defaults |

### Build and test
| Page | What you will do |
|---|---|
| [Vite and styling](guides/frontend.md) | Set up Vite, styling and the client build |
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

## Layout
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
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
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Advanced

### Advanced {advanced}

| Page | What you will do |
|---|---|
| [Upgrading to 2.2](getting-started/upgrading.md) | Migrate from 2.1 to 2.2 |
| [Internationalization (i18n)](guides/i18n.md) | Add translations with your choice of library |
| [Recipes](guides/recipes.md) | Examples and patterns, not a tutorial |

*These pages are not part of the default reading path. An "All documentation" link allows you to see everything.*
