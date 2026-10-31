# Svelte layouts

A `layout.svelte` wraps every page below it, in client mode (`useCSR = True`). The root `layout.svelte` defines the
whole document; a `layout.svelte` in a subdirectory wraps the pages below it, renders them with the
`children` snippet and keeps its state while the user navigates.

## Root layout

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";

  let { children }: { children?: Snippet } = $props();
</script>

<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <title>My app</title>
  </head>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

`nx new` with Svelte and `useCSR = True` creates this file. `<!DOCTYPE html>` is added for you.

## Nested layouts

```svelte filename="src/routes/dashboard/layout.svelte"
<script lang="ts">
  let { children } = $props();
</script>

<section>
  <aside>Sidebar</aside>
  {@render children?.()}
</section>
```

`dashboard/index.svelte` renders as `root layout > dashboard layout > page`. Each layout also
receives the route's props as `params`.

## How the document is produced

| Moment | What happens |
|---|---|
| `nx dev` | each request asks the Vite dev server to render the layouts and the page in Node. |
| `nx build` | every static route is rendered to a complete document; a dynamic route is rendered without its page. |
| `nx start` | Python serves the pre-rendered file and adds the client assets. No Node process runs. |
| Browser | Svelte builds the body and swaps it in; `<html>` and `<head>` stay as sent. See [how the browser takes over](../../routing/fbr/layouts/README.md#how-the-browser-takes-over-the-document). |

For the browser, Nexy removes `<html>`, `<head>` and `<body>` from the root layout before Svelte
compiles it: Svelte cannot create those elements in the browser (and cannot hydrate them), and the
server already sent them. Keep `{ ... }` expressions out of a `<script>` written inside `<head>`.

Svelte renders the page inside an extra `<div style="display: contents">`, which does not affect
layout or CSS.

## Navigation

A click on a `Link` replaces the page inside the layout and leaves the layouts mounted. The layouts
that differ between two pages are rebuilt.

## Rules

- Only the **root** layout writes `<html>`, `<head>` and `<body>`.
- `layout.svelte` wraps `.svelte` pages only.
- It cannot coexist with `layout.nexy`.
- It needs Svelte 5 (`$props` and snippets).
- Pages under a layout are mounted in the browser: they have no server-rendered snapshot.

## Next steps

- [Islands](islands.md): Svelte inside a server-mode page, with `layout.nexy`
- [Actions and navigation](actions-and-navigation.md): the `Link` that keeps layouts mounted
- [Layouts](../../routing/fbr/layouts/README.md): how Nexy resolves a chain of layouts
