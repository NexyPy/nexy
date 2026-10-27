---
name: nexy-preact
description: Writing Preact 10 routes, layouts and components in a Nexy project in idiomatic Preact - hooks, state and signals, never hand-written DOM scripts. Load it for any .tsx file when useFF = preact().
---

# Preact in Nexy

## Idiomatic Preact only

Use hooks from `preact/hooks` (`useState`, `useEffect`, `useRef`, `useMemo`) or `@preact/signals`
when the project already uses them. Do not mix hand-written DOM code into components: no
`document.querySelector`, no document-level listeners, no `innerHTML`.

The one allowed script is a short `<ThemeScript />` that sets the saved theme class on `<html>`
before the first paint.

## Files

- `src/routes/*.tsx`: pages. Default export is the component.
- `src/routes/layout.tsx`: the root one owns the document and receives the page as `children`.
- `src/components/*.tsx`: components, never inside `src/routes/`.

```tsx
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>My app</title>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Differences from React that matter

- Attributes are `class` and `charset`, not `className` and `charSet`.
- Types: `ComponentChildren` for children, `JSX.Element` for a single element.
- Preact cannot hydrate a whole document: the browser renders the page body and swaps it in.
  Do not rely on the server `<html>` being hydrated; keep `<html>` and `<head>` static.
- `.mdx` files import from `preact` to be compiled with Preact.

## Rules

- Typed props, default exports, one component per file named like the file.
- Stable `key`s on lists. Real `button` and `a` elements.
- Import with `@/`. Navigate with `Link` from `@nexy/client`. Server calls go through `useAction`
  from `@nexy/client`.
- Icons are SVG components. No emoji.

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) before building a view, follow
[nexy-styling](../nexy-styling/SKILL.md), and write the test first
([nexy-testing](../nexy-testing/SKILL.md)).
