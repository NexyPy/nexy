---
name: nexy-ux-audit
description: The UX and information-architecture audit to run before building or changing any page, component, form or message in a Nexy project. Produces a short written brief. Load it whenever the change has a view.
---

# UX and information-architecture audit

Run this before code. It takes minutes and prevents rebuilding. Write the answers down, in the
conversation or in the pull request, in plain language.

## 1. Frame

Answer in one sentence each.

- **Who** arrives here, and in what state (new, hurried, returning, on a phone)?
- **What job** do they come to do? Phrase it as their goal, not as a feature.
- **What would make them leave** without doing it?
- **What is the one thing** this view must make easy?

If you cannot answer, stop and ask. A view without a job is decoration.

## 2. Information architecture

- List what the person needs to see, then **order it by importance to them**.
- **Name things with their words.** Replace internal terms (handler, route, island, slot) with what
  the person would say.
- **Group by task**, not by data type or by file.
- **One page, one job.** If a page has two jobs, it is two pages or one job is secondary.
- **Depth.** Can they reach the goal in three steps or fewer from where they land?
- **Wayfinding.** The title, the heading, the navigation label and the URL agree.
- **Content budget.** Cut every block that does not serve the job. The page that remains should feel
  inevitable.

## 3. States

Design all of them, not only the happy one.

| State | Ask |
|---|---|
| First visit, empty | What is the one action to take? |
| Loading | Is there something useful to show before the data arrives? |
| Error | Does it say what happened and what to do next? |
| Success | Does it confirm in the words of the action? |
| Offline or slow | What still works? |
| Long or odd content | Names that wrap, 200 items, none |

## 4. Interaction

- Primary action is visible, singular and labelled with a verb that says what happens.
- Destructive actions are reversible or confirmed, and look different from safe ones.
- Feedback within 100 ms: a pressed state, a spinner, a disabled button.
- Keyboard: every action is reachable in a sensible order, focus is visible, and nothing traps it.
- Touch targets are at least 44 px on a phone.

## 5. Quality floor

- Contrast meets WCAG AA (4.5:1 text, 3:1 large text and icons).
- Semantic HTML first: `button` for actions, `a` for navigation, labels on every field, one `h1`.
- Works without a mouse and at 320 px wide. Motion respects `prefers-reduced-motion`.
- Icons are SVG, text is human, there is no emoji (see [nexy-principles](../nexy-principles/SKILL.md)).

## 6. Output

Finish with a brief of five lines or fewer:

```text
Who:        <one line>
Job:        <one line>
Structure:  <the order of what is on the page and why>
States:     <the ones that need design>
Cut:        <what was left out on purpose>
```

Then continue with the test (see [nexy-testing](../nexy-testing/SKILL.md)). Return to this brief when
a choice is unclear: the answer is whatever serves the job.
