# Frontend Layouts

A **Layout** is a wrapper that defines the shared structure around one or more pages. Layouts enable the "app-like" experience by preserving state and avoiding full-page reloads during navigation.

## Nesting Logic

Layouts follow a hierarchical structure based on the directory tree under `src/routes/`.

1.  **Root Layout**: Every project has a root layout (e.g., `src/routes/layout.nexy`). This is the only layout responsible for defining the document shell: `<html>`, `<head>`, and `<body>`.
2.  **Nested Layouts**: Any folder can contain its own `layout.*` file. This layout wraps all pages and sub-layouts within that folder.
3.  **Inheritance**: A page is wrapped by all layouts from the root down to its own folder.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

A nested layout draws only its part of the UI and puts the page where `children` goes:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Shared State & Composition

Layouts are designed to be stable. In client mode, when navigating between two pages that share
the same layout, the layout is **not** re-rendered; only the child content changes. In server mode
every navigation is a new document.

- **Slots**: Layouts provide a slot where the nested page is injected: `children` in JSX, and the
  `children` prop in a `.nexy` layout.
- **State Preservation**: Because the layout stays mounted, any state held within it (e.g., a search query in a header) is preserved during navigation.

The same slot in a `.nexy` layout:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

The search field below keeps what the user typed while they move between the dashboard pages,
because the layout that holds it never unmounts:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Static Constraints

For routes that are pre-rendered (SSG), the root layout cannot depend on request-time data such as
cookies or headers. It must be representable as a static shell that the client then hydrates.

Read the theme from the browser instead, in a script of the static shell:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Framework Implementation

The implementation of slots and nesting varies slightly by framework. See the **Differences** guide for your chosen technology:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
