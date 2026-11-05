# Frontend Layouts

A **Layout** is a wrapper that defines the shared structure around one or more pages. Layouts enable the "app-like" experience by preserving state and avoiding full-page reloads during navigation.

## Nesting Logic

Layouts follow a hierarchical structure based on the directory tree under `src/routes/`.

1.  **Root Layout**: Every project has a root layout (e.g., `src/routes/layout.nexy`). This is the only layout responsible for defining the document shell: `<html>`, `<head>`, and `<body>`.
2.  **Nested Layouts**: Any folder can contain its own `layout.*` file. This layout wraps all pages and sub-layouts within that folder.
3.  **Inheritance**: A page is wrapped by all layouts from the root down to its own folder.

## Shared State & Composition

Layouts are designed to be stable. When navigating between two pages that share the same layout, the layout is **not** re-rendered; only the child content changes.

- **Slots**: Layouts provide a "slot" (usually `children` in JSX or `{{ content }}` in Jinja2) where the nested page is injected.
- **State Preservation**: Because the layout stays mounted, any state held within it (e.g., a search query in a header) is preserved during navigation.

## Static Constraints

For routes that are pre-rendered (SSG), the root layout cannot depend on request-time data such as cookies or headers. It must be representable as a static shell that the client then hydrates.

## Framework Implementation

The implementation of slots and nesting varies slightly by framework. See the **Differences** guide for your chosen technology:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
