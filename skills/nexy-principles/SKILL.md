---
name: nexy-principles
description: The rules for every task in a Nexy project or in Nexy itself - order of work, KISS, SOLID, TDD, one function one treatment, no emoji, real SVG icons, human text, human-centred information architecture. Load it before writing or changing any code.
---

# Principles

## Order of work

1. **Audit the experience first when the change has a view.** A view is a page, a component, a
   form, a message, an error. Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) and write down its
   findings before touching code. No view, no audit.
2. **Write the test that fails** (red). One behaviour, one assertion, named
   `test_<thing>_<scenario>`.
3. **Write the least code that passes** (green).
4. **Refactor** while the tests stay green.
5. **Run the gates** from [nexy-testing](../nexy-testing/SKILL.md). Report failures as they are.

Skipping step 1 or 2 is the most common way to produce code that works and is still wrong.

## Code

**KISS.** The simplest code that works wins. No abstraction for a case that does not exist yet, no
clever one-liner, no option nobody asked for.

**One function, one treatment.** A function does one thing and its name is a verb that says which:
`parse_header`, `render_row`, `save_user`. If the name needs "and", split it. Aim for fewer than 20
lines.

**One class, one intention.** A class exists for one reason you can say in one sentence. A parser
parses, a builder builds, a router routes. Aim for fewer than 10 methods. Depend on a `Protocol`,
not on a concrete class, and pass collaborators in rather than creating them inside.

**One folder, one set of intentions.** A folder gathers files that serve related intentions and is
named after that intention (`billing/`, `routing/`, `theme/`). Never `utils/`, `misc/`, `common2/`.
When a folder mixes two intentions, split it.

**SOLID in practice.** One reason to change per unit. Extend by adding, not by editing a switch.
Small interfaces. Code against abstractions.

**No duplication.** The second copy is a signal; the third is a bug. Extract after the second, not
before.

**Names.** English, complete words, no abbreviations a newcomer would have to guess. A comment says
why, never what.

## Zero emoji

No emoji in code, comments, UI text, terminal output, logs, documentation or commit messages. Status
is carried by words and by colour with a text label, not by a pictograph.

## Icons are real SVG

Every icon is an SVG: an inline component with a `path`, or a file in `public/`. Never an emoji, a
unicode symbol used as a picture (arrows, check marks, crosses), or an icon font loaded for one
glyph. Icons are decorative (`aria-hidden="true"`) or carry an accessible name.

## Text is for humans

- Say what happens, in plain verbs, in sentence case: "Save changes", not "Submit".
- An action keeps one name everywhere: the button "Publish" leads to "Published".
- An error says what went wrong and what to do next. It does not apologise and it is never vague.
- An empty screen invites an action. It does not explain the framework.
- Write for the person using the product, not for the person who built it. "Your app is running",
  not "FastAPI ASGI server bound to 0.0.0.0".
- English by default. User-facing strings of the command line go through the translator.

## Information architecture, centred on people

Organise by what people come to do, not by how the code is organised.

- Group by task and by the words people use. Rename anything they would not say aloud.
- One page, one job. One heading per idea. The most important thing comes first.
- Keep navigation shallow: three levels is a ceiling, not a target.
- URLs, titles, labels and headings agree with each other.
- Every list has an order that means something (importance, time, alphabet), not insertion order.

## Commits

Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`. The message
says why. AI tools never appear as author or co-author: no `Co-authored-by`, no "Generated with"
footer.
