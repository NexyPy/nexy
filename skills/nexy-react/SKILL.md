---
name: nexy-react
description: Writing React 19 routes, layouts and components in a Nexy project in idiomatic React - hooks and state, never hand-written DOM scripts. Load it for any .tsx file when useFF = react().
---

# React in Nexy

## Idiomatic React only

Write React the way React is written. State lives in `useState` and `useReducer`, effects in
`useEffect`, derived values in plain expressions or `useMemo`, shared logic in custom hooks.

**Never** in a React file: `document.querySelector`, `addEventListener` on the document, inline
`<script>` that wires clicks, `innerHTML`, `data-*` attributes used as hooks for a script. If you
reach for the DOM, you need state, a ref or an effect instead.

The one allowed script is a short `<ThemeScript />` that sets a class on `<html>` before the first
paint, so a saved theme never flashes. Everything after that is a hook.

```tsx
function useTheme() {
  const [dark, setDark] = useState(false);
  useEffect(() => setDark(document.documentElement.classList.contains("dark")), []);

  function toggle() {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    setDark(next);
  }
  return { dark, toggle };
}
```

## Files

- `src/routes/index.tsx`: a page. Default export is the component.
- `src/routes/layout.tsx`: in client mode the root one owns the document.
- `src/components/*.tsx`: components. **Never** inside `src/routes/`.

```tsx
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>My app</title>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

`suppressHydrationWarning` on `<html>` is needed when a script changes it before hydration.

## Rules

- Function components, typed props (`type Props = {...}`), default exports for routes and
  components.
- One component per file, named like the file. Small components: if the JSX is long, extract.
- Lists get stable `key`s. Never an index for a list that reorders.
- Import with the `@/` alias: `import Button from "@/components/button.tsx"`.
- Navigate with `Link` from `@nexy/client`; keep `<a>` for external URLs.
- Call the server with `useAction` from `@nexy/client` and the typed functions in `@nexy/actions`.
- Pass the server's idea of state through props or actions, not through globals.
- Interactive controls are `button`s and `a`s with real labels, not clickable `div`s.
- Icons are SVG components (a `path` prop), `aria-hidden="true"` when decorative. No emoji.

## Before building the view

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md). Style with the project's mode
([nexy-styling](../nexy-styling/SKILL.md)). Test per [nexy-testing](../nexy-testing/SKILL.md).
