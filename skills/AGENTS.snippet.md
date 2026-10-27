# Working in a Nexy project

Read `skills/nexy-principles/SKILL.md` before any task. Load the other skills in `skills/` when their
topic comes up (see `skills/README.md`).

## Order of work

1. If the change has a view, audit the experience first (`skills/nexy-ux-audit/SKILL.md`): who uses
   it, what they came to do, how the information is organised for them.
2. Write the test that fails.
3. Write the least code that passes.
4. Refactor, then run `nx check` and `nx test`.

## Code

- KISS. One function does one treatment. One class carries one intention. One folder holds one set
  of related intentions.
- No emoji anywhere: code, text, logs, commit messages.
- Icons are real SVG, never emoji or symbol characters.
- Text is written for people: plain verbs, sentence case, errors say what happened and what to do.
- Match the style mode of the project (Tailwind, UnoCSS or plain CSS) and the idioms of its
  framework. No hand-written DOM scripts in React, Vue, Svelte, Solid or Preact code.
- `__nexy__/` is generated: never edit it, never commit it.
