# Coding agents

A project made with `nx new` carries the rules a coding agent needs to write Nexy code your way:
the order of work, the code and writing rules, and one skill per topic. This page says what you get,
where it goes, and how to keep it current. Working on Nexy itself is a different job: read the
repository's root `AGENTS.md`.

## What `nx new` adds

| File | Read by | Holds |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | the stack of the project, the order of work, the rules, the list of skills |
| `CLAUDE.md` | Claude Code | one line, `@AGENTS.md`, so both read the same text |
| `.agents/skills/` | Codex, OpenCode | the skills |
| `.claude/skills/` | Claude Code, OpenCode | the same skills |

`AGENTS.md` is short and tailored. A client-routed Vue project reads "client-routed, Vue, styled
with Tailwind"; an API project is told there are no views. Only the skills that fit are copied: a
React project gets `nexy-react` and no Vue skill, a server project gets the `.nexy` and Markdown
skills, an API project gets no skill about views.

To skip all of it, create the project with `nx new --no-agents`.

## The skills

| Skill | Covers |
|---|---|
| `nexy-principles` | order of work, code rules, writing rules |
| `nexy-ux-audit` | the experience and information-architecture audit to run before any view |
| `nexy-project` | modes, folders, file conventions, configuration, commands |
| `nexy-file` | `.nexy` pages, props, hooks, islands |
| `nexy-markdown` | `.md` and `.mdx` content |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | idiomatic code for the client framework |
| `nexy-styling` | Tailwind, UnoCSS or plain CSS, and the design tokens |
| `nexy-backend` | API handlers, actions, WebSocket, ISR, middleware |
| `nexy-modular` | controllers, modules, injection and guards of the modular router |
| `nexy-security` | dependencies, input, sessions, authorization, secrets |
| `nexy-testing` | the test-first loop and the gates |
| `nexy-framework-dev` | changing Nexy itself, rather than a project built with Nexy |

The rules they enforce: audit the experience before building a view, write the failing test first,
one function does one treatment, one class carries one intention, one folder holds one set of
related intentions, no emoji, real SVG icons, plain text written for people, and no hand-written
DOM scripts in React, Vue, Svelte, Solid or Preact.

## Add them to an existing project

```bash
nx skills
```

Run it at the root of the project. It reads `nexyconfig.py` and `package.json` to find the stack,
copies the matching skills, and writes `AGENTS.md` and `CLAUDE.md` when they are missing.

It never overwrites a file you wrote: an existing `AGENTS.md` or `CLAUDE.md` is kept, and the
command tells you so. Add the skill list to your own file by hand if you want it there. A skill of
your own in `.claude/skills/` or `.agents/skills/` is left alone; only the `nexy-*` skills are
refreshed.

Run `nx skills` again after you upgrade Nexy to refresh the copies, and commit the result so the
whole team shares it.

## How an agent finds them

- `AGENTS.md` (or `CLAUDE.md`, which imports it) is read at the start of every session. It names
  the skills.
- Each skill starts with a name and a description that say what it covers and when to load it. The
  agent reads those first and opens a skill only when the task matches.

The skills follow the open [Agent Skills format](https://agentskills.io/specification), so other
agents that read `SKILL.md` folders can use them too.

## What they do not do

Skills tell an agent how to work; they do not make its output correct. Keep your own checks:

- Read what the agent changed.
- Run `nx check`, `nx test` and `nx build`. The skills ask for this and for the output to be
  reported, not summarised.
- Audit dependencies the agent adds (`nexy-security` explains how).

The examples in the skills are checked by Nexy's own tests: the imports exist, the configuration
fields exist, the commands exist, the Python parses. That catches drift, not misjudgement.

## Map

An agent answers faster when it knows which page holds the answer.

| You need | Read |
|---|---|
| the product, in one page | [README](../README.md) |
| to run a project | [getting-started](../getting-started/quick-start.md) |
| a file's URL | [routing](../routing/README.md) |
| dynamic segments, layouts, error pages | [pages](../routing/fbr/pages/README.md) |
| the current path, query, cookies, session | [hooks](../routing/fbr/navigation/hooks.md) |
| to edit a page | [.nexy files](../views/nexy/README.md) or [views](../views/README.md) |
| Markdown or MDX | [markdown](../views/nexy/markdown.md) |
| built-in HTML helpers | [components](../views/nexy/components.md) |
| rendering mode | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| a WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| controllers and modules | [modular](../routing/modular/README.md) |
| to add an endpoint | [API](../routing/fbr/handlers/README.md) |
| a form posted from a page | [actions](actions.md) |
| why a request failed, and which page answers it | [exceptions](../reference/exceptions.md) |
| translations | [i18n](i18n.md) |
| a config field | [config](../reference/config.md) |
| to test the app | [testing](testing.md) |
| the client build | [frontend](frontend.md) |

## Project invariants

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

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

When the docs and the code disagree, trust the code and say so: `nexy/core/config.py` holds every
option, `nexy/modules/routers/fbrouter/` the routing rules, `nexy/modules/compiler/` how `.nexy`
files become modules.

## Next steps

- [CLI](../reference/cli.md): `nx new` and `nx skills`
- [File conventions](../reference/file-conventions.md): reserved names and routing rules
- [Glossary](../reference/glossary.md): the words these rules rely on
- [Security](../reference/security.md): the version floors the security skill points to
