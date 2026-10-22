# Changelog

All notable changes to Nexy are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Changed

- **Package layout**: `nexy/utils/` is now `nexy/helpers/` — a transversal
  layer with zero upward imports (`common`, `fs`, `imports`, `server`).
  All feature code moved under `nexy/modules/` (`cli`, `compiler`, `frontend`,
  `routers`, `runtime`, `i18n`, `builder`). The public facade exported by
  `nexy/__init__.py` is unchanged.
- **CLI scaffolding**: project templates (`web-fbr`, `web-modular`, `api-fbr`,
  `api-modular`, `alembic`, `_shared`) now live inside
  `nexy/modules/cli/templates/`.
- **Dev tooling**: the file watcher and `__pycache__` management moved to
  `nexy/modules/cli/devtools/` (`watcher.py`, `pycache.py`).
- **Scaffolds**: the Counter, Card, and Theme templates were rewritten —
  consistent utility classes across frameworks, explicit state hooks on
  Preact, and a table-of-contents layout for markdown pages.

### Fixed

- **Production SSR for default exports**: the static-site generator looked up
  `<name>.default.html` while the build emits `<name>.Default.html`, so the
  server-rendered payload was silently empty for default-export routes on
  case-sensitive filesystems. The lookup now matches emitted names.
- **SSG pipeline**: React, Preact, and Solid are prerendered through per-file
  esbuild builds with a CPU-bound worker pool instead of Vite, and SSR
  failures now surface the real error in the build warning instead of a
  generic message.

### Added

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
