---
name: nexy-solid
description: Writing Solid 1.9 routes, layouts and components in a Nexy project in idiomatic Solid - signals, memos and effects, props never destructured. Load it for any .tsx file when useFF = solid().
---

# Solid in Nexy

## Idiomatic Solid only

A Solid component runs **once**. Reactivity comes from signals, not from re-running the body.

- State: `createSignal`. Derived values: `createMemo` or a function. Side effects: `createEffect`,
  `onMount`, `onCleanup`.
- **Never destructure props**: `props.title`, not `({ title })`. Destructuring breaks reactivity.
- Read a signal by calling it (`count()`), inside JSX or an effect, not once in the body.
- Control flow with `<Show>`, `<For>`, `<Switch>`, not `&&` and `.map` for dynamic lists.
- No hand-written DOM code: no `document.querySelector`, no document-level listeners, no
  `innerHTML` (use `ref` and an effect when the DOM is truly needed).

The one allowed script is a short `<ThemeScript />` that sets the saved theme class on `<html>`
before the first paint.

```tsx
import { createSignal } from "solid-js";

export default function Counter() {
  const [count, setCount] = createSignal(0);
  return <button onClick={() => setCount(count() + 1)}>Clicked {count()} times</button>;
}
```

## Files

- `src/routes/*.tsx`: pages. `src/components/*.tsx`: components, never inside `src/routes/`.
- `src/routes/layout.tsx`: the root one owns the document. Use `props.children`, and `class`.

```tsx
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>My app</title>
      </head>
      <body>{props.children}</body>
    </html>
  );
}
```

## Notes

- Attributes are `class` and `charset`. Raw HTML uses `innerHTML={...}` on the element.
- Solid hydrates the server document and needs the Node renderer; keep `solid({ ssr: true })` in
  `vite.config.ts` in client mode.
- `useAction` returns accessors: `pending()`, `data()`, `error()`.
- Import with `@/`. Navigate with `Link` from `@nexy/client`.
- Icons are SVG components. No emoji.

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) before building a view, follow
[nexy-styling](../nexy-styling/SKILL.md), and test first ([nexy-testing](../nexy-testing/SKILL.md)).
