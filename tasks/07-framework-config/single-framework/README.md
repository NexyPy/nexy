# 07 — Framework Config · Single Framework

## Objective

Enforce **exactly one** frontend framework per project, derived from `useFF` in
`nexyconfig.py`. Route extensions must be strictly limited to the active set, and
out-of-set files must be skipped with a warning — never a hard error.

## Rules (user decisions)

- `useFF: FrontendFramework | None` — a single framework, never a list.
- Always-active extensions: `.nexy`, `.md`, `.mdx`, `.py`.
- Active JS extensions added from the chosen framework:
  - `react` → `.tsx`, `.jsx`
  - `vue` → `.vue`
  - `svelte` → `.svelte`
  - `solid` → `.tsx`
  - `preact` → `.tsx`, `.jsx`
- `.vue` files can be authored with `react` OR `nexy` as the render target.
- A project may mix `.tsx` and `.nexy` routes (primary pattern `*.nexy` or `*.tsx`,
  `.mdx` tolerated) — but **never two JS frameworks**.
- Out-of-set file (e.g. `page.vue` with `react` active): project passes, file is
  **not compiled**, a **warning** is printed. No `SystemExit`.

## Nexy current state (violations)

| Anchor | Current behavior | Needed |
|---|---|---|
| `nexy/core/models.py:112` | `useFF: list[FrontendFramework] = []` | `useFF: FrontendFramework \| None = None` |
| `nexy/routers/fbrouter/discovery.py:15-18` | globs all `ROUTE_FILE_EXTENSIONS` | filter against active set |
| `nexy/core/config.py:27` | `ROUTE_FILE_EXTENSIONS = [".nexy",".mdx",".md",".py",".tsx",".vue",".svelte"]` | derive from framework |
| `nexy/core/config.py:134-147` | loops `for ff in ff_list` | single framework mapping |
| `nexyconfig.py:7` | `useFF = [react(), vue()]` | `useFF = react()` |

## Consumers to migrate

- `nexy/cli/commands/add.py:82-84` — reads `useFF[0].name`.
- `nexy/frontend/base.py:12-21` — `_get_ff_list()`.
- `nexy/frontend/__init__.py:68-105` — `ff_list` iteration for `ff.auto.ts`.
- `nexy/templates/_shared/web/nexyconfig.py.jinja2:7` — emits `useFF = [react()]`.

## TDD phases

1. **Red** — test: `useFF = react()`, a `page.vue` exists in `src/routes/` →
   warning emitted, `page.vue` not registered, process continues.
2. **Green** — `config.py`: validate single framework; error if ≥2 configured.
3. **Green** — `discovery.py`: derive active extensions; warn+skip out-of-set files.
4. **Green** — migrate consumers (`add.py`, `base.py`, `frontend/__init__.py`,
   `nexyconfig.py.jinja2`).
5. **Green** — `nexyconfig.py` → `useFF = react()`.
6. **Refactor** — clean `FRAMEWORK_REGISTRY` / `FRONTEND_EXTENSIONS` accordingly.

## Definition of Done

- `nexy build` on a react project containing `page.vue` → **succeeds**, prints warning,
  `page.vue` is not routed/compiled.
- Clean project builds with EXIT=0.
- No remaining `useFF` list usage in `nexy/`.
- `ruff check`, `mypy --strict`, `pytest` all pass.

## References

- [Matrix analysis](../competitive/ANALYSIS.md) — single-framework is the config
  precondition for every other epic.
- Next.js/Nuxt/TanStack all select one view layer per app; no framework allows
  react+vue+svelte simultaneously.