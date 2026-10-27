# Coding agents

A project made with `nx new` carries the rules a coding agent needs to write Nexy code your way:
the order of work, the code and writing rules, and one skill per topic. This page says what you get,
where it goes, and how to keep it current.

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
| `nexy-security` | dependencies, input, sessions, authorization, secrets |
| `nexy-testing` | the test-first loop and the gates |

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

## Next steps

- [For AI agents](../reference/agents.md): invariants of a Nexy project
- [CLI](../reference/cli.md): `nx new` and `nx skills`
- [Security](../reference/security.md): the version floors the security skill points to
