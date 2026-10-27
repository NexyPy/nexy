---
name: nexy-framework-dev
description: Rules for changing Nexy itself (the nexy/ package, its templates, scripts and docs) rather than a project built with it - architecture, quality gates, structure limits, attribution and documentation upkeep. Load it when the working directory is the Nexy repository.
---

# Working on Nexy

Start with `nexy-principles`. This skill adds what is specific to the
repository.

## Architecture

| Layer | Directory |
|---|---|
| CLI | `nexy/modules/cli/` |
| Router | `nexy/modules/routers/` |
| Compiler | `nexy/modules/compiler/` |
| Frontend (Vite, SSG) | `nexy/modules/frontend/` |
| Core (config, models) | `nexy/core/` |
| Transversal helpers | `nexy/helpers/` (no upward imports) |

**The compiler does not compile what Vite compiles.** `.tsx`, `.vue`, `.svelte` and `.mdx` get a thin
Python wrapper; Vite and the SSG scripts do the real work. Python renders `.nexy` and `.md` only.

## Gates

Run in this order. Each must pass before you say a change is done.

```bash
ruff check nexy/
ruff format nexy/ --check
python -m mypy nexy --strict
python -m pytest tests/ -v
python scripts/audit_structure.py --check
```

`python scripts/verify.py` runs the same gates and stops at the first failure.
`python scripts/audit_dependencies.py` audits the dependencies against the lock.

## Structure limits

Functions under 20 lines, classes under 10 methods, no copied code. `audit_structure.py --check`
fails on a new or worse offender; `--write` records a new baseline only after a real refactor.

## Tests

TDD: the failing test comes first. Unit tests live in `tests/unit/nexy/<area>/`. A change to a
user-visible message needs its translation in every catalog under `nexy/modules/i18n/`, and the
English default in the code must equal the English catalog.

## Templates and examples

The project starters are Jinja2 files under `nexy/modules/cli/templates/`. A change to the look of
the starter is tried in an example project first, then ported to every template
(React, Preact, Solid, Vue, Svelte, `.nexy`) and checked by `tests/unit/nexy/cli/`.

## Documentation

`docs/` is plain Markdown: one question per page, entry point `docs/README.md`, machine entry
point `llms.txt`. Do not add a docs site generator. When behaviour changes, update the page and
`CHANGELOG.md` in the same change. If the docs and the code disagree, the code is right: fix the
docs.

## Commits

Conventional Commits. AI tools never appear as author or co-author; `scripts/check_attribution.py`
enforces it through `.githooks/commit-msg` (enable with `git config core.hooksPath .githooks`).
Branches are `feature/*`, `fix/*`, `docs/*`, `perf/*`.
