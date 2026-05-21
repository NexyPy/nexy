# Architecture

## Overview

Nexy is a full-stack Python meta-framework that bridges FastAPI backends with
Vite-powered frontends (React, Vue, Svelte, Solid, Preact). It uses a custom
.nexy component format that mixes Python frontmatter with Jinja2 HTML
templates, compiled at runtime through a Virtual File System (VFS).

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP / HMR WebSocket
┌──────────────────▼──────────────────────────────────┐
│              Uvicorn (FastAPI)                       │
│  ┌─────────────┴──────────────┐                     │
│  │  AppServer                 │                     │
│  │  - Router (FBR / Modular)  │                     │
│  │  - Middleware stack        │                     │
│  │  - VFS import hook        │                     │
│  └─────────────┬──────────────┘                     │
└────────────────┼────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────────┐
    ▼            ▼            ▼                  ▼
┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
│Compiler│ │ Watcher │ │ Frontend │ │ Static files │
│- Parse │ │- FS     │ │- Vite    │ │- public/     │
│- Build │ │  events │ │- SSG     │ │- fonts       │
│- Import│ │- HMR    │ │- Entries │ │              │
└────────┘ └─────────┘ └──────────┘ └──────────────┘
```

## Project structure

```
nexy/
├── cli/                    # Typer CLI (nx, nexy commands)
│   ├── __init__.py         # CLI app entry
│   └── commands/           # dev, start, build, init, new
├── compiler/               # .nexy file compilation pipeline
│   ├── parser/             # scanner -> sanitizer -> template -> validator -> logic
│   └── generator/          # Python code generation from parsed AST
├── core/                   # Core framework models & types
│   ├── config.py           # NexyConfigModel (nexyconfig.py)
│   ├── models.py           # Pydantic models
│   └── types.py            # Type aliases & protocols
├── routers/                # Request routing
│   ├── app.py              # AppServer assembly
│   ├── fbrouter/           # File-based router
│   └── actions/            # Route action handlers
├── frontend/               # Client-side framework integration
│   ├── react.py, vue.py, svelte.py, solid.py, preact.py
│   ├── runtime.ts          # Browser runtime
│   └── vite.ts             # Vite plugin & build pipeline
├── utils/                  # Utilities
│   ├── dev/                # Dev server, watcher, HMR
│   ├── init/               # Project initialization
│   └── server/             # Server config, ports
├── i18n/                   # Internationalization
├── templates/              # Project scaffold templates
└── vfs/                    # Virtual file system
    ├── finder.py           # Module finder (PEP 302)
    └── loader.py           # Module loader (PEP 302)
```

## Data flow

### Request lifecycle

```
HTTP Request
  │
  ▼
Uvicorn -> FastAPI -> AppServer
  │
  ├─ Middleware (CORS, GZip, TrustedHost, Session, Auth)
  │
  └─ Router dispatch
       │
       ├─ FBRouter: route path -> file in src/routes/
       └─ ModularRouter: route path -> controller method
       │
       ▼
  Component compilation (on first request or file change)
       │
       ├─ Scanner: extract frontmatter (---) from .nexy
       ├─ Sanitizer: normalize framework-specific syntax
       ├─ TemplateParser: HTML -> AST -> Jinja2 template
       ├─ LogicParser: frontmatter Python -> Jinja2 context
       └─ Render: Jinja2 template + context -> HTML string
       │
       ▼
  HTML response (SSR) + Vite-injected client assets
```

### Dev mode file watching

```
File change (save)
  │
  ▼
watchdog observer fires event
  │
  ▼
Watcher._normalize() -> strips CWD prefix
Watcher._skip() -> filters .venv/, node_modules/, etc.
  │
  ▼
Watcher.compile() -> runs compiler on changed file(s)
  │
  ▼
on_reload_api() -> sets server.should_exit = True
  │
  ▼
Uvicorn restart loop:
  1. sys.modules cleared (__nexy__.*, nexy.routers.app/fbrouter)
  2. server.run() re-imports everything fresh
  3. VFS always has latest compiled content
```

## Key modules

### Virtual File System (VFS)

The VFS is an in-memory singleton that stores compiled .py and .html files.
It survives across uvicorn restarts within the same process, so compiled
content is always available immediately after re-import.

- `NexyVFSFinder` — PEP 302 module finder, intercepts `__nexy__.*` imports
- `NexyVFSLoader` — loads compiled source from VFS instead of disk
- Registered via `sys.meta_path` at startup

### Compiler pipeline (`nexy/compiler/`)

1. **Scanner** — Parses `---` frontmatter delimiters, extracts Python header
2. **Sanitizer** — Rewrites framework-specific syntax (vue vs react vs nexy)
3. **Template parser** — HTML to AST, validates component references
4. **Logic parser** — Compiles Python frontmatter to Jinja2-compatible expressions
5. **Generator** — Produces `__nexy__/*.py` and `__nexy__/*.html` files in VFS

### Router

Two routing strategies:

- **File-based router (FBR)**: `src/routes/index.nexy` → `/`,
  `src/routes/blog/[slug].nexy` → `/blog/{slug}`. Auto-discovery of routes
  from filesystem, supports layouts via `_layout.nexy` files.

- **Modular router**: Apps with `app_controller.py` + `app_module.py` pattern
  (inspired by NestJS). Decorator-based routing with dependency injection.

### Frontend integration

Each supported framework (React, Vue, Svelte, Solid, Preact) has:

- A Python module in `nexy/frontend/` for framework detection and entry generation
- A TypeScript SSG module in `nexy/frontend/scripts/` for static generation
- esbuild-based per-file SSR builds (no Vite dependency in production)

## Design decisions

| Decision | Rationale |
|----------|-----------|
| VFS instead of disk writes | Avoids filesystem pollution, enables instant re-import |
| uvicorn restart instead of importlib.reload | Module cache cannot be reliably cleared; restart is deterministic |
| esbuild instead of Vite for SSR | Faster per-file builds, no Vite dependency in production |
| Jinja2 for .nexy rendering | Mature, sandboxed, extensible, same engine as Django templates |
| Custom watcher instead of uvicorn --reload | Fine-grained control over what triggers restart, debouncing |
| `sys.modules` clearing before restart | Bypasses Python's import cache for fresh module state |
| Pydantic for config validation | Runtime type safety, IDE autocomplete, schema generation |

## Performance characteristics

- **Startup**: Sub-second (<100ms for compile, <200ms for full server ready)
- **HMR**: Sub-100ms file change to browser refresh
- **SSR**: ~5-15ms per component (esbuild per-file)
- **Static file serving**: FastAPI's StaticFiles (offloaded to Vite in dev)

## Security

- Jinja2 auto-escaping enabled by default (XSS protection)
- CORS middleware configurable via `nexyconfig.py`
- Session middleware with signed cookies
- No arbitrary code execution in templates (Jinja2 sandbox)
- Environment variables for secrets, never hardcoded
