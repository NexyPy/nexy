# Skills for coding agents

Rules that make an agent write Nexy code the way the project wants it: clean, tested, and designed
for the person who will use it. They work with Claude Code, OpenCode, Codex and any agent that reads
`SKILL.md` folders or an `AGENTS.md` file.

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
| [nexy-testing](nexy-testing/SKILL.md) | writing the test first, running the gates |
| [nexy-framework-dev](nexy-framework-dev/SKILL.md) | changing Nexy itself, not a project built with it |

## Use them

**Claude Code.** Copy the folders you need into `.claude/skills/` of the project, or into
`~/.claude/skills/` for every project. Each folder holds one `SKILL.md`; Claude loads it when its
`description` matches the task.

**OpenCode and Codex.** Both read `AGENTS.md` at the project root. Paste [AGENTS.snippet.md](AGENTS.snippet.md)
into it: it states the rules that apply to every task and links the skills for the rest. Agents
that also read `SKILL.md` folders can load them as they are.

## Keep them true

A skill states what the code does today. When the code and a skill disagree, the code wins: fix the
skill in the same change. Examples, names and commands must run as written.
