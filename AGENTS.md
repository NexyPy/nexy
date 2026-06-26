# Nexy — Agent Guide

## Vision & Ambition
L'objectif principal de Nexy est de **surpasser les solutions existantes** telles que Django, Next.js, Remix, Reflect et Astro, tant en matière d'expérience développeur (DX) que de performances en production.
- **Sub-second startup** and **Sub-100ms HMR**.
- **Browser error overlay** for compilation failures.
- **Clean terminal output** (no emojis, structured timings).
- **All code in English**: No French comments or variables.

## Philosophy (KISS · TDD · SOLID)

- **KISS**: simplest working code wins. No premature abstraction, no clever one-liners. Functions < 20 lines, classes < 10 methods.
- **TDD**: write the test first (red), minimal code to pass (green), then refactor. One assertion per test. Name: `test_<thing>_<scenario>`.
- **SOLID**: one responsibility per class/file. `TemplateParser` parses, `Builder` builds, `Router` routes. Depend on abstractions (`Protocol`), inject via `nexy/runtime/injection.py`.

## Commands (Astral toolchain — no Makefile)

```bash
# Quality gates (run in this order: lint → format → typecheck → test)
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v

# Auto-fix
ruff check nexy/ --fix
ruff format nexy/

# Single test
python -m pytest tests/unit/nexy/parser/test_scanner.py -v

# Install dev deps
uv pip install -e ".[dev]"
```

## Architecture

| Layer | Dir | Key files |
|-------|-----|-----------|
| CLI | `nexy/cli/` | `__init__.py` (Typer app), `commands/{dev,start,build,init}.py` |
| Router | `nexy/routers/` | `app.py` (AppServer assembly), `fbrouter/` (file-based), `actions/` |
| Compiler | `nexy/compiler/` | `parser/{scanner,sanitizer,template,validator,logic}.py`, `generator/` |
| Frontend | `nexy/frontend/` | `{react,vue,svelte,solid,preact}.py` + `runtime.ts`, `vite.ts` |
| Core | `nexy/core/` | `config.py`, `models.py`, `types.py` |
| Entry | `nexy/app.py` | exports `app: FastAPI` = `AppServer().run()` |
| pkg init | `nexy/__init__.py` | exports `Audio`, `Video`, `Form`, `Import`, `Template`, `Vite` |

## Toolchain

- **Python**: hatchling build, uv for deps, >=3.12 (`.python-version` = 3.13)
- **JS/TS**: pnpm (root + `extensions/vscode/` + `packages/react/`), vite 7, eslint
- **Lint/format**: ruff for both (line-length=100, target-version=py312). No black/isort.
- **Typecheck**: mypy --strict on `nexy/` + `tsc -b` for TS
- **CLI binary**: `nx` or `nexy` → `nexy.cli:CLI`

## Gotchas

- `test_config.py` uses `hasattr` pattern — watch for config API changes.
- Integration tests (`tests/integration/`) may require project scaffolding or a temp workspace.
- `docs/` is a **separate Nexy app** with its own `.git` — do not treat as monorepo child.
- `skills/` dir contains project philosophy docs (KISS, SOLID, TDD, framework-dev).
- `nexyconfig.py` at root is the user-facing config (not `pyproject.toml`).
- `.nexy` files use `---` frontmatter delimiter for Python logic.

## Conventions

- **Branches**: `feature/*`, `fix/*`, `docs/*`, `perf/*`
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`)
- **i18n**: English default; extract strings to `nexy/i18n/en/`
- **Coverage target**: ≥95% per module (CONTRIBUTING.md)

## Session Progress (June 2026)

### Completed — TOC via generated code (no template.py injection)

**`template.py`**: stripped TOC auto-injection (`{toc_html}` placeholder replacement, `TOC_AUTO` fallback). `render()` now returns pure rendered content — no TOC awareness at all.

**`logic.py`**: TOC is fully generated-code concern:
- Layout files get `toc_html: str = ''` auto-appended to their NexyProps (visible to both function params and Jinja2 context)
- `.md` pages with a layout import `_build_toc_html`, extract TOC post-render, and pass `toc_html=toc_html` to `__Layout(children=rendered, toc_html=toc_html)`
- Non-layout `.md` pages still get the `toc_html` variable in scope (can be used directly in template), with empty string default

**`table_of_contents.nexy`**: updated to render `{{ toc_html | safe if toc_html else '' }}`

### Previously completed

**Template rewrites** (counter.tsx.jinja2, card.tsx.jinja2, theme.tsx.jinja2):
- Extracted `Button`/`AddIcon`/`RemoveIcon` sub-components in counter
- Switched Preact from `useSignal` to `useState`/`ComponentChildren`
- Replaced `pointer-events-none` with `border-gray-300` on count span
- Solid/React: `space-y-0.5px`, Preact: `space-y-[0.5px]`
- Simplified card.tsx: removed `CardProps` interface, plain `function Card()`
- Rewrote theme.tsx: `containerRef` + `useRef`/`useLayoutEffect` + separate ThemeButton/SunIcon/MoonIcon/MonitorIcon
- Added `{% raw %}…{% endraw %}` around framework blocks to protect `{{` in JSX

**Vite build pipeline — client-only warnings**:
- `frontend/vite.ts`: `[nexy] Building server components…` (buildStart), `[nexy] Building client bundles…` (closeBundle)
- `scripts/entries.ts`: `⚠ client-only: {file} — {reason}, no server HTML`
- `scripts/utils.ts`: `getProjectFrameworks()` checks for `from 'react'`/`from 'solid-js'`/`from 'preact'` imports
- `scripts/ssg.ts`: warns when `.tsx`/`.jsx` found but no framework installed
- `scripts/ssg.html.ts`: `⚠ client-only: {file} — no server HTML, rendering client placeholder`
- `ssg.{react,preact,solid,vue,svelte}.ts`: SSR failures → warning + empty `<div id="{entryId}-root"></div>`
- `frontend/__init__.py`: logs detected frameworks in `_generate_vite_entry()`

**Bug fixes** (`theme.jinja2` — "none" framework):
- Added `active = 'system'` to frontmatter (was missing → `{{active}}` rendered empty string)
- Changed `--spacing-slider-left`/`--spacing-slider-width` → `--slider-left`/`--slider-width` (was inconsistent with vue/svelte/tsx — all use `--slider-*`)

**SSG unified on per-file esbuild builds — parallèle**:
- `ssg.preact.ts`: revu vers worker pool parallèle avec `os.cpus().length`
- `ssg.react.ts`: supprimé Vite + `@vitejs/plugin-react` → esbuild per-file parallèle
- `ssg.solid.ts`: supprimé Vite + `vite-plugin-solid` → esbuild per-file parallèle
- Workers partagent un compteur atomique `let idx = 0` ; `Math.min(os.cpus().length, files.length)` workers en parallèle
- `Promise.allSettled` implicite via worker pool — chaque fichier buildé indépendamment, un échec ne bloque pas les autres
- Messages d'erreur réels maintenant inclus dans les warnings catch-blocks (React/Solid avaient `"SSR failed"` générique)

### MDX translation & file reorganization (June 10)

**`docs/scripts/translate_mdx.py`**: recreated standalone script (was lost after robocopy cleanup). Parses MDX into segments (frontmatter, fenced code blocks, text), protects inline elements with `%%pN%%` placeholders, batch-translates via `deep_translator.GoogleTranslator.translate_batch()`, restores placeholders, writes locale variant.

**Translation re-run (5 top-level pages)**: `build_and_deploy.mdx`, `create_a_projet.mdx`, `index.mdx`, `projet_structure.mdx`, `router-choice.mdx` → 50 locale variants created (10 locales each). 0 errors, 1 transient connection reset handled gracefully by individual fallback.

**File reorganization**: 55 files (5 base + 50 locale) moved into `(name)/` group dirs. Top-level `src/routes/docs/` now clean (only `__init__.py` + `layout.nexy`). Subdirectory pages (cli, components, config, … ~130 pages) were already properly organized from previous session.

### Blocked → Done
- `vsce package` failed under pnpm (npm dependency resolution in shallow pnpm store), resolved with `--no-dependencies` flag: `npx vsce package --no-dependencies`

### Key findings
- `.nexy` files rendered via standard Jinja2 `Environment` (no sandbox) — `range()` works in `{% for %}`
- Icon SVGs ARE identical across frameworks (same Heroicons path data, only attribute naming differs: `fill-rule`/`fillRule`)
- 28/32 tests pass (4 pre-existing `TemplateFormatter.format_attributes` failures unrelated)
- Ruff errors on `.jinja2` files are expected (mixed HTML/JS/Python, not valid Python)
- No Vite dependency in production SSG pipeline — esbuild seul pour React, Preact, Solid SSR builds
- Pylance delegation requires **real `.py` on disk** (`.nexy-virt/`) — Pylance ignores non-`file://` schemes for imports
- CSS/JS/HTML delegation works with custom virtual scheme URIs (`nexy-embed-*://`) — only color provider needs untitled docs
- vsce packaging needs `--no-dependencies` when running under pnpm's strict node_modules layout
