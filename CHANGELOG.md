# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Community standard files: CODE_OF_CONDUCT.md, SECURITY.md, ARCHITECTURE.md
- Issue templates and pull request template (.github/)
- FUNDING.yml for GitHub Sponsors integration
- LICENSE file (MIT) at repository root
- git-cliff configuration (cliff.toml) for automated changelog generation
- Generated README.md in scaffolded projects

### Fixed

- Module cache stale data: sys.modules is now cleared before uvicorn restart
- `_normalize` strips CWD prefix from absolute paths for correct module matching
- theme.jinja2: added missing `active = 'system'` to frontmatter

### Changed

- Watcher simplified: direct compile + restart loop, removed importlib.reload
- Dev server restart loop: uvicorn.Server.should_exit pattern with os._exit fallback
- pyproject.toml templates: dynamic project name and description via Jinja2
- ORM choices in `nx n`: "None" is now last in the list
- Uvicorn shutdown/HMR messages filtered from terminal output
- Template projects use `lang="{{ locale }}"` instead of hardcoded `lang="fr"`
- Venv activation command is now platform-aware (shows only the relevant command)

## [2.0.9] - 2026-05-21

### Added

- Header and footer components with theme toggle
- Parallel SSG builds using esbuild worker pool
- Middleware support: CORS, GZip, TrustedHost, Session, Authentication
- Scoped injectable decorator and request scope clearing
- Modular and FBR templates for user management

### Fixed

- Theme management and styling inconsistencies

### Changed

- SSG builds now use per-file esbuild (no Vite dependency for SSR)
- Controller registration uses path-based tags

## [2.0.8] - 2026-05-20

### Added

- Server-side hooks implementation
- Dev server status bar with structured timing output
- Batch SSR builds for Preact, React, and Solid
- SSL support and performance metrics

### Fixed

- Error handling for SSR failures (real error messages in catch blocks)
- Theme button styling for "none" client framework

### Changed

- Browser error overlay for compilation failures
- Clean terminal output (no emojis, structured timings)

## [2.0.7] - 2026-05-18

### Added

- Theme switcher component (light, dark, system modes)
- Comprehensive root-level documentation (README, CONTRIBUTING)

### Changed

- Enhanced project initialization with auto dependency installation
- Template system restructured with shared components

## [2.0.6] - 2026-05-15

### Added

- Search component with SSG build improvements
- Blog route with controller and basic CRUD
- scalar-fastapi integration for API documentation

### Changed

- .gitignore cleaned for better dependency management
- Vite plugin logging refined

## [2.0.5] - 2026-05-10

### Added

- `__pycache__` utility for cache management
- CLI initialization improvements

### Changed

- Core refactor: new parser structure, models, and tests
- Router abstraction: FileBasedRouter → AppModule pattern

## [2.0.2] - 2026-05-01

### Added

- React package and static asset serving paths
- Framework-specific templates with CSS and Vite support
- Font assets (Inter, Geist variable fonts)

### Fixed

- Vue/Svelte static file path resolution
- SSR logging cleanup

### Changed

- Frontend package restructured with framework directories

## [2.0.1] - 2026-04-20

### Added

- VS Code extension with language support for .nexy files
- Frontend framework integration (React, Vue, Svelte, Solid, Preact)
- Template rendering system with markdown support
- Dependency injection and modular routing system

### Changed

- CLI: configurable host/port, improved dev server handling
- Enhanced configuration model with dynamic properties

## [2.0.0b7] - 2026-04-10

### Added

- I18n support with template registry
- Performance benchmarking infrastructure
- Tailwind CSS integration and component mounting
- Custom HMR for Python and Nexy files

### Changed

- Complete rewrite of the project initialization system
- Internal toolchain: Makefile → Astral (ruff, mypy, uv)

## [2.0.0b6] - 2026-04-01

### Added

- Initial release of the Nexy meta-framework
- `nx` CLI with dev, build, start, init commands
- File-based routing system
- Modular routing (NestJS-inspired)
- Vite integration for frontend builds
- Jinja2-based .nexy component system
- VFS (Virtual File System) for runtime compilation
- Project scaffold templates (web-fbr, web-modular, api-fbr, api-modular)

[Unreleased]: https://github.com/NexyPy/nexy/compare/v2.0.9...HEAD
[2.0.9]: https://github.com/NexyPy/nexy/compare/v2.0.8...v2.0.9
[2.0.8]: https://github.com/NexyPy/nexy/compare/v2.0.7...v2.0.8
[2.0.7]: https://github.com/NexyPy/nexy/compare/v2.0.6...v2.0.7
[2.0.6]: https://github.com/NexyPy/nexy/compare/v2.0.5...v2.0.6
[2.0.5]: https://github.com/NexyPy/nexy/compare/v2.0.2...v2.0.5
[2.0.2]: https://github.com/NexyPy/nexy/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/NexyPy/nexy/compare/v2.0.0b7...v2.0.1
[2.0.0b7]: https://github.com/NexyPy/nexy/compare/v2.0.0b6...v2.0.0b7
[2.0.0b6]: https://github.com/NexyPy/nexy/releases/tag/v2.0.0b6
