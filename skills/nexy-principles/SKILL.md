---
name: nexy-principles
description: The rules for every task in a Nexy project or in Nexy itself - order of work, KISS, SOLID, TDD, one function one treatment, no emoji, real SVG icons, human text, human-centred information architecture. Load it before writing or changing any code.
---

# Principles

## Order of work

1. **Audit the experience first when the change has a view.** A view is a page, a component, a
   form, a message, an error. Run `nexy-ux-audit` and write down its
   findings before touching code. No view, no audit.
2. **Write the test that fails** (red). One behaviour, one assertion, named
   `test_<thing>_<scenario>`.
3. **Write the least code that passes** (green).
4. **Refactor** while the tests stay green.
5. **Run the gates** from `nexy-testing`. Report failures as they are.

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

## Characters a person does not type

A keyboard has a hyphen, straight quotes and three dots. A language model reaches for characters
people rarely type, and readers have learned to spot them. Pangram measured some of them hundreds
of times more often in model text than in human text (box drawing about 940 times, the almost-equal
sign 241 times, the warning sign 57, the right arrow 48), and the em dash shows up about 17 times per
10,000 words of model text against 2 for people. None of them is proof on its own, but together
they make a page read as generated. So none of them is written, by an agent or a person, in code,
comments, UI text, terminal output, logs, documentation, commit messages, pull requests, issues, or
in a reply to the user.

| Do not write (code point) | Name | Write instead |
| --- | --- | --- |
| U+2014 | em dash | a comma, a colon, parentheses, or two sentences |
| U+2013 | en dash | a hyphen, or "to" for a range: `1-5`, "Monday to Friday" |
| U+2192, U+2190, U+21D2 | arrows | "to", "then", "becomes"; in a UI, an SVG icon |
| U+2026 | ellipsis character | three dots `...`, or finish the sentence |
| U+201C, U+201D, U+2018, U+2019 | curly quotes | straight quotes `"` and `'` |
| U+2022, U+00B7 | bullet, middle dot | a Markdown list; in a UI, a gap or a border in CSS |
| U+2248, U+00D7 | almost equal, times | "about", "x" or "by": `1080x1350` |
| U+2713, U+2714, U+2717, U+26A0, U+2605 | check marks, ballot x, warning sign, star | a word ("ok", "warning"), or an SVG icon |
| U+2500, U+2502, U+251C, U+2514 | box drawing | plain text, or a list of paths |
| U+00A0, U+200B, U+200C, U+200D, U+FEFF | no-break and zero-width spaces | a normal space, or nothing |

**The design follows the same rule.** A separator in a menu, a breadcrumb or a footer is a CSS
border or a `gap`, never a dash, an arrow or a middle dot in the markup, nor in `content:` of a
pseudo-element. This holds for the mobile menu and drawer as much as for the desktop: an "open"
or "back" arrow, a close cross and a check mark are SVG icons with an accessible name.

**Two exceptions only.**

- A code block that reproduces real output keeps it as it is: the output of `tree`, a log line
  copied from a tool.
- A translated page follows the typography of its language: the dash of Russian (`Файл — это`),
  the quotes of French (`« »`), German (`„ “`) or Chinese (`“ ”`). The English source still uses
  none of these.

`tests/unit/sites/test_human_characters.py` keeps them out of the interfaces of both docs sites
and of the starters.

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
- Write so search finds the page: the title and the headings are the words a person types, the first
  sentence answers them, the slug repeats them. One page per question.

## Commits

Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`. The message
says why. AI tools never appear as author or co-author: no `Co-authored-by`, no "Generated with"
footer.

**One commit, one unit: a function, a logic, or a structure, never two at once.**

- *A function*: the function, its test, and its doc line.
- *A logic*: one behaviour or bug fix, with the test that proves it.
- *A structure*: one move, rename or split that changes no behaviour.

A refactor and a feature never share a commit: a reviewer must be able to read one intention per
commit, and revert it alone. If a change needs two of them, make two commits.
