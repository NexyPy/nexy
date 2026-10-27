# For AI agents

Rules and entry points for an agent working in a project built with Nexy. Working on Nexy itself is
a different job: read the repository's root `AGENTS.md`.

## Map

| You need | Read |
|---|---|
| the product, in one page | [README](../README.md) |
| to run a project | [getting-started](../getting-started/quick-start.md) |
| a file's URL | [routing](../routing/README.md) |
| dynamic segments, layouts, error pages | [pages](../routing/fbr/pages/README.md) |
| the current path, query, cookies, session | [hooks](../routing/fbr/navigation/hooks.md) |
| to edit a page | [.nexy files](../views/nexyfile.md) or [views](../views/README.md) |
| Markdown or MDX | [markdown](../views/markdown.md) |
| built-in HTML helpers | [components](../views/components.md) |
| rendering mode | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| a WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| controllers and modules | [modular](../routing/modular/README.md) |
| to add an endpoint | [API](../routing/fbr/handlers/README.md) |
| a form posted from a page | [actions](../guides/actions.md) |
| translations | [i18n](../guides/i18n.md) |
| a config field | [config](config.md) |
| to test the app | [testing](../guides/testing.md) |
| the client build | [frontend](../guides/frontend.md) |

## Skills

A project made with `nx new` already holds the rules for agents: `AGENTS.md`, `CLAUDE.md` and the
skills in `.agents/skills/` and `.claude/skills/`. Read `AGENTS.md` first; it lists the skills and
says which one to load for a task. For an existing project, run `nx skills`. See
[Coding agents](../guides/ai-agents.md).

## Invariants

1. `__nexy__/` is generated. Never edit it, never commit it. Delete it to force a clean build.
2. One file per URL. `index.nexy` and `index.py` for the same path is a bug, not a priority rule.
3. Reserved names inside `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`,
   `notfound.nexy`, `dependencies.py`, `__init__.py`. Do not use them for content.
4. `.nexy` frontmatter is Python that runs per request. No module-level side effects: no file
   handles, no database connections, no network calls at import.
5. `.py` in `src/routes/` is an API handler. Methods are function names (`GET`, `POST`, ...).
6. Configuration lives in `nexyconfig.py`, not in environment variables and not in scattered
   constants.
7. Autoescaping is off in `.nexy` templates: escape untrusted values with `| e`.

## Commands

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

## How to answer a question about Nexy

1. Search `docs/` for the concept.
2. If the page is silent, read the installed package - `nexy/core/config.py` for options,
   `nexy/modules/routers/fbrouter/` for routing rules, `nexy/modules/compiler/` for how `.nexy`
   files become modules.
3. If the docs and the code disagree, trust the code and say so.
