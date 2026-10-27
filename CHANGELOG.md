# Changelog

All notable changes to Nexy are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

## [2.2.0] - 2026-10-27

### Removed

- **The "Built with Nexy" badge** and its `useBadge` setting. The development toolbar stays
  (`useDevTools`). A `useBadge` line left in a `nexyconfig.py` is ignored.

### Changed

- **MDX is compiled by Vite only.** The Python compiler no longer parses or renders `.mdx` through
  the `.nexy` pipeline: it writes the thin wrapper that serves the route, like for `.tsx`, `.vue`
  and `.svelte`. `nx check` no longer compiles `.mdx` files.
- **The React starter** (client-routed, Tailwind or UnoCSS) has a new design written with utility
  classes and idiomatic React: a home page that confirms the app is running and lists the first
  three steps, an About page, and reusable components (`Button`, `Frame`, `Header`, `Footer`,
  `ThemeToggle` and more). The theme switch is a hook with state instead of a global script. The
  other frameworks and plain CSS keep their current starter for now.
- **The development toolbar** follows the page: white in a light theme, dark in a dark theme. Its
  close control is an icon, and the Routes tab lists the routes again.
- **Package layout**: `nexy/utils/` is now `nexy/helpers/` - a transversal
  layer with zero upward imports (`common`, `fs`, `imports`, `server`).
  All feature code moved under `nexy/modules/` (`cli`, `compiler`, `frontend`,
  `routers`, `runtime`, `i18n`, `builder`). The public facade exported by
  `nexy/__init__.py` is unchanged.
- **CLI scaffolding**: project templates (`web-fbr`, `web-modular`, `api-fbr`,
  `api-modular`, `alembic`, `_shared`) now live inside
  `nexy/modules/cli/templates/`.
- **Dev tooling**: the file watcher and `__pycache__` management moved to
  `nexy/modules/cli/devtools/` (`watcher.py`, `pycache.py`).
- **Scaffolds**: the Counter, Card, and Theme templates were rewritten -
  consistent utility classes across frameworks, explicit state hooks on
  Preact, and a table-of-contents layout for markdown pages.

### Fixed

- **`nx dev` no longer stops on a server error.** When uvicorn cannot start or crashes, dev
  reports the reason, keeps Vite and the watcher running, and starts again at the next file
  change. Only Ctrl+C stops it.
- **The development toolbar's Routes tab** printed `[object HTMLDivElement]` instead of the list.
- **Production SSR for default exports**: the static-site generator looked up
  `<name>.default.html` while the build emits `<name>.Default.html`, so the
  server-rendered payload was silently empty for default-export routes on
  case-sensitive filesystems. The lookup now matches emitted names.
- **SSG pipeline**: React, Preact, and Solid are prerendered through per-file
  esbuild builds with a CPU-bound worker pool instead of Vite, and SSR
  failures now surface the real error in the build warning instead of a
  generic message.

### Added

- **Skills for coding agents** in `skills/`: principles (order of work, KISS, SOLID, TDD, one
  function one treatment, no emoji, real SVG icons, human text), a UX and information-architecture
  audit to run before any view, and one skill each for `.nexy`, Markdown and MDX, React, Preact,
  Solid, Vue, Svelte, styling, the backend, testing and work on the framework itself. An
  `AGENTS.md` snippet carries the rules to OpenCode and Codex.
- Compiler regression suites: byte-level route compile matrix (8 route
  kinds), compiler dispatch contract, markdown route compiler tests, and the
  frontend `useFF` contract tests backed by `vite_entry.normalize_ff`.

### Removed

- Dead code: the unused `BaseFrontendGenerator` abstraction, the unused
  `helpers/common/constants.py`, empty stub modules, and the `Task()`/`Job()`
  decorator stubs. Contract tests lost with the dead abstraction were ported
  to the production code they verify.

## [2.1.1] and earlier

See [GitHub releases](https://github.com/NexyPy/nexy/releases) for the
release history of versions 2.1.1 and earlier.
