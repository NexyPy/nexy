# Skills for coding agents

Rules that make an agent write Nexy code the way the project wants it: clean, tested, secure, and
designed for the person who will use it. They follow the open [Agent Skills](https://agentskills.io/specification)
format, so Claude Code, Codex, OpenCode and the other agents that read `SKILL.md` folders load them
as they are.

## The skills

| Skill | Load it when |
|---|---|
| [nexy-principles](nexy-principles/SKILL.md) | always: order of work, code rules, writing rules |
| [nexy-ux-audit](nexy-ux-audit/SKILL.md) | the change has a view: a page, a component, a form, a message |
| [nexy-project](nexy-project/SKILL.md) | creating or moving files, choosing server or client mode |
| [nexy-file](nexy-file/SKILL.md) | writing a `.nexy` page, layout or component |
| [nexy-markdown](nexy-markdown/SKILL.md) | writing `.md` or `.mdx` content |
| [nexy-react](nexy-react/SKILL.md) | writing `.tsx` with React |
| [nexy-preact](nexy-preact/SKILL.md) | writing `.tsx` with Preact |
| [nexy-solid](nexy-solid/SKILL.md) | writing `.tsx` with Solid |
| [nexy-vue](nexy-vue/SKILL.md) | writing `.vue` |
| [nexy-svelte](nexy-svelte/SKILL.md) | writing `.svelte` |
| [nexy-styling](nexy-styling/SKILL.md) | styling: Tailwind, UnoCSS or plain CSS |
| [nexy-backend](nexy-backend/SKILL.md) | API handlers, actions, WebSocket, ISR, middleware |
| [nexy-security](nexy-security/SKILL.md) | adding a dependency, handling input, sessions, authorization |
| [nexy-testing](nexy-testing/SKILL.md) | writing the test first, running the gates |
| [nexy-framework-dev](nexy-framework-dev/SKILL.md) | changing Nexy itself, not a project built with it |

## Get them in a project

A project made with `nx new` already has them. Nexy writes:

| File | For |
|---|---|
| `AGENTS.md` | the stack of the project, the order of work, the rules, and the list of skills; read by Codex and OpenCode |
| `CLAUDE.md` | one line, `@AGENTS.md`, so Claude Code reads the same file |
| `.agents/skills/` | the skills for Codex and OpenCode |
| `.claude/skills/` | the skills for Claude Code and OpenCode |

Only the skills that fit the project are copied: a client-routed Vue project gets `nexy-vue` and no
`.nexy` skill; an API project gets no view skill. `nx new --no-agents` skips all of it.

For an existing project, run `nx skills` at its root. It adds or refreshes the skills, writes
`AGENTS.md` and `CLAUDE.md` when they are missing, and **never overwrites** a file you wrote or a
skill of your own. Run it again after upgrading Nexy to refresh the copies. Commit the files so the
whole team, and its agents, share them.

By hand: copy the folders you need into `.claude/skills/` or `.agents/skills/`, and paste
[AGENTS.snippet.md](AGENTS.snippet.md) into your `AGENTS.md`.

## How an agent finds them

- **Always loaded:** `AGENTS.md` (`CLAUDE.md` for Claude Code). It is short on purpose and names the
  skills.
- **Loaded when relevant:** every skill starts with a `name` and a `description` that say what it
  covers and when to load it. The agent reads those at start-up and opens the whole skill only for
  a matching task.

## Keep them true

A skill states what the code does today. When the code and a skill disagree, the code wins: fix
the skill in the same change. `tests/unit/nexy/skills/` checks the format of every skill, that its
Python examples parse, and that the imports, configuration fields, commands and paths it names
exist.
